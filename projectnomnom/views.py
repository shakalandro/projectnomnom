import json
import urlparse
import base64
import operator
import logging
import StringIO
import datetime
from projectnomnom import models, recipe_form
from PIL import Image
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.core import serializers
from django.utils import datastructures
from django.utils.copycompat import deepcopy
from django import shortcuts


def getValidRecipes(user):
    public_recipes = models.Recipe.objects.filter(public=True)
    my_recipes = models.Recipe.objects.filter(public=False, owner=user)
    return sorted(JoinRecipes(list(my_recipes) + list(public_recipes)), key=lambda x: x['pk'])


def JoinRecipes(recipes):
    recipes = toJson(recipes)
    for i in range(len(recipes)):
        ingrs = models.Ingredient.objects.filter(recipeingredient__recipe=recipes[i]['pk'])
        directions = models.Directions.objects.filter(recipe__id=recipes[i]['pk'])
        recipes[i]['fields']['ingredients'] = map(lambda x: x['fields'], toJson(ingrs))
        recipes[i]['fields']['directions'] = sorted(map(lambda x: x['fields'], toJson(directions)),
                                                    key=lambda x: x['step_number'])
    return recipes


def GetIndexData(user):
        recipes = getValidRecipes(user)
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


def toJson(recipes):
    return json.loads(serializers.serialize('json', recipes))

def getModelInstance(recipe, request):
    recipe = deepcopy(recipe)
    del recipe.cleaned_data['ingredients']
    del recipe.cleaned_data['directions']            
    parts = recipe.cleaned_data['category'].split('-')
    recipe.cleaned_data['category'] = parts[0]
    recipe.cleaned_data['subcategory'] = parts[1]
    recipe.cleaned_data['owner'] = request.user.uid
    if 'image' in request.FILES:
        image_data = request.FILES['image'].read()
        recipe.cleaned_data['image'] = base64.b64encode(image_data)
    return models.Recipe(**recipe.cleaned_data)    


def saveDirsAndIngrs(data, recipe_obj):
    """
    Params:
        data: a bound recipe form object
        recipe_obj: a recipe model instance corresponding to recipe that has been saved
    """
    recipe_ingrs = models.RecipeIngredient.objects.filter(recipe=recipe_obj)
    ingrs = models.Ingredient.objects.filter(id__in=recipe_ingrs)
    dirs = models.Directions.objects.filter(recipe=recipe_obj)
    recipe_ingrs.delete()
    ingrs.delete()
    dirs.delete()
    
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
    print 'adding: %s' % request.method
    if request.method == 'GET':
        recipe_form_inst = recipe_form.RecipeForm()
        return shortcuts.render(request, 'addrecipe.html.tmpl',
                                {'form': recipe_form_inst,
                                 'index_data': GetIndexData(request.user.uid),
                                 'fb_code': request.REQUEST.get('code', None)})
    elif request.method == 'POST':
        # need to wipe and rewrite new directions and ingreadients, need to pull this out for security
        recipe = recipe_form.RecipeForm(request.POST)
        if recipe.is_valid():
            recipe_obj = getModelInstance(recipe, request)
            recipe_obj.save()
            print 'recipe_id: %s' % recipe_obj.id
            saveDirsAndIngrs(recipe.cleaned_data, recipe_obj)
            return HttpResponseRedirect('/viewrecipe/%d' % recipe_obj.id)
        else:
            return shortcuts.render(request, 'addrecipe.html.tmpl',
                                    {'form': recipe,
                                     'index_data': GetIndexData(request.user.uid)})
def edit_recipe(request, recipe_id):
    recipe = models.Recipe.objects.get(id=recipe_id)
    if recipe.owner != request.user.uid and False:
        return HttpResponseForbidden()
    
    if request.method == 'GET':
        recipe_dict = JoinRecipes([recipe])[0]['fields']
        # fix ingredients
        for idx, ingr in enumerate(recipe_dict['ingredients']):
            for key, value in ingr.items():
                recipe_dict['ingredients-%d-%s' % (idx, key)] = value
        del recipe_dict['ingredients']
        # fix directions
        for idx, dir in enumerate(recipe_dict['directions']):
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
                                 'fb_code': request.REQUEST.get('code', None)})
    else:
        recipe = recipe_form.RecipeForm(request.POST)
        if recipe.is_valid():
            if 'image' not in recipe.cleaned_data or recipe.cleaned_data['image'] is None:
                recipe.cleaned_data['image'] = models.Recipe.objects.get(id=recipe_id).image
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
        result = getValidRecipes(request.user.uid)
    else:
        recipe_ids = map(lambda x: long(x), recipe_ids)
        recipes = getValidRecipes(request.user.uid)
        recipes = filter(lambda x: x is not None and
                         (x['fields']['owner'] == request.user.uid or x['fields']['public']) and
                         x['pk'] in recipe_ids, recipes)
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
        print editable_recipes
        return shortcuts.render(request, 'viewrecipe.html.tmpl', 
                                {'recipes': result,
                                 'index_data': GetIndexData(request.user.uid),
                                 'editable': editable_recipes,
                                 'page_url': request.build_absolute_uri(request.path)})

def recipe_image(request, recipe_id):
    try:
        response = HttpResponse(mimetype="image/jpeg")
        recipe = models.Recipe.objects.get(id=recipe_id)
        if recipe.image is not None and recipe.image != '':
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
