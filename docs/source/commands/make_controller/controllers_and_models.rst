Controllers and Models with make:controller
===========================================

Controllers usually exist because some kind of data needs to be shown,
updated, or organized. 

In the last chapter we introduced ``--crud`` which scaffold out a ton of 
structure in our controller, routes, and templates.  If fact it kind of 
treated the last segment like a data strcture.  However, it does not 
actually make the model class.  You will need to be explicit 
in or for Flask-Commands to make a model.  I did this by design, because when 
you make the model you have options.  Let's dive into when the controller class
should have an associated model and how that model should be generated.

Add a Model with ``--model`` or ``-m``
--------------------------------------

.. youtube_embed:: add-a-model-with-model-or-m

Often a controller is tied to a model. Flask-Commands gives you two ways method
to handle this connection.  


.. admonition:: Before you run this

   If you have been following the tutorial from the beginning, you will already
   have a ``RecipeController`` and a ``Recipe`` model in your project.

   My suggestion would be to spin up a fresh app with something like
   ``flask new example_two`` so you can see the creation output from start to
   finish.


The most direct method is to explicitly name the model using ``--model``:

.. code-block:: bash

   flask make:controller RecipeController --model Recipe

Alternatively, you can let Flask-Commands generate the model name 
for you from the controller name using the flag ``-m``:

.. code-block:: bash

   flask make:controller RecipeController -m

These two commands produce the same general result:

- a plain ``RecipeController``
- an ``Recipe`` model

The important difference is who chooses the model name.

With ``--model Recipe``, you choose the exact model name.  You could have called
it anything you want if you prefer plural model name this is your opportunity 
to make your model plurla with ``--model Recipes``.

On the other hand, with ``-m`` or ``--generate-model``, Flask-Commands reads 
the controller name and generates the model name as the prior segment before 
the word controller.  

The generation for a single word before ``Controller`` like ``RecipeController`` is
straight forward; however, when there are nested relationship producing multiple
words before ``Controller`` like ``REcipeIngredientController`` the story is more
interesting. 

Naming Nested Controllers by the Relationship
---------------------------------------------

.. youtube_embed:: naming-nested-controllers-by-the-relationship

Let's say our cooking app needs a new data structure, we are tired of 
making ``Recipe`` over and over again 🤪.  A Recipe has Ingredients so we need
the relationship **Recipe -> Ingredient**.

Go Nested with ``--crud``
-------------------------

.. youtube_embed:: go-nested-with-make-controller-crud

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

you end up with a nested route shape:

- ``/recipes/<int:recipe_id>/ingredients``

And instead of a flat endpoint name, you preserve the nesting with:

.. code-block:: python

   url_for('recipes.ingredients.index', recipe_id=1)

That saves real mental energy later.

Now we need to nest, build out all RESTful action, and generate a model with.
Now that the model naming is clear, we can look at the more interesting case:
when one controller name can describe more than one valid structure.
