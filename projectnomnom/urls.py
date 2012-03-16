from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^/?$', redirect_to, {'url': '/viewrecipe/all'}),
    url(r'^viewrecipe/$', redirect_to, {'url': '/viewrecipe/all'}),
    url(r'^viewrecipe/(?P<recipe_ids>(\d+(,\d+)*)|all)$', 'projectnomnom.views.view_recipe'),
    url(r'^recipeimage/(?P<recipe_id>\d+).jpg$', 'projectnomnom.views.recipe_image'),
    url(r'^addrecipe$', 'projectnomnom.views.add_recipe'),
    url(r'^cookbook$', 'projectnomnom.views.cookbook'),
    url(r'^editrecipe/(?P<recipe_id>\d+)$', 'projectnomnom.views.edit_recipe'),
    url(r'^search/', 'projectnomnom.views.search'),
)