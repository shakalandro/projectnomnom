"""
This script saves the database into a fixture that could be used later to re-seed the database.

Note: needs to be run from the django shell with python manage.py shell

@author: Roy McElmurry(roy.miv@gmail.com)
"""

import optparse
import datetime
import os
from django.core.management.base import BaseCommand
from django.core import serializers
from projectnomnom import models


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            optparse.make_option('--out', default='fixture', help='File name prefix of archive.'),
            optparse.make_option('--dir', help='Archive directory.',
                    default=os.path.join(os.path.dirname(__file__), '/fixtures')))
    
    def handle(self, *args, **options):
    
        dir_name = '%s/%s/%s/%s/' % (options['dir'], datetime.date.today().year,
                                     datetime.date.today().month,
                                     datetime.date.today().day)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        data = []
        for recipe in models.Recipe.objects.all():
            data.append(recipe)
            try:
                data.append(models.RecipeImage.objects.get(recipe=recipe.id))
            except:
                pass
            for recipe_ingr in models.RecipeIngredient.objects.all().filter(recipe=recipe.id):
                data.append(recipe_ingr)
                data.append(models.Ingredient.objects.get(id=recipe_ingr.ingredient.id))
            for dir in models.Directions.objects.all().filter(recipe=recipe.id):
                data.append(dir)
            for sub in models.Substitution.objects.all().filter(recipe=recipe.id):
                data.append(sub)
            for rating in models.Rating.objects.all().filter(recipe=recipe.id):
                data.append(rating)
        
        out = open(os.path.join(dir_name, '%s_%s.json' % (options['out'], datetime.datetime.now().isoformat())), 'w')
        out.write(serializers.serialize('json', data, indent=2))
        out.close()
        self.stdout.write('Data saved to %s\n' % out.name)
        
        out = open(os.path.join(options['dir'], 'initial_data.json'), 'w')
        out.write(serializers.serialize('json', data, indent=2))
        out.close()
        self.stdout.write('Data saved to %s\n' % out.name)
