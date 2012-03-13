import json
from projectnomnom import models, settings
from django.core import serializers 


def getValidRecipes(user):
    public_recipes = models.Recipe.objects.filter(public=True)
    my_recipes = models.Recipe.objects.filter(public=False, owner__in=[user] + settings.FACEBOOK['APP_ADMINS'])
    return sorted(JoinRecipes(list(my_recipes) + list(public_recipes)), key=lambda x: x['pk'])


def JoinRecipes(recipes):
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