'''
Created on Mar 15, 2012

@author: shakalandro
'''

from haystack import indexes, site
from projectnomnom import models

class RecipeIndex(indexes.SearchIndex): 
    name = indexes.CharField(model_attr='name', document=True)
    author = indexes.CharField(model_attr='author')
    
    def index_queryset(self):
        return models.Recipe.objects.all()
    
    def prepare(self, obj):
        self.prepared_data = super(RecipeIndex, self).prepare(obj)
        self.prepared_data['text'] = obj.name
        return self.prepared_data
    
site.register(models.Recipe, RecipeIndex)