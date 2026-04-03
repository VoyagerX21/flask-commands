make:controller and Models
==========================

Controllers usually exist because some kind of data needs to be shown,
updated, or organized. That is why ``flask make:controller`` does not stop at
controller files.

Add a Model with ``--model`` vs ``-m``
--------------------------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: Add a model with --model vs -m.*

Often a controller is tied to a model. Flask-Commands gives you two ways to
handle that.

You can explicitly name the model:

.. code-block:: bash

   flask make:controller IngredientController --model Ingredient

or you can let Flask-Commands generate the model name from the controller
name:

.. code-block:: bash

   flask make:controller IngredientController -m

These two commands produce the same general result:

- a plain ``IngredientController``
- an ``Ingredient`` model

The difference is how the model name is chosen.

Use ``--model`` when you want to state the model name directly.

Use ``-m`` or ``--generate-model`` when you want Flask-Commands to infer the
model name from the controller name.

That may sound like a small distinction, but it becomes much more useful once
you start working with nested structures.

Go Nested with ``--crud``
-------------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: Go nested with make:controller --crud.*

Now let’s say our cooking app needs a relationship like **Recipe -> Ingredient**.

That means we want a nested controller:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud

With this one change, you get a lot of structural benefits:

- ``app/controllers/recipe_ingredient_controller.py``
- nested routes under ``app/routes/recipes/ingredients/``
- templates under ``app/templates/recipes/ingredients/``
- nested endpoint names like ``recipes.ingredients.index``

That last part matters a lot to me.

If ingredients belong to recipes, I want the route names, folder structure,
and controller name to read that way too. The app should tell the truth about
the relationship.

So instead of a flat route like:

- ``/ingredients``

you get the nested route shape:

- ``/recipes/<int:recipe_id>/ingredients``

And instead of a flat endpoint name, you get:

.. code-block:: python

   url_for('recipes.ingredients.index', recipe_id=1)

That saves real mental energy later.

Now that the model naming is clear, we can look at the more interesting case:
when one controller name can describe more than one valid structure.
