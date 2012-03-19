from projectnomnom import models, settings

class RecipeAccessControl(object):
    """
    Handles collecting all of the recipes that are available to a given user.
    """
    
    @staticmethod
    def __getRecipePool(recipe_list):
        """
        Returns a list of recipe objects from the given list of recipe ids. If the list of recipe
        ids in None, all recipe objects are returned.
        
        Params:
            recipe_list: A list of recipe ids in string form.
        Return: A list of recipe model objects.
        """
        if recipe_list is None:
            return models.Recipe.objects.all()
        else:
            return models.Recipe.objects.filter(pk__in=recipe_list)
    
    @staticmethod
    def getUsersRecipes(user, allowed_recipes=None):
        """
        Filters and returns recipes created by the given user. Filtering will be performed on the
        all recipes unless allowed_recipes is not None in which case a subset of that list will be
        returned. Admin users are considered to have created all recipes.
        
        Note: Both public and private recipes are returned.
        
        Params:
            user: A valid user id.
            allowed_recipes: A list of recipe ids from which to filter.
        Return: A list of recipe model objects sorted by id.
        """
        recipes = RecipeAccessControl.__getRecipePool(allowed_recipes)
        recipes = recipes.filter(owner=user)
        return sorted(recipes, key=lambda x: x.pk)
    
    @staticmethod
    def getPublicRecipes(allowed_recipes=None):
        """
        Returns all public recipes. Filtering will be performed on all recipes unless
        allowed_recipes is not None in which case a subset of that list will be returned.
        
        Params:
            user: A valid user id.
            allowed_recipes: A list of recipe ids from which to filter.
        Return: A list of recipe model objects sorted by id.
        """
        recipes = RecipeAccessControl.__getRecipePool(allowed_recipes)
        recipes = recipes.filter(public=True)
        return sorted(recipes, key=lambda x: x.pk)
    
    @staticmethod
    def getUserAndPublicRecipes(user, allowed_recipes=None):
        """
        Returns the recipes that are viewable for the given user without duplicates, this includes
            1) the recipes that user created
            2) public recipes
            
        Params:
            user: the user to filter for
            desired: a list of recipe ids from which to filter
        Return: A list of recipe model objects sorted by id.
        """
        recipes = RecipeAccessControl.__getRecipePool(allowed_recipes)
        public_recipes = recipes.filter(public=True)
        my_recipes = recipes.filter(public=False, owner=user)
        return sorted(list(my_recipes) + list(public_recipes), key=lambda x: x.pk)

