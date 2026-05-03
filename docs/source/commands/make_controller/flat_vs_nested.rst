Flat vs Nested with make:controller 
===================================

Some controller names describe only one clear model shape. Others can describe
more than one valid data structure, and that is where this chapter gets
interesting.

In the last chapter we used ``-m`` in the simplest possible case:

.. code-block:: bash

   flask make:controller RecipeController --crud -m

That command works cleanly because ``RecipeController`` points to one obvious
model: ``Recipe``.

But not every controller name is that simple. In the last chapter we also saw
that longer names can carry different meanings:

- one data structure with a multi-word name
- a namespace that organizes part of the app
- a nested resource relationship

This chapter picks up from there. We already know that ``-m`` tells
Flask-Commands to generate model classes from the controller name. Now we need
to decide what kind of model shape Flask-Commands should generate when the name
could reasonably mean more than one thing.

To make that decision, Flask-Commands looks at the controller name segments and
compares them to the registered models. From there, it determines the possible
model-generation options. This is where you come in and guide the command with
one of two options: ``--flat`` or ``--nest``. They let you tell Flask-Commands
which model story the controller name should tell.

The ``-m`` Flag and the Flat or Nested Choice
--------------------------------------------

.. youtube_embed:: choose-flat-vs-nested-when-using-m

The ``--crud`` flag builds the RESTful scaffolding:

- controller methods
- route handlers
- templates for the ``GET`` actions

The ``-m`` flag adds model generation to that process. That means this command:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud -m

asks Flask-Commands to generate model names from ``RecipeIngredientController``.

That name can tell two different model stories:

- flat: ``RecipeIngredient``
- nested: ``Recipe -> Ingredient``

So Flask-Commands prompts you to choose.

The exact prompt depends on which models are already registered.

If ``Recipe`` is not registered yet, Flask-Commands sees multiple child-like
segments:

.. code-block:: text

   Detected multiple child like segments:
   Recipe, Ingredient
   1 (flatten resource model)  = RecipeIngredient
   2 (generate the following models) = Recipe, Ingredient
   Choose model structure (1/2, flat/nest): [1]:

In this case, the flat choice generates one model, ``RecipeIngredient``. The
nested choice generates two models, ``Recipe`` and ``Ingredient``.

If ``Recipe`` is already registered, the prompt changes:

.. code-block:: text

   Detected nested models:
   Recipe
     1) (flatten resource model) = RecipeIngredient
     2) (nested generated model) = Ingredient
   Choose model structure (1/2, flat/nest): [1]:

Now Flask-Commands recognizes ``Recipe`` as an existing parent model. The flat
choice still generates ``RecipeIngredient``, but the nested choice only needs
to generate ``Ingredient``.

In both cases, ``-m`` is what creates the flat-or-nested question. Registered
models help Flask-Commands understand which words are already part of your app
and which words still need generated models.

If you choose **flat**, Flask-Commands keeps the words together:

- model generated: ``RecipeIngredient``
- controller class: ``RecipeIngredientController``
- CRUD routes: ``/recipe-ingredients``

If you choose **nested**, Flask-Commands builds the relationship:

- model story: ``Recipe -> Ingredient``
- controller class: ``RecipeIngredientController``
- CRUD routes: ``/recipes/<int:recipe_id>/ingredients``

You can skip the prompt with either ``--flat`` or ``--nest``:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud -m --flat
   flask make:controller RecipeIngredientController --crud -m --nest

The important lesson is not that ``Recipe`` must already exist for the command
to work. Flask-Commands can generate missing models for you. The bigger lesson
is that if you want every level to have its own CRUD scaffolding, you should
build the resource tree in order.

This is one of those spots where the tool is trying to be honest rather than
magical. Sometimes a name can describe more than one good structure, and in
that moment the command lets you decide which story your app should tell.

The same flat-versus-nested decision shows up again from the model-first side,
and it is worth seeing from that direction too.