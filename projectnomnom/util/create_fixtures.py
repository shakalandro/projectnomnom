'''
Created on Aug 31, 2011

@author: shakalandro
'''

import argparse
import base64
import json
import logging
import StringIO
import os
import glob
import itertools
from PIL import Image
from xml.etree import ElementTree


parser = argparse.ArgumentParser(argument_default=None,
        description='Import ProjectNomNom 1.0 XML files into Google Appengine data store.')
parser.add_argument('-d', '--directory', metavar='D', type=str,
                    help='The directory to crawl for recipe XML files.',
                    default='.')
parser.add_argument('-l', '--levels', metavar='L', type=int,
                    help='How many directories deep are the XML files from the directory.',
                    default=2)
parser.add_argument('-s', '--host', metavar='S', type=str,
                    help='The url of the ProjectNomNom server to add recipes to.',
                    default='localhost')
parser.add_argument('-t', '--port', metavar='T', type=int,
                    help='The port of the ProjectNomNom server to add recipes to.',
                    default=8080)
parser.add_argument('-p', '--password', metavar='P', type=str,
                    help='The password associated with the given user email.')
parser.add_argument('-u', '--user', metavar='U', type=str,
                    help='The email of the Google user to connect with and import recipes as.')
parser.add_argument('-i', '--max_image_size', metavar='I', type=int, default=3500,
                    help='The maximum width in pixels that uploaded images should be '
                         '(assumes jpeg output).')

# Prevents primary keys from clashing
_INGREDIENT_COUNT = 1
_DIRECTION_COUNT = 1

def ParseIngredientOrSubstitute(xml):
    """Parses an 'item' or 'substitute' element and returns the resulting dict."""
    amount = xml.get('amount')
    prep = xml.get('prep')
    result = {'fields': {'item': xml.text.strip()}}
    if prep is not None:
        result['fields']['prep'] = prep
    if amount is not None:
        result['fields']['amount'] = amount
    return result

def XMLRecipeToDict(xml, num):
    global _INGREDIENT_COUNT
    global _DIRECTION_COUNT
    recipe_dict = {'model': 'projectnomnom.recipe',
                   'pk': num,
                   'fields': {'public': True,
                              'owner': 'test@example.com'}}
    static_info_fields = ['name', 'author', 'category', 'subcategory']
    information = xml.find('information')
    for item in static_info_fields:
        recipe_dict['fields'][item] = information.find(item).text.strip()
    
    # category fix
    if recipe_dict['fields']['category'] == 'Beverages':
        recipe_dict['fields']['category'] = 'Beverage'
    
    description = information.find('description')
    if description is not None:
        recipe_dict['fields']['description'] = description.text.strip()
        recipe_dict['fields']['servings'] = int(description.get('serves'))
    
    ingredients = xml.find('ingredients')
    ingredients_list = []
    recipe_ingredients = []
    subs_list = []
    for ingr in itertools.chain(ingredients.findall('ingredient'), ingredients.findall('garnish')):
        item = ingr.find('item')
        ingredient = ParseIngredientOrSubstitute(item)
        ingredient['model'] = 'projectnomnom.ingredient'
        ingredient['pk'] = str(_INGREDIENT_COUNT)
        ingredient['fields']['garnish'] = ingr.tag == 'garnish'
        ingredients_list.append(ingredient)
        
        recipe_ingredients.append({'model': 'projectnomnom.recipeingredient',
                                   'pk': str(_INGREDIENT_COUNT),
                                   'fields': {'recipe': num,
                                              'ingredient': str(_INGREDIENT_COUNT)}})
        _INGREDIENT_COUNT += 1
        subs = ingr.find('substitute')
        if subs:
            sub = ParseIngredientOrSubstitute(subs)
            sub['model'] = 'projectnomnom.ingredient'
            sub['pk'] = str(_INGREDIENT_COUNT)
            sub['fields']['garnish'] = False
            ingredients_list.append(sub)
            subs_list.append({'model': 'projectnomnom.substitution',
                          'pk': str(_INGREDIENT_COUNT),
                          'fields': {'ingredient': str(_INGREDIENT_COUNT - 1),
                                     'substitute': str(_INGREDIENT_COUNT),
                                     'recipe': num}})
            _INGREDIENT_COUNT += 1
    
    directions = xml.find('directions')
    directions_list = []
    direction_count = 1
    for direction in (directions.findall('*/step') + directions.findall('step')):
        directions_list.append({'model': 'projectnomnom.directions',
                                'pk': _DIRECTION_COUNT,
                                'fields': {'direction': direction.text.strip(),
                                           'step_number': direction_count,
                                           'recipe': num}
                                })
        direction_count += 1
        _DIRECTION_COUNT += 1
    
    static_nutr_fields = ['servingsize', 'calories', 'protein', 'fat', 'sugar']
    nutrition = xml.find('nutrition')
    if nutrition is not None:
        for kind in static_nutr_fields:
            nutr_kind = nutrition.find(kind)
            if nutr_kind is not None:
                recipe_dict['fields'][kind] = int(nutr_kind.text.strip())

    return [recipe_dict] + recipe_ingredients + ingredients_list + subs_list + directions_list

if __name__ == '__main__':    
    args = parser.parse_args()
    base_path = args.directory + '/*' * args.levels
    recipe_imgs = glob.glob('%s/*.jpg' % base_path)
    recipes = []
    recipe_count = 1
    for recipe in glob.glob('%s/*.xml' % base_path):
        data = XMLRecipeToDict(ElementTree.parse(recipe), recipe_count)
        recipe_dict = data[0]['fields']

        recipe_count += 1
        img_name = '%s/%s.jpg' % (os.path.dirname(recipe), data[0]['fields']['name'].replace(' ', '_'))
        
        if img_name in recipe_imgs:
            img = Image.open(img_name)
            width, height = img.size
            if width > args.max_image_size:
                newheight = int(args.max_image_size * (height / float(width)))
                logging.warning('Resizing image from (%s %s) to (%s %s)', width,
                             height, args.max_image_size, newheight)
                img = img.resize((args.max_image_size, newheight))
            outstr = StringIO.StringIO()
            img.save(outstr, 'jpeg')
            recipe_dict['image'] = base64.b64encode(outstr.getvalue())
            
        recipes += data
        
    f = open('/Users/shakalandro/Code/Projects/ProjectNomNom2/projectnomnom/fixtures/initial_data.json', 'w')
    f.write(json.dumps(recipes, indent=2))
    f.close()
