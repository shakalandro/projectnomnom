'''
Creates a cookbook PDF from a set of provided options.

@author: Roy McElmurry (roy.miv@gmail.com)
'''
import pyx
from projectnomnom.util import recipe_access_control as acl
from django.utils.copycompat import deepcopy

class CookbookGenerator(object):
    """
    Handles the creation of a PDF file from a set of options.
    """
    def __init__(self, user, options):
        """
        Params:
            user: The id of the app user.
            options: A dictionary of cookbook options derived from a CookbookData form.
        """
        options = deepcopy(options)
        self.recipe_ids = options['recipes']
        del options['recipes']
        self.options = options
        self.user = user
        
        
    def generate(self):
        """
        Returns a pyx document that can be used to write a PDF file.
        """
        doc = pyx.document.document()
        recipes = acl.RecipeAccessControl.getUserAndPublicRecipes(self.user,
                                                                  allowed_recipes=self.recipe_ids)
        for r in recipes:
            page = self.format_recipe(r)
            doc.append(page)
        return doc
        

    def format_recipe(self, recipe):
        """
        Formats a single recipe into a single 8.5 x 11 page.
        
        Params:
            recipe: The recipe to format.
        Return: A pyx page object.
        """
        pyx.unit.set(defaultunit='t_inch')
        canv = pyx.canvas.canvas()
        canv.stroke(pyx.path.rect(0, 0, 8.5 * pyx.unit.t_inch, 11 * pyx.unit.t_inch))
        canv.text(0, 0, recipe.name)
        canv.text(0, -10, recipe.author)
        return pyx.document.page(canv,
                                 paperformat=pyx.document.paperformat(8.5, 11),
                                 margin=3*pyx.unit.t_cm)
