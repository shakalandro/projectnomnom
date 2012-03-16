import json
from projectnomnom import models, settings
from django.core import serializers 


def getValidRecipes(user, desired=None, joined=True):
    """
    Returns the recipes that are viewable for the given user, this includes
        1) recipes that user created
        2) public recipes
        
    Params:
        user: the user to filter for
        desired: a list of recipe ids from which to filter
    """
    if desired is None:
        recipes = models.Recipe.objects.all()
    else:
        recipes = models.Recipe.objects.filter(pk__in=desired)
    public_recipes = recipes.filter(public=True)
    my_recipes = recipes.filter(public=False, owner__in=[user] + settings.FACEBOOK['APP_ADMINS'])
    all_recipes = list(my_recipes) + list(public_recipes)
    if joined:
        all_recipes = joinRecipes(all_recipes)
    else:
        all_recipes = toJson(all_recipes)
    return sorted(all_recipes, key=lambda x: x['pk'])

def getViewableRecipes(user):
    recipes = models.Recipe.objects.all()
    public_recipes = recipes.filter(public=True)
    my_recipes = recipes.filter(public=False, owner__in=[user] + settings.FACEBOOK['APP_ADMINS'])
    return list(my_recipes) + list(public_recipes)

def joinRecipes(recipes):
    """
    Given a list of Recipe model objects, adds the ingredients and directions to the data fields
    """
    recipes = toJson(recipes)
    for i in range(len(recipes)):
        ingrs = models.Ingredient.objects.filter(recipeingredient__recipe=recipes[i]['pk'])
        directions = models.Directions.objects.filter(recipe__id=recipes[i]['pk'])
        recipes[i]['fields']['ingredients'] = map(lambda x: x['fields'], toJson(ingrs))
        recipes[i]['fields']['directions'] = sorted(map(lambda x: x['fields'], toJson(directions)),
                                                    key=lambda x: int(x['step_number']))
    return recipes

def toJson(recipes):
    return json.loads(serializers.serialize('json', recipes))