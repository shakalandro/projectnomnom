import itertools
from django.db import models


def GetCategories():
    return ['Appetizer', 'Beverage', 'Bread', 'Breakfast', 'Dessert',
            'Entree', 'Salad', 'Soup', 'Snack', 'Other']

def GetSubcategories(category=None):
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
        return map(lambda x: (x[0], map(lambda y: ('%s-%s' % (x[0], y), y), x[1])), subcategories)

def validateRating(self, n):
    return n < 100
    
class Rating(models.Model):
    recipe = models.ForeignKey('Recipe')
    rater = models.TextField()
    rating = models.PositiveSmallIntegerField(validators=[validateRating])
    comment = models.TextField()
    
class Ingredient(models.Model):
    garnish = models.BooleanField()
    item = models.CharField(max_length=100)
    prep = models.CharField(max_length=100)
    amount = models.CharField(max_length=100)

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

class Recipe(models.Model):
    """The schema for a recipe."""
    public = models.BooleanField()
    name = models.CharField(max_length=200)
    owner = models.TextField()
    author = models.CharField(blank=False, max_length=100)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    description = models.TextField(blank=False, null=True)
    servings = models.PositiveSmallIntegerField(blank=False, null=True)
    category = models.CharField(choices=map(lambda x: (x, x), GetCategories()), max_length=50)
    subcategory = models.CharField(validators=[lambda x: x in itertools.chain(*GetSubcategories().values())],
                                     max_length=50)
    image = models.TextField(blank=False, null=True)
    
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


class FacebookUser(models.Model):
    name = models.TextField()
    uid = models.EmailField()
    token = models.TextField()
    expiration = models.DateTimeField()
