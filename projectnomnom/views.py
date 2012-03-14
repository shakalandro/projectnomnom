import urlparse
import base64
import operator
import logging
import StringIO
import datetime
import pyx
from projectnomnom import models, recipe_form, settings
from projectnomnom.util import recipe_util
from PIL import Image
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.utils import datastructures
from django.utils.copycompat import deepcopy
from django import shortcuts



def GetIndexData(user):
        recipes = recipe_util.getValidRecipes(user)
        # Map each recipe to a 4-tuple
        data = set(map(lambda x: (x['fields']['category'], x['fields']['subcategory'],
                                  x['fields']['name'], x['pk']), recipes))
        # sort the list by category and sub-sort by subcategory
        data = sorted(data, key=operator.itemgetter(0, 1))
        result = datastructures.SortedDict()
        for category, subcategory, name, recipe_id in data:
            if category not in result:
                result[category] = datastructures.SortedDict()
            if subcategory not in result[category]:
                result[category][subcategory] = []
            if len(name) > 23:
                name = name[:20].strip() + '...'
            result[category][subcategory].append((name, recipe_id))
        return result


def getModelInstance(recipe, request):
    recipe = deepcopy(recipe)
    del recipe.cleaned_data['ingredients']
    del recipe.cleaned_data['directions']
    del recipe.cleaned_data['image']         
    parts = recipe.cleaned_data['category'].split('-')
    recipe.cleaned_data['category'] = parts[0]
    recipe.cleaned_data['subcategory'] = parts[1]
    recipe.cleaned_data['owner'] = request.user.uid
    return models.Recipe(**recipe.cleaned_data)    


def saveDirsAndIngrs(data, recipe_obj):
    """
    Params:
        data: cleaned data from a bound recipe form object
        recipe_obj: a recipe model instance corresponding to recipe that has been saved
    """
    recipe_ingrs = models.RecipeIngredient.objects.filter(recipe=recipe_obj)
    ingrs = models.Ingredient.objects.filter(id__in=recipe_ingrs)
    dirs = models.Directions.objects.filter(recipe=recipe_obj)
    recipe_ingrs.delete()
    ingrs.delete()
    dirs.delete()
    
    if data.get('image', None):
        models.RecipeImage(recipe=recipe_obj, image=data['image']).save()
    
    ingrs = data['ingredients']
    dirs = data['directions']
    # Build ingrs entries
    for i in range(int(ingrs['ingredients-TOTAL_FORMS'])):
        ingr = models.Ingredient(item=ingrs['ingredients-%d-item' % i],
                                 amount=ingrs['ingredients-%d-amount' % i],
                                 prep=ingrs['ingredients-%d-prep' % i],
                                 garnish='ingredients-%d-garnish' % i in ingrs)
        ingr.save()
        models.RecipeIngredient(recipe=recipe_obj, ingredient=ingr).save()
        
        #if 'ingredients-%d-subtitute' % i in ingrs and ingrs['ingredients-%d-subtitute' % i]:
        #    sub = ingr = models.Ingredient(item=ingrs['ingredients-%d-item' % i],
        #                                   amount=ingrs['ingredients-%d-amount' % i],
        #                                   prep=ingrs['ingredients-%d-prep' % i],
        #                                   garnish='ingredients-%d-garnish' % i in ingrs)
    
    # Build directions entries
    for i in range(int(dirs['directions-TOTAL_FORMS'])):
        dir = models.Directions(recipe=recipe_obj,
                                step_number=i,
                                direction=dirs['directions-%d-direction' % i])
        dir.save()


# Start Handlers

def add_recipe(request):
    if request.method == 'GET':
        recipe_form_inst = recipe_form.RecipeForm()
        return shortcuts.render(request, 'addrecipe.html.tmpl',
                                {'form': recipe_form_inst,
                                 'index_data': GetIndexData(request.user.uid),
                                 'fb_code': request.REQUEST.get('code', None),
                                 'page_name': 'add_recipe'})
    elif request.method == 'POST':
        recipe = recipe_form.RecipeForm(request.POST)
        if recipe.is_valid():
            if request.FILES.get('image', None):
                recipe.cleaned_data['image'] = base64.b64encode(request.FILES['image'].read())
            recipe_obj = getModelInstance(recipe, request)
            recipe_obj.save()
            saveDirsAndIngrs(recipe.cleaned_data, recipe_obj)
            return HttpResponseRedirect('/viewrecipe/%d' % recipe_obj.id)
        else:
            return shortcuts.render(request, 'addrecipe.html.tmpl',
                                    {'form': recipe,
                                     'index_data': GetIndexData(request.user.uid),
                                     'fb_code': request.REQUEST.get('code', None),
                                     'page_name': 'add_recipe'})
def edit_recipe(request, recipe_id):
    recipe = models.Recipe.objects.get(id=recipe_id)
    if recipe.owner != request.user.uid and str(request.user.uid) not in settings.FACEBOOK['APP_ADMINS']:
        return HttpResponseForbidden()
    
    if request.method == 'GET':
        recipe_dict = recipe_util.JoinRecipes([recipe])[0]['fields']
        # fix ingredients
        for idx, ingr in enumerate(recipe_dict['ingredients']):
            for key, value in ingr.items():
                recipe_dict['ingredients-%d-%s' % (idx, key)] = value
        del recipe_dict['ingredients']
        # fix directions
        for idx, dir in enumerate(sorted(recipe_dict['directions'], key=lambda x: x['step_number'])):
            for key, value in dir.items():
                recipe_dict['directions-%d-%s' % (idx, key)] = value
        del recipe_dict['directions']
        recipe_dict['category'] += '-' + recipe_dict['subcategory']
        del recipe_dict['subcategory']
        recipe_form_data = recipe_form.RecipeForm(recipe_dict)
        return shortcuts.render(request, 'editrecipe.html.tmpl',
                                {'form': recipe_form_data,
                                 'index_data': GetIndexData(request.user.uid),
                                 'recipe_id': recipe.id,
                                 'fb_code': request.REQUEST.get('code', None),
                                 'page_name': 'edit_recipe'})
    else:
        recipe = recipe_form.RecipeForm(request.POST)
        if recipe.is_valid():
            if request.FILES.get('image', None):
                recipe.cleaned_data['image'] = base64.b64encode(request.FILES['image'].read())
            else:
                recipe.cleaned_data['image'] = models.RecipeImage.objects.get(recipe=recipe_id).image
            recipe_obj = getModelInstance(recipe, request)
            recipe_obj.id = int(recipe_id)
            recipe_obj.created = datetime.datetime.now()
            recipe_obj.save()
            saveDirsAndIngrs(recipe.cleaned_data, recipe_obj)
            return HttpResponseRedirect('/viewrecipe/%d' % recipe_obj.id)
        else:
            return HttpResponseBadRequest()

def view_recipe(request, recipe_ids):
    recipe_ids = urlparse.unquote(recipe_ids).split(',')
    if recipe_ids[0] == 'all':
        result = recipe_util.getValidRecipes(request.user.uid)
    else:
        recipe_ids = map(lambda x: long(x), recipe_ids)
        recipes = recipe_util.getValidRecipes(request.user.uid)
        recipes = filter(lambda x: x['pk'] in recipe_ids, recipes)
        if len(recipes) != len(recipe_ids):
            return HttpResponseBadRequest('You do not have permission to view the requested recipe(s).')
        result = recipes
           
    args = urlparse.parse_qs(request.META['QUERY_STRING'])
    
    if 'output' in args and 'json' in args['output']:
        response = HttpResponse()
        response.write(result)
        return response
    else:
        editable_recipes = map(lambda x: x['pk'], filter(lambda x: x['fields']['owner'] == request.user.uid, result))
        has_image = map(lambda y: y['pk'], filter(lambda x: len(models.RecipeImage.objects.filter(recipe=x['pk'])), result))
        return shortcuts.render(request, 'viewrecipe.html.tmpl', 
                                {'recipes': result,
                                 'index_data': GetIndexData(request.user.uid),
                                 'editable': editable_recipes,
                                 'has_image': has_image,
                                 'page_host': request.build_absolute_uri('/'),
                                 'page_name': 'view_recipe'})

def writePDF(form_data):
    pyx.text.set(mode='tex')
    doc = pyx.document.document()
    print form_data
    for i in range(len(form_data['recipes'])):
        canv = pyx.canvas.canvas()
        canv.text(0, 0, str(form_data['recipes'][i]))
        doc.append(pyx.document.page(canv,
                paperformat=pyx.document.paperformat(8.5 * pyx.unit.inch, 11 * pyx.unit.inch),
                margin=3*pyx.unit.t_cm))
    return doc

def generate_cookbook(request):
    if request.method == 'GET':
        return shortcuts.render(request, 'cookbook.html.tmpl',
                                {'form': recipe_form.CookbookData(request.user),
                                 'fb_code': request.REQUEST.get('code', None),
                                 'page_name': 'cookbook'})
    elif request.method == 'POST':
        form = recipe_form.CookbookData(request.user.uid, request.POST)
        if form.is_valid():
            response = HttpResponse(mimetype="application/pdf")
            pdf = writePDF(form.cleaned_data)
            pdf.writePDFfile(response)
            return response
        else:
            print form.errors
            return shortcuts.render(request, 'cookbook.html.tmpl',
                                    {'form': form,
                                     'fb_code': request.REQUEST.get('code', None),
                                     'page_name': 'cookbook'})
    

def recipe_image(request, recipe_id):
    try:
        response = HttpResponse(mimetype="image/jpeg")
        recipe = models.RecipeImage.objects.get(recipe=recipe_id)
        logging.info('image found: %s' % len(recipe.image))
        input = StringIO.StringIO(base64.b64decode(recipe.image))
        img = Image.open(input)
        if img.size[0] > img.size[1]:
            size = (500, int((img.size[0] * 1.0 / img.size[1]) * 500))
        else:
            size = (int((img.size[0] * 1.0 / img.size[1]) * 400), 400)
        img.thumbnail(size)
        img.save(response, 'JPEG')
        return response
    except:
        return HttpResponseNotFound()
