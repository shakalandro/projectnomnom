import itertools
import json
from django.core import serializers
from django.db import models


class ModelUtility(object):
    """
    Provides a bunch of utility functions for the model classes. These functions could not be
    included in their respective models because the python class loader will not have these defined
    at the time that they are used in the class.
    
    TODO: move these into their proper classes and see if they will load when placed above the
        field definitions.
    """
    
    @staticmethod
    def getCategories():
        return ['Appetizer', 'Beverage', 'Bread', 'Breakfast', 'Dessert',
                'Entree', 'Salad', 'Soup', 'Snack', 'Other']
    
    @staticmethod
    def getSubcategories(category=None):
        subcategories = (('-none-', ('-none-',)),
                         ('Appetizer', ('Meaty', 'Vegetarian', 'Seafood', 'Othur')),
                         ('Beverage', ('Cocktail', 'Mixed Alcoholic', 'Milkshake',
                                      'Smoothie', 'Coffee', 'Juice', 'Tea', 'Other')),
                         ('Bread', ('Bread', 'Biscuit', 'Muffin', 'Other')),
                         ('Breakfast', ('Eggs', 'Pancakes/Waffles/Crepes', 'Bacon', 'Other')),
                         ('Dessert', ('Cake', 'Pie', 'Cookie', 'Ice-Cream', 'Candy',
                                     'Pudding', 'Other')),
                         ('Entree', ('Meaty', 'Seafood', 'Pasta', 'Casserole', 'Vegetarian',
                                    'Pizza', 'Stir-Fry', 'Other')),
                         ('Salad', ('Pasta Salad', 'Fruit Salad', 'Vegetable Salad', 'Other')),
                         ('Soup', ('Cream', 'Broth', 'Hearty', 'Chowder', 'Other')),
                         ('Snack', ('Fruit', 'Sandwich', 'Seafood', 'Other')),
                         ('Other', ('Dip', 'Sauce', 'Other')))
        if category is not None:
            for type, values in subcategories:
                if type == category:
                    return values
            return None
        else:
            return map(lambda x: (x[0], map(lambda y: ('%s-%s' % (x[0], y), y), x[1])),
                       subcategories)
    
    @staticmethod
    def subCategoryValidator(category):
        return category in itertools.chain(*ModelUtility.getSubcategories().values())
    
    @staticmethod
    def validateRating(n):
        return n < 100

    
class Rating(models.Model):
    recipe = models.ForeignKey('Recipe')
    rater = models.TextField()
    rating = models.PositiveSmallIntegerField(validators=[ModelUtility.validateRating])
    comment = models.TextField()


class Ingredient(models.Model):
    garnish = models.BooleanField()
    item = models.CharField(max_length=100)
    prep = models.CharField(max_length=100)
    amount = models.CharField(max_length=100)

    def toJson(self):
        """
        Returns the current model object in JSON format.
        """
        return json.loads(serializers.serialize('json', [self]))[0]

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey('Recipe')
    ingredient = models.ForeignKey('Ingredient')


class Substitution(models.Model):
    recipe = models.ForeignKey('Recipe')
    ingredient = models.ForeignKey('Ingredient', related_name='ingr')
    substitute = models.ForeignKey('Ingredient', related_name='sub')
    comment = models.TextField()


class Directions(models.Model):
    recipe = models.ForeignKey('Recipe')
    step_number = models.PositiveSmallIntegerField()
    direction = models.TextField()
    
    def toJson(self):
        """
        Returns the current model object in JSON format.
        """
        return json.loads(serializers.serialize('json', [self]))[0]


class RecipeImage(models.Model):
    recipe = models.ForeignKey('Recipe', primary_key=True)
    image = models.TextField(blank=False, null=True)


class Recipe(models.Model):
    """The schema for a recipe."""
    public = models.BooleanField()
    name = models.CharField(max_length=200)
    owner = models.TextField()
    author = models.CharField(blank=False, max_length=100)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    description = models.TextField(blank=False, null=True)
    servings = models.PositiveSmallIntegerField(blank=False, null=True)
    category = models.CharField(choices=map(lambda x: (x, x), ModelUtility.getCategories()),
                                max_length=50)
    subcategory = models.CharField(validators=[ModelUtility.subCategoryValidator], max_length=50)
    
    #timings
    prep_time = models.IntegerField(blank=False, null=True)
    cook_time = models.IntegerField(blank=False, null=True)
    clean_time = models.IntegerField(blank=False, null=True)
    
    #nutrition
    servingsize = models.CharField(blank=False, max_length=100, null=True)
    calories = models.PositiveSmallIntegerField(blank=False, null=True)
    protein = models.PositiveSmallIntegerField(blank=False, null=True)
    carbohydrates = models.PositiveSmallIntegerField(blank=False, null=True)
    fat = models.PositiveSmallIntegerField(blank=False, null=True)
    sugar = models.PositiveSmallIntegerField(blank=False, null=True)
    
    def __str__(self):
        return self.title
    
    def getIngredients(self):
        """
        Returns a list of Ingredient model objects that correspond to the current Recipe.
        """
        return sorted(Ingredient.objects.filter(recipeingredient__recipe=self.pk),
                      key=lambda x: x.pk)

    def getDirections(self):
        """
        Returns a list of Direction model objects that correspond to the current Recipe.
        """
        return sorted(Directions.objects.filter(recipe__id=self.pk),
                      key=lambda x: x.step_number)
    
    def hasRecipeImage(self):
        """
        Returns whether the current Recipe has an image.
        """
        return len(RecipeImage.objects.filter(recipe=self.pk)) > 0
    
    def hasNutritionInfo(self):
        """
        Returns whether the current Recipe has nutrition information.
        """
        return (self.servingsize is not None or
                self.calories is not None or
                self.protein is not None or
                self.carbohydrates is not None or
                self.fat is not None or
                self.sugar is not None)
    
    def toJson(self):
        """
        Returns the current model object in JSON format.
        """
        return json.loads(serializers.serialize('json', [self]))[0]


class FacebookUser(models.Model):
    name = models.TextField()
    uid = models.EmailField()
    token = models.TextField()
    expiration = models.DateTimeField()
