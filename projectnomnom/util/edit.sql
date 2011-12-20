# delete a recipe entirely

delete from projectnomnom_ingredient
where id in (
  select i.id 
  from projectnomnom_ingredient i, projectnomnom_recipeingredient r
  where r.recipe_id = XXX and r.ingredient_id = i.id
);

delete from projectnomnom_recipeingredient
where recipe_id = XXX;

delete from projectnomnom_recipe where id = XXX;