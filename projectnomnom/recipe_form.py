import json
import logging
import operator
from django import forms
from django.core import exceptions
from django.forms.formsets import formset_factory
from django.utils import safestring
from projectnomnom import models
from projectnomnom.util import list_field, recipe_util
from django.core import serializers


def to_json(stuff):
    return json.loads(serializers.serialize('json', stuff))


def BuildCategoryChoices():
    return models.GetSubcategories()


def CategoryValidator(value):
    parts = value.split('-')
    if (len(parts) != 2 or parts[0] not in models.GetCategories() or
            parts[1] not in models.GetSubcategories(category=parts[0])):
        raise exceptions.ValidationError('You must choose a valid category.')


def IngredientsValidator(values):
    logging.info(values)
    factory_class = formset_factory(IngredientForm)
    formset = factory_class(values, prefix='ingredients')
    map(lambda x: x.is_valid(), formset.forms)
    ingr_names = []
    for form in formset.forms:
        if 'item' in form.cleaned_data and form.cleaned_data['item'] != '':
            ingr_names.append(form.cleaned_data['item'])

    for form in formset.forms:
        if ('substitute' in form.cleaned_data and form.cleaned_data['substitute'] and
                form.cleaned_data['sub_ingredient'] not in ingr_names):
            raise exceptions.ValidationError('You must choose a valid ingredient to substitute.')            


class IngredientForm(forms.Form):
    item = forms.CharField(label='Ingredient')
    amount = forms.CharField(label='Amount')
    prep = forms.CharField(label='Prep', required=False)
    garnish = forms.BooleanField(label='Garnish', initial=False, required=False)
    substitute = forms.BooleanField(label='Substitute', initial=False, required=False)
    sub_ingredient = forms.ChoiceField(label='For', required=False)
    comment = forms.CharField(label='Comment', required=False)


class DirectionForm(forms.Form):
    direction = forms.CharField(label='')


class NutritionForm(forms.Form):
    calories = forms.IntegerField(label='Calories', required=False)
    protein = forms.IntegerField(label='Protein', required=False)
    carbohydrates = forms.IntegerField(label='Carbohydrates', required=False)
    fat = forms.IntegerField(label='Fat', required=False)
    sugar = forms.IntegerField(label='Sugar', required=False)


class TimingsForm(forms.Form):
    prep_timing = forms.IntegerField(label='Prep Time', required=False)
    cook_timing = forms.IntegerField(label='Cook Time', required=False)
    clean_timing = forms.IntegerField(label='Clean Time', required=False)


class RecipeForm(forms.Form):
    class Media:
        css = {'all': ('/static/recipe_form.css',)}
        js = ('/static/recipe_form.js',)
    
    name = forms.CharField(required=True, label='Recipe Name')
    author = forms.CharField(required=True, label='Recipe Author')
    public = forms.BooleanField(required=False, initial=True)
    image = forms.ImageField(required=False)
    category = forms.ChoiceField(choices=BuildCategoryChoices(), required=True, label='Category',
                                 validators=[CategoryValidator])
    servings = forms.IntegerField(required=True, label='Servings')
    description = forms.CharField(required=True, label='Description',
                                  widget=forms.Textarea(attrs={'rows': 5, 'cols': 60}))
    ingredients = list_field.ListField(base_form=IngredientForm, is_ordered=False, label='Ingredients',
                                       required=True, validators=[IngredientsValidator])
    directions = list_field.ListField(base_form=DirectionForm, label='Directions', required=True)
    timings = TimingsForm()
    nutrition = NutritionForm()
    
    def __init__(self, data=None, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, data=data, **kwargs)
        if data and len(data):
            self.timings = TimingsForm(data=data)
            self.nutrition = NutritionForm(data=data)
        
    def full_clean(self):
        super(RecipeForm, self).full_clean()
        self.timings.full_clean()
        self.nutrition.full_clean()

    def is_valid(self):
        return (super(RecipeForm, self).is_valid() and
                self.timings.is_valid() and
                self.nutrition.is_valid())

    def as_p(self):
        result = super(RecipeForm, self).as_p()
        result += ('</ul><p>Timings (in minutes):</p><ul>' +
                   self.timings.as_ul() +
                   '</ul></ol>\n<p>Nutrition (in grams):</p><ul>' +
                   self.nutrition.as_ul() +
                   '</ul>')
        return safestring.mark_safe(result)

class CookbookData(forms.Form):
    recipes = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple)
    recipe_size = forms.ChoiceField(choices=[(1, 'full page'), (0.5, '1/2 page'), (0.16, '1/6 page')],
                                    widget=forms.RadioSelect)
    show_page_numbers = forms.BooleanField(required=False)
    show_authors = forms.BooleanField(required=False)
    
    def __init__(self, user, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        recipe_ids = sorted(map(lambda x: (x['pk'], x['fields']['name']), recipe_util.getValidRecipes(user)),
                            key=operator.itemgetter(1))
        self.fields['recipes'] = forms.MultipleChoiceField(choices=recipe_ids,
                                                           widget=forms.CheckboxSelectMultiple)

