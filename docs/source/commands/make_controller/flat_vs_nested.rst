Flat vs Nested with make:controller 
===================================

Some controller names describe only one clear model shape. Others can describe
more than one valid data structure, and that is where this chapter gets
interesting.

Choose Flat vs Nested When Using ``-m``
---------------------------------------

.. youtube_embed:: choose-flat-vs-nested-when-using-m

Suppose you run:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud -m

If ``Recipe`` already exists, Flask-Commands can see two possible model
stories:

- flat: ``RecipeIngredient``
- nested: ``Ingredient`` under ``Recipe``

So it prompts you to choose.

If you choose **flat**:

- model generated: ``RecipeIngredient``
- controller stays ``RecipeIngredientController``
- CRUD routes are flat under ``/recipe-ingredients``

If you choose **nested**:

- model generated: ``Ingredient``
- controller still stays ``RecipeIngredientController``
- CRUD routes are nested under ``/recipes/<int:recipe_id>/ingredients``

You can skip the prompt with:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud -m --flat
   flask make:controller RecipeIngredientController --crud -m --nest

The rules are:

- ``--flat`` and ``--nest`` are mutually exclusive
- ``--flat`` and ``--nest`` require ``-m`` or ``--generate-model``
- ``--flat`` and ``--nest`` cannot be combined with explicit ``--model``

This is one of those spots where the tool is trying to be honest rather than
magical. Sometimes a name can describe more than one good structure, and in
that moment the command lets you decide which story your app should tell.

The same flat-versus-nested decision shows up again from the model-first side,
and it is worth seeing from that direction too.


topics to discuss with chat
never use the word 'infer' instead us the word 'generate' in Choose Flat for One Multi-Word Model we should tie back to the prior chapter where we did the same thing but had to use --model and then explicity tell Flask Commands that the model was a two word model otherwise we would have ended up with a namespace of Shopping and a crud structure on List.  With the combo of -m and --flat we solve this problem without have to provide a variable and instead let flask commands generate everything from the controller name.  

in Choose Nested for a Registered Parent and a New Child i think we should show what happens when Recipe is not registered and when Recipe is registered.  in both cases you end up with the two distinct data structures recipe and ingredient however if you do not build up the data structures sequentually like

flask make:controller RecipeController --crud -m 
flask make:controller RecipeIngredientController --crud -m --nest

then you end up with Recipe model but no routes or templates specifficly for recipe.  However flask commands is forgiving in that if you did do 

flask make:controller RecipeIngredientController --crud -m --nest

first then you can actually go back and now do 

flask make:controller RecipeController --crud -m 

or if you just want a specific RESTful resource like show or index you could do 

flask make:view recipes.index -rc
flask make:view recipes.show -rc

