'''
Created on Mar 14, 2012

@author: shakalandro
'''
import pyx
from projectnomnom.util import recipe_util
from django.utils.copycompat import deepcopy

class CookbookGenerator(object):
    def __init__(self, user, options):
        options = deepcopy(options)
        self.recipe_ids = options['recipes']
        del options['recipes']
        self.options = options
        self.user = user
        
        
    def generate(self):
        doc = pyx.document.document()
        recipes = recipe_util.getValidRecipes(self.user, desired=self.recipe_ids)
        for i in range(len(recipes)):
            canv = self.format_recipe(recipes[i]['fields'])
            doc.append(pyx.document.page(canv,
                    paperformat=pyx.document.paperformat(8.5, 11),
                    margin=3*pyx.unit.t_cm))
        return doc
        

    def format_recipe(self, recipe_data):
        pyx.unit.set(defaultunit='t_inch')
        canv = pyx.canvas.canvas()
        canv.stroke(pyx.path.rect(0, 0, 8.5 * pyx.unit.t_inch, 11 * pyx.unit.t_inch))
        canv.text(0, 0, recipe_data['name'])
        canv.text(0, -10, recipe_data['author'])
        return canv
