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