import mox
from django import test
from django.contrib.auth import models as django_models
from django.utils import unittest
from projectnomnom import models

class RecipeModelTest(unittest.TestCase):

    FAKE_RECIPE = {
            'id': '5',
            'public': True,
            'name': 'Borshct',
            'author': 'Betty Crocker',
            'owner': 'test@example.com',
            'description': 'A tasty Soup.',
            'category': 'Soup',
            'subcategory': 'Hearty',
            'servings': 4,
            'image': 'Junk',
            'timings': {
                'id': '2',
                'prep': 10,
                'cook': 20,
                'clean': 30
                },
            'ratings': [
                {'id': '1',
                'rater': 'rater1@example.com',
                'rating': 100,
                'comment': 'Good STuff!'
                 },
                {'id': '2',
                'rater': 'rater2@example.com',
                'rating': 36,
                'comment': 'Gross, Beets!'
                 }
                ],
            'ingredients': [
                {'id': '1',
                 'item': 'Beets',
                 'prep': 'Diced',
                 'amount': '3.0',
                 },
                {'id': '2',
                 'item': 'Beef',
                 'prep': 'Diced',
                 'amount': '0.5 lb',
                 },
                {'garnish': True,
                 'id': '3',
                 'item': 'Mint',
                 'amount': '0.0 oz',
                 }
                ],
            'substitutions': [
                {'id': '1',
                 'ingredient': '1',
                 'item': 'Radishes',
                 'prep': 'Washed',
                 'amount': '4.0',
                 },
                {'id': '2',
                 'ingredient': '3',
                 'item': 'Chocolate',
                 'prep': 'Melted',
                 'amount': '10 oz',
                 'comment': 'Gross, mint!'
                 }
                ],
            'directions': [
                    'Foo',
                    'Bar',
                    'Baz'
                    ],
            'nutrition': {
                'id': '2',
                'servingsize': '1 cup',
                'calories': 1500,
                'protein': 10,
                'carbohydrates': 0,
                'fat': 3,
                'sugar': 42          
                }
            }
    
    CONVERSION_RECIPE = {
            "owner": 'shakalandro@gmail.com',
            "public": True,
            "category": "Appetizer", 
            "nutrition": {
                "id": "1",
                "calories": 300
            }, 
            "description": "Delicate crab meat sits atop a bed of melted cheese, green onions, and creamy mayo to create this irresistible dish that can serve as an appetizer or as a main dish (depending on how much you can eat!).", 
            "author": "Christie Oliver", 
            "ingredients": [
                {
                  "item": "French Bread", 
                  "amount": "16 inch loaf", 
                  "id": "1"
                }, 
                {
                  "item": "Cheddar Cheese", 
                  "amount": "12 oz", 
                  "id": "2"
                }, 
                {
                  "item": "Crab", 
                  "amount": "8 oz", 
                  "id": "3"
                }, 
                {
                  "item": "Green Onions", 
                  "amount": "6 tbsp", 
                  "id": "4"
                }, 
                {
                  "item": "Mayonnaise", 
                  "amount": "1/4 cup", 
                  "id": "5"
                }, 
                {
                  "item": "Hot Pepper Sauce", 
                  "amount": "1/8 tsp", 
                  "id": "6"
                }
            ], 
            "name": "Crab and Cheese Stuffed French Bread", 
            "servings": 4, 
            "directions": [
                "Cut bread loaf in half lengthwise and hollow out.", 
                "Flake the crab meat if not already flaked.", 
                "Chop the green onions.", 
                "Grate the cheese", 
                "Place bread on ungreased baking sheet.", 
                "Sprinkle cheese over bread halves.", 
                "Combine remaining ingredients in small  bowl and spoon crab mixture over cheese", 
                "Preheat the oven to 350 degrees", 
                "Bake until cheese bubbles.", 
                "Cut each piece in half crosswise."
            ], 
            "substitutions": [], 
            "subcategory": "Seafood"
        }

    def assertDictEqual(self, dict1, dict2):
        if len(dict1) != len(dict2):
            raise AssertionError('The given dicts have a different number of entries: %d, %d'
                                 % (len(dict1), len(dict2)))
        else:
            for key, value in dict1.iteritems():
                if key not in dict2.keys():
                    raise AssertionError('The first dict has a %s field, but the second does not.'
                                         % key)
                elif dict2[key] != value:
                    raise AssertionError('Dicts disagree on %s: %s, %s' % (key, value, dict2[key]))

    def setUp(self):
        # Create an instance of Mox
        self.mox = mox.Mox()
        test.utils.setup_test_environment()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()

    def tearDown(self):
        self.mox.VerifyAll()
        self.mox.ResetAll()
        self.mox.UnsetStubs()
        self.testbed.deactivate()
        unittest.TestCase.tearDown(self)

    def testRecipeConstruct(self):
        recipe_args = {'public': True,
                       'name': 'Borshct',
                       'owner': django_models.User(email='test@example.com')
                       }
        recipe = models.Recipe(**recipe_args)
        self.assertTrue(recipe)
"""
    def testRecipeFromDictSimple(self):
        recipe_dict = {'public': True,
                       'name': 'Borshct',
                       'owner': 'test@example.com'
                       }
        recipe = models.Recipe.FromDict(recipe_dict)
        recipe.put()
        self.assertEqual(models.Recipe.objects.all().count(), 1)
        self.assertEqual(recipe.public, True)
        self.assertTrue(recipe.created)
        self.assertEqual(recipe.name, 'Borshct')
        self.assertEqual(recipe.owner.email(), 'test@example.com')

    def testRecipeFromDictWithReference(self):
        recipe_dict = {'public': True,
                       'name': 'Borshct',
                       'owner': 'test@example.com',
                       'timings': {
                            'prep': 10,
                            'cook': 20,
                            'clean': 30
                            }
                       }
        recipe = models.Recipe.FromDict(recipe_dict)
        recipe.put()
        self.assertEqual(models.Recipe.objects.all().count(), 1)
        self.assertEqual(recipe.public, True)
        self.assertEqual(recipe.name, 'Borshct')
        self.assertEqual(recipe.owner.email(), 'test@example.com')
        self.assertEqual(recipe.timings.prep, 10)
        self.assertEqual(recipe.timings.cook, 20)
        self.assertEqual(recipe.timings.clean, 30)

    def testRecipeFromDictWithSubstitutes(self):
        recipe_dict = {'public': True,
                       'name': 'Borshct',
                       'owner': 'test@example.com',
                       'ingredients': [
                            {'id': '1',
                             'item': 'Beets',
                             'prep': 'Diced',
                             'amount': '3.0',
                             }],
                        'substitutions': [
                            {'ingredient': '1',
                             'item': 'Radishes',
                             'prep': 'Washed',
                             'amount': '4.0',
                             'comment': 'Kinda like Beets'
                             }
                            ]
                       }
        recipe = models.Recipe.FromDict(recipe_dict)
        recipe.put()
        self.assertEqual(models.Recipe.objects.all().count(), 1)
        self.assertEqual(recipe.public, True)
        self.assertEqual(recipe.name, 'Borshct')
        self.assertEqual(recipe.owner.email(), 'test@example.com')
        
        self.assertEqual(len(recipe.substitutions), 1)
        self.assertEqual(len(recipe.ingredients), 1)
        
        ingr_id = recipe.ingredients[0].id_or_name()
        subs = models.Substitution.objects.get(recipe.substitutions[0])
        self.assertEqual(subs.ingredient.key().id_or_name(), ingr_id)
        self.assertEqual(subs.ingredient.item, 'Beets')
        self.assertEqual(subs.ingredient.prep, 'Diced')
        self.assertEqual(subs.ingredient.amount, '3.0')
        self.assertEqual(subs.item, 'Radishes')
        self.assertEqual(subs.prep, 'Washed')
        self.assertEqual(subs.amount, '4.0')
        self.assertEqual(subs.comment, 'Kinda like Beets')

    def testRecipeFromDictFull(self):
        recipe = models.Recipe.FromDict(RecipeModelTest.FAKE_RECIPE)
        recipe.put()
        self.assertEqual(len(recipe.ingredients), 3)
        self.assertEqual(len(recipe.substitutions), 2)
        self.assertEqual(len(recipe.directions), 3)
        self.assertEqual(recipe.nutrition.calories, 1500)

        recipe = models.Recipe.FromDict(RecipeModelTest.CONVERSION_RECIPE)
        recipe.put()
        self.assertEqual(len(recipe.ingredients), 6)
        self.assertEqual(len(recipe.substitutions), 0)
        self.assertEqual(len(recipe.directions), 10)
        self.assertEqual(recipe.nutrition.calories, 300)

    def testRecipeToDict(self):
        recipe_args = {'public': True,
                       'name': 'Borshct',
                       'owner': django_models.User(email='test@example.com')
                       }
        recipe = models.Recipe(**recipe_args)
        recipe.put()
        recipe_dict = models.Recipe.ToDict(recipe)
        self.assertEqual(recipe_dict['public'], True)
        self.assertEqual(recipe_dict['name'], 'Borshct')
        self.assertEqual(recipe_dict['owner'], 'test@example.com')

    def testRecipeToDictWithReference(self):
        recipe_args = {'key_name': '5',
                       'public': True,
                       'name': 'Borshct',
                       'owner': users.User(email='test@example.com')
                       }
        timings_args = {'key_name': '2',
                        'prep': 10,
                        'cook': 20,
                        'clean': 30
                        }
        timings = models.Timings(**timings_args)
        recipe_args['timings'] = timings.put()
        recipe = models.Recipe(**recipe_args)
        recipe_dict = models.Recipe.ToDict(recipe)
        self.assertEqual(recipe_dict['public'], True)
        self.assertEqual(recipe_dict['name'], 'Borshct')
        self.assertEqual(recipe_dict['owner'], 'test@example.com')
        del timings_args['key_name']
        del recipe_args['key_name']
        timings_args['id'] = '2'
        recipe_args['id'] = '5'
        self.assertDictEqual(recipe_dict['timings'], timings_args)

    def testRecipeToDictWithSubstitutes(self):
        recipe_args = {'public': True,
                       'name': 'Borshct',
                       'owner': django_models.User(email='test@example.com')
                       }
        ingredient_args = {'id': '1',
                           'item': 'Beets',
                           'prep': 'Diced',
                           'amount': '3.0',
                           }
        substitution_args = {'item': 'Radishes',
                             'prep': 'Washed',
                             'amount': '4.0',
                             'comment': 'Kinda like Beets'
                             }
        ingredient = models.Ingredient(**ingredient_args)
        substitution_args['ingredient'] = ingredient.put()
        substitution = models.Substitution(**substitution_args)
        recipe_args['ingredients'] = [ingredient.put()]
        recipe_args['substitutions'] = [substitution.put()]
        recipe = models.Recipe(**recipe_args)
        recipe.put()
        recipe_dict = models.Recipe.ToDict(recipe)
        self.assertEqual(recipe_dict['public'], True)
        self.assertEqual(recipe_dict['name'], 'Borshct')
        self.assertEqual(recipe_dict['owner'], 'test@example.com')

        self.assertEqual(len(recipe_dict['ingredients']), 1)
        self.assertEqual(recipe_dict['ingredients'][0]['id'], '1')
        self.assertEqual(recipe_dict['ingredients'][0]['item'], 'Beets')
        self.assertEqual(len(recipe_dict['substitutions']), 1)
        self.assertEqual(recipe_dict['substitutions'][0]['ingredient'], '1')
        self.assertEqual(recipe_dict['substitutions'][0]['item'], 'Radishes')

    def testRecipeConvertRoundTrip(self):
        recipe = models.Recipe.FromDict(RecipeModelTest.FAKE_RECIPE)
        recipe_dict = models.Recipe.ToDict(recipe)
        # Patch the created field because it is auto-generated
        fake_recipe_temp = RecipeModelTest.FAKE_RECIPE.copy()
        fake_recipe_temp['created'] = recipe_dict['created']
        self.assertDictEqual(recipe_dict, fake_recipe_temp)

        # Make a second pass, get rid of created field
        del recipe_dict['created']
        recipe2 = models.Recipe.FromDict(recipe_dict)
        recipe_dict2 = models.Recipe.ToDict(recipe2)
        # Patch the created field because it is auto-generated
        recipe_dict['created'] = recipe_dict2['created']
        self.assertDictEqual(recipe_dict, fake_recipe_temp)
        self.assertDictEqual(recipe_dict, recipe_dict2)
"""

if __name__ == '__main__':
    unittest.main()