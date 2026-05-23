.. _flat-vs-nested-with-make-model:

Flat vs Nested with make:model
==============================

Some model names describe one obvious structure. Others can describe more than one valid resource shape, and that is where this chapter gets interesting.

In the last chapter we used ``make:model`` with ``--crud`` to build a simple model-backed resource. That workflow is easy to read when the model is one word like ``Recipe``.

.. code-block:: bash

   flask make:model Recipe --crud

However, not every model name is this simple. As we have seen before, we might
have multiple words describing a single model, like ``ShoppingList``.  Other times, the words might describe a nested
relationship, like ``Recipe -> Ingredient``.

This chapter explains how ``make:model`` handles these multi-word scenarios from the model-first side.


Choose Flat or Nested with ``--crud``
-------------------------------------

.. youtube_embed:: choose-flat-or-nested-with-crud-for-make-model

In the prior chapter we saw that adding ``--crud`` to ``make:model`` instructs Flask-Commands to build the model and
then wires RESTful scaffolding around it.

In the last chapter you saw this with a simple one-word model, ``Recipe``.  In that case, there is only one structure choice. When you provide ``make:model`` with a multi-word segment we introduce a bit of ambiguity as we will see in the section.

If you are following this tutorial from the controller chapters,  this section will feel familiar as it mirrors the :ref:`Flat or Nest with the -m Option<flat-or-nest-with-the-m-option>`
section, but from the model-first side.

In the controller-first workflow, we explored the multi-segment controller with the following command:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud -m

This command asks Flask-Commands to create a controller, generate a model from the controller name, and wire RESTful scaffolding around the result.

The model-first approach version of the above command is shortened to:

.. code-block:: bash

   flask make:model RecipeIngredient --crud

This reads more directly:

   Make a ``RecipeIngredient`` model-backed resource and wire CRUD around it.

The command is easier to read and remember; however, the multi-word segments introduce a naming question.

- should the word segments stay together as one model?
- or should the route wiring show a parent-child relationship based on the word segments?

This uncertainty results in the following terminal prompt:

.. code-block:: text

   Detected nested model structure:
      1) (flatten model) = RecipeIngredient
      2) (nested model chain) = Recipe -> Ingredient
   Choose model structure (1/2, flat/nest) [1]:

In this case, Flask-Commands can create one flat model,
``RecipeIngredient``, or it can generate the nested model chain,
``Recipe -> Ingredient``.

If  ``Recipe`` is already registered, then the prompt becomes:

.. code-block:: text

   Detected nested model structure:
      1) (flatten model) = RecipeIngredient
      2) (nested leaf model) = Ingredient
   Choose model structure (1/2, flat/nest) [1]:

Now Flask-Commands recognizes ``Recipe`` as an existing parent model. The flat
choice still keeps ``RecipeIngredient`` together, but the nested choice only
needs to generate the missing child model, ``Ingredient``.

Skipping the Prompt with ``--flat`` or ``--nest``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. youtube_embed:: skipping-the-prompt-with--flat-or--nest

If you know which structure you want, you can skip the prompt by using either ``--flat`` or ``--nest``.

Choosing Flat for One Multi-Word Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. youtube_embed:: choosing-flat-for-one-multi-word-model

Use ``--flat`` when the words describe one model:

.. code-block:: bash

   flask make:model ShoppingList --crud --flat

.. admonition:: Make Controller Equivalence

   Recall this is the model-first equivalent of what we saw in  :ref:`Choose Flat for One Multi-Word Model<choose-flat-for-one-multi-word-model>` with the following command:

   - ``flask make:controller ShoppingListController --crud -m --flat``

In one command you end up with the flat ``ShoppingList`` resource, which is
fully wired up with a new controller, routes, and views.

- model class: ``ShoppingList``
- model file: ``app/models/shopping_list.py``
- controller class: ``ShoppingListController``
- controller file: ``app/controllers/shopping_list_controller.py``
- route package: ``app/routes/shopping_lists/``
- template folder: ``app/templates/shopping_lists/``
- URL shape: ``/shopping-lists``


Choosing Nest for a Parent-Child Resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. youtube_embed:: choosing-nest-for-parent-child-resource

Use ``--nest`` when the words describe a relationship:

.. code-block:: bash

   flask make:model RecipeIngredient --crud --nest

.. admonition:: Make Controller Equivalence

   That is the model-first equivalent of:

   - ``flask make:controller RecipeIngredientController --crud -m --nest``

In this one command you tell Flask-Commands to make an ``Ingredient`` model as a nested resource under ``Recipe`` and to wire RESTful resources around ``Ingredient``.

- model class: ``Ingredient``
- model file: ``app/models/ingredient.py``
- controller class: ``RecipeIngredientController``
- controller file: ``app/controllers/recipe_ingredient_controller.py``
- route package: ``app/routes/recipes/ingredients``
- template folder: ``app/templates/recipes/ingredients/``
- URL shape: ``/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>``


This happens independently of ``Recipe``.  If ``Recipe`` is not built then Flask-Commands also builds out the missing parent models, in addition to the child model, ``Ingredient``.  While this is helpful it does leave missing RESTful route resources for the parent resource as the CRUD behavior is only applied to the child model.  In order for ``Recipe`` to also have all the RESTful routes you would have run ``make:model`` on ``Recipe`` first before running ``make:model`` on the combined ``RecipeIngredient``.

.. admonition:: Why do we need to nest?

   You might ask, *'Why do we even need to nest I want an ``Ingredient`` model so why not just run ``flask make:model Ingredient --crud``?*

   The answer is, you can if you don't care about having routes that show the nested relationship. This approach would result in URLs like this

   - ``/recipes/<int:recipe_id>``
   - ``/ingredients/<int:ingredient_id>``

   instead of

   - ``/recipes/<int:recipe_id>``
   - ``/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>``


Use ``make:controller`` for Namespacing
---------------------------------------

.. youtube_embed:: use-make-controller-for-namespacing

Namespaces are different from nested models.

A namespace is not a data structure. It is an organizing prefix for part of the
application. Because of that, namespacing belongs more naturally to the
controller and route shape than to the model shape.

We saw this in
:ref:`Multi-Word Namespaces<make-controller-multi-word-namespaces>` and
:ref:`Public Pages and Private Tools<make-controller-public-pages-and-private-tools>`
with ``TestKitchenRecipeController``.

The important idea is that ``TestKitchen`` is not a model. It is a section of
the application where test kitchen users can manage recipes.

So if we want this structure:

.. centered:: ``TestKitchen / Recipe``

I would rely on ``make:model`` for the ``Recipe`` model and ``make:controller`` for the ``TestKitchen`` namespace.  In other words, I would use the following commands:

.. code-block:: bash

   flask make:model Recipe
   flask make:controller TestKitchenRecipeController --crud

The first command creates and generates the model ``Recipe``.

The second command creates a namespaced RESTful controller around the already
registered ``Recipe`` model.

Flask-Commands reads ``TestKitchenRecipeController`` like this:

- ``TestKitchen`` is the namespace
- ``Recipe`` is the registered model-backed resource
- ``Controller`` tells Flask-Commands this is controller structure

So the URL shape becomes:

- ``/test-kitchen/recipes``
- ``/test-kitchen/recipes/<int:recipe_id>``

There is no ``TestKitchen`` model, and there is no
``<int:test_kitchen_id>`` route parameter. ``TestKitchen`` is just the namespace
that organizes this part of the application.

Once the namespace exists, we can return to ``make:model`` when we are ready to add
children models as we will see in the next section.

Build Nested Resources One Level at a Time
------------------------------------------

.. youtube_embed:: build-nested-resources-one-level-at-a-time-make-model

Now let's build multiple child resources on top of our ``TestKitchen / Recipe``
structure.

Suppose test kitchen users need to manage recipe steps and tips before a recipe
is published.  In addition, suppose the public can only see a list of all the
published recipes and each view each individual recipe.

That overall structure looks like this for the test kitchen users:

.. centered:: ``TestKitchen / Recipe -> CookStep -> Tip``

for the publich the url looks like this

- ``/recipes`` all recipes
- ``/recipes/<int:recipe_id>`` an individual recipe

To build this out from start to finish in a new project I would use the following commands:

.. code-block:: bash

   flask make:model Recipe
   flask make:view recipes.index -rc
   flask make:view recipes.show -rc
   flask make:controller TestKitchenRecipeController --crud
   flask make:model TestKitchenRecipeCookStep --crud --nest
   flask make:model TestKitchenRecipeCookStepTip --crud --nest

The first command creates the top-level model

- registered model: ``Recipe``

The second and third commands build out the wired up views for showing all recipes and an individual recipe.

- controller: ``RecipeController``
- URL shape: ``/recipes``
- URL shape: ``/recipes/<int:recipe_id>``

The fourth command adds the RESTful actions around the  namespaced ``Recipe`` model:

- namespace: ``TestKitchen``
- registered model: ``Recipe``
- controller: ``TestKitchenRecipeController``
- URL shape: ``/test-kitchen/recipes``

Then we return to ``make:model`` for the first child model, ``CookStep``:

.. code-block:: bash

   flask make:model TestKitchenRecipeCookStep --crud --nest

Flask-Commands reads that command like this:

- namespace: ``TestKitchen``
- registered parent: ``Recipe``
- generated child model: ``CookStep``

So it builds:

- model: ``CookStep``
- controller: ``TestKitchenRecipeCookStepController``
- URL shape: ``/test-kitchen/recipes/<int:recipe_id>/cook-steps``

Then we add the next child model, ``Tip``:

.. code-block:: bash

   flask make:model TestKitchenRecipeCookStepTip --crud --nest

Now Flask-Commands sees both ``Recipe`` and ``CookStep`` as registered parents:

- namespace: ``TestKitchen``
- registered parents: ``Recipe`` and ``CookStep``
- generated child model: ``Tip``

So it builds:

- model: ``Tip``
- controller: ``TestKitchenRecipeCookStepTipController``
- URL shape: ``/test-kitchen/recipes/<int:recipe_id>/cook-steps/<int:cook_step_id>/tips``

The order matters.

If you skip the ``CookStep`` model generation and jump straight to:

.. code-block:: bash

   flask make:model TestKitchenRecipeCookStepTip --crud --nest

Flask-Commands does not know that ``CookStep`` should be a parent model to ``Tip``. Instead, it will read the
remaining words as one child model and generate ``CookStepTip``.

So the pattern is:

   Build the structure from the top down. Use ``make:controller`` for the
   namespace surface, then return to ``make:model --crud --nest`` when you are
   ready to add one additional child at a time.
