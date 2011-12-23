import argparse
import datetime
import os
try:
    from projectnomnom import models
    from django.core import serializers
except:
    import sys
    sys.path.append('.')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'projectnomnom.settings'
    from projectnomnom import models
    from django.core import serializers

def to_serial(thing):
    return 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build backup fixture from DB.')
    parser.add_argument('--out', default='fixture', help='File name prefix of archive.')
    parser.add_argument('--dir', default='projectnomnom/fixtures', help='Archive directory.')
    args = parser.parse_args()

    dir_name = '%s/%s/%s/%s/' % (args.dir, datetime.date.today().year,
                                 datetime.date.today().month,
                                 datetime.date.today().day)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    data = []
    for recipe in models.Recipe.objects.all():
        data.append(recipe)
        for recipe_ingr in models.RecipeIngredient.objects.all().filter(recipe=recipe.id):
            data.append(recipe_ingr)
            data.append(models.Ingredient.objects.get(id=recipe_ingr.ingredient.id))
        for dir in models.Directions.objects.all().filter(recipe=recipe.id):
            data.append(dir)
        for sub in models.Substitution.objects.all().filter(recipe=recipe.id):
            data.append(sub)
        for rating in models.Rating.objects.all().filter(recipe=recipe.id):
            data.append(rating)
    
    out = open(os.path.join(dir_name, '%s_%s.json' % (args.out, datetime.datetime.now().isoformat())), 'w')
    out.write(serializers.serialize('json', data))
    out.close()
    print 'Data saved to %s' % out.name
    
    out = open(os.path.join(args.dir, 'initial_data.json'), 'w')
    out.write(serializers.serialize('json', data))
    out.close()
    print 'Data saved to %s' % out.name
