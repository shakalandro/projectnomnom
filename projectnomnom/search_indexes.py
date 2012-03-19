'''
Defines the data to be indexed by the haystack module. If any changes are made to this module you
must run the following command

python manage.py rebuild_index

@author: shakalandro
'''

from haystack import indexes, site
from projectnomnom import models

class RecipeIndex(indexes.RealTimeSearchIndex): 
    text = indexes.CharField(document=True)
    name = indexes.CharField(model_attr='name')
    author = indexes.CharField(model_attr='author')
    
    def index_queryset(self):
        return models.Recipe.objects.all()
    
    def prepare(self, obj):
        self.prepared_data = super(RecipeIndex, self).prepare(obj)
        ingrs = models.Ingredient.objects.filter(recipeingredient__recipe=obj.pk)
        ingr_text = reduce(lambda x, y: x + ' ' + y.item, ingrs, '')
        self.prepared_data['text'] = obj.name + obj.author + ingr_text
        return self.prepared_data
    

site.register(models.Recipe, RecipeIndex)