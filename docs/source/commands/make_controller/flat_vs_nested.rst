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
one of two options: ``--flat`` or ``--nest``. These options let you tell
Flask-Commands which model story the controller name should tell.

.. _flat-or-nest-with-the-m-option:

Flat or Nest with the ``-m`` Option
-----------------------------------

.. youtube_embed:: flat-or-nest-with-the-m-option

When you add the ``--crud`` flag you are telling Flask-Commands to build a
RESTful scaffolding for the data structure.  That means build:

- controller methods
- route handlers
- templates for the ``GET`` actions

In addition, we have seen that the  ``-m`` flag adds model generation to that
process. Putting this together means that the command:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud -m

asks Flask-Commands to generate model names from
``RecipeIngredientController`` with RESTful scaffolding.  In the prior
chapter, we ran this command without the ``-m`` option and with ``Recipe``
as a registered model.

If we run this command in a new project the generated model name from
``RecipeIngredientController`` can tell two different model stories:

- flat: ``RecipeIngredient``
- nested: ``Recipe -> Ingredient``

So Flask-Commands prompts you to choose.

The exact prompt depends on which models are already registered.

If ``Recipe`` is not registered yet, Flask-Commands sees multiple child-like
segments:

.. code-block:: text

   Detected multiple child like segments:
   Recipe, Ingredient
      1) (flatten resource model)  = RecipeIngredient
      2) (generate the following models) = Recipe, Ingredient
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
choice still generates ``RecipeIngredient``, but the nested choice only
generated the missing nested structure ``Ingredient``.

In both cases, ``-m`` is what creates the flat-or-nested question. Registered
models help Flask-Commands understand which words are already part of your app
and which words should be used to generate a model.

If you choose **flat**, Flask-Commands keeps the words together:

- model generated: ``RecipeIngredient``
- controller class: ``RecipeIngredientController``
- URL shape: ``/recipe-ingredients/<int:recipe_ingredient_id>``

If you choose **nested**, Flask-Commands builds the relationship:

- model story: ``Recipe -> Ingredient``
- controller class: ``RecipeIngredientController``
- URL shape: ``/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>``

You can skip the prompt with either ``--flat`` or ``--nest``:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud -m --flat
   flask make:controller RecipeIngredientController --crud -m --nest

Therefore, Flask-Commands can build out complicated data
structures under multiple setups (a registered or not registered ``Recipe``).
If the new data structure contains the name
of an existing data structure, choose ``--flat`` and keep the words together
as one model. Conversely, if the controller name is describing a parent-child
relationship, choose ``--nest`` and let relationship show in the
generated CRUD structure.

Let's revisit a command we showed in the prior chapter and used these new
options to shorten the command.

.. _choose-flat-for-one-multi-word-model:

Choose Flat for One Multi-Word Model
------------------------------------

.. youtube_embed:: choose-flat-for-one-multi-word-model

In the previous chapter we used ``ShoppingListController`` as an example of a
controller whose model name needs more than one word.

A ``ShoppingList`` is one data structure. It is not a ``Shopping`` model with a
nested ``List`` model under it.

In `Single Data Structures that are Multiple Words <controllers_and_models.html#single-data-structures-that-are-multiple-words>`__, we solved the problem by naming the model directly:


.. code-block:: bash

   flask make:controller ShoppingListController --crud --model ShoppingList

That works because ``--model ShoppingList`` explicitly tells Flask-Commands
that ``ShoppingList`` should stay together as one model.

Without that instruction, ``Shopping`` becomes a namespace and ``List``
becomes the RESTful resource, which is not the story we want for a
shopping list.

Now that we have ``-m`` and ``--flat``, we can let Flask-Commands generate
the multi-word model from the controller name:

.. code-block:: bash

   flask make:controller ShoppingListController --crud -m --flat

This command says:

- ``--crud``: build the RESTful controller, routes, and templates
- ``-m``: generate the model from the controller name
- ``--flat``: keep ``ShoppingList`` together as one model

The generated structure is flat:

- model class: ``ShoppingList``
- model file: ``app/models/shopping_list.py``
- controller class: ``ShoppingListController``
- route package: ``app/routes/shopping_lists``
- template folder: ``app/templates/shopping_lists``
- URL shape: ``/shopping-lists/<int:shopping_list_id>``

The rule to remember here is:

 To keep all the words before ``Controller`` together as one data structure
 use ``--flat`` with the ``-m`` generator flag.

Build Nested Resources One Level at a Time
------------------------------------------

.. youtube_embed:: build-nested-resources-one-level-at-a-time

Now that ``ShoppingList`` is registered as one flat model, we can build nested
resources under it.

Suppose your cooking app wants to organize a shopping list by store, and then
track ingredients inside each store.

That relationship looks like this:

.. centered:: ``ShoppingList -> Store -> Ingredient``

I recommend building the relationship one level at a time:

.. code-block:: bash

   flask make:controller ShoppingListController --crud -m --flat
   flask make:controller ShoppingListStoreController --crud -m --nest
   flask make:controller ShoppingListStoreIngredientController --crud -m --nest

As we have seen the first command creates the top-level flat resource:

- model: ``ShoppingList``
- controller: ``ShoppingListController``
- routes: ``/shopping-lists``

The second command sees ``ShoppingList`` as a registered parent and generates
the next child:

- parent model: ``ShoppingList``
- generated model: ``Store``
- controller: ``ShoppingListStoreController``
- routes: ``/shopping-lists/<int:shopping_list_id>/stores``

The third command now sees both ``ShoppingList`` and ``Store`` as registered
parents and generates the next child:

- parent models: ``ShoppingList`` and ``Store``
- generated model: ``Ingredient``
- controller: ``ShoppingListStoreIngredientController``
- routes: ``/shopping-lists/<int:shopping_list_id>/stores/<int:store_id>/ingredients``

It is tempting to think that ``--nest`` will always split every remaining word
into its own model, especially because earlier we saw that
``RecipeIngredientController --crud -m --nest`` can generate both ``Recipe``
and ``Ingredient`` when neither model exists yet.

But once ``ShoppingList`` is registered, Flask-Commands has a parent to anchor
the relationship. If you skip the middle command and run:

.. code-block:: bash

   flask make:controller ShoppingListController --crud -m --flat
   flask make:controller ShoppingListStoreIngredientController --crud -m --nest

Flask-Commands reads the second command as a multi-word data structure like
this:

- registered parent: ``ShoppingList``
- generated child: ``StoreIngredient``

So you get:

.. centered:: ``ShoppingList -> StoreIngredient``

not:

.. centered:: ``ShoppingList -> Store -> Ingredient``

There is one more shortcut you might be tempted to try. What if you skip
straight to the longest controller name?

.. code-block:: bash

   flask make:controller ShoppingListStoreIngredientController --crud -m --nest

If none of those models are registered yet, Flask-Commands has no registered
parent chain to anchor on. In that case, the nested choice generates each
segment as its own model:

.. centered:: ``Shopping -> List -> Store -> Ingredient``

That is probably not what you meant. A ``ShoppingList`` should be one
two-word data structure, not separate ``Shopping`` and ``List`` models.

Also notice that this command only creates one CRUD controller:
``ShoppingListStoreIngredientController``. The generated CRUD surface is for
the final nested resource, ``Ingredient``. It does not give you separate CRUD
controllers for ``Shopping``, ``List``, or ``Store``.

Flask-Commands uses the registered parents as an anchor and when you provide
the option ``--nest`` it then takes the remaining word segments that come
after the registered parent chain and combines them to generate the new
child resource. Consequently, if we want ``Store`` to be its own parent in
the chain, we have to build-up in order by generating and registering ``Store``
before generating ``Ingredient`` under it.

The takeaway pattern to remember is:

 Build nested resources one command at a time, from the top down. Run the parent
 resource command first, then run the next child resource command under that
 parent. Repeat this pattern for each child resource in the nested chain.

Each command registers the next model before the following command needs it.
Because every command includes ``--crud``, every level also receives its own
controller, routes, and templates.

Combine Namespaces with Nested Model Generation
-----------------------------------------------

.. youtube_embed:: combine-namespaces-with-nested-model-generation

You can combine namespaces, nested resources, CRUD scaffolding, and generated
models. The key is still to build the registered model chain in order.

In the previous chapter we introduced a multi-word namespace (review in
sections
:ref:`Multi-Word Namespace <make-controller-multi-word-namespaces>` and
:ref:`Public Pages and Private Tools <make-controller-public-pages-and-private-tools>`)
with ``TestKitchenRecipeController``. Let's keep using that idea and build a
deeper staff-only workflow inside the test kitchen namespace.

Suppose test kitchen users need to manage recipe steps and tips before a recipe
is published.

That relationship looks like this:

.. centered:: ``TestKitchen / Recipe -> CookStep -> Tip``

Start by creating the top-level model-backed resource:

.. code-block:: bash

   flask make:controller RecipeController --crud -m

.. admonition:: Public Index and Show Only Pages

   In a more realistic application, you would just create a view page showing
   all the recipes and a single recipe resource for the public using the
   following two commands.

   .. code-block:: bash

      flask make:view recipes.index -rcm
      flask make:view recipes.show -rc

Then create the test kitchen CRUD controller for the already existing
``Recipe`` model:

.. code-block:: bash

   flask make:controller TestKitchenRecipeController --crud

Now you can generate nested children inside the test kitchen namespace:

.. code-block:: bash

   flask make:controller TestKitchenRecipeCookStepController --crud -m --nest
   flask make:controller TestKitchenRecipeCookStepTipController --crud -m --nest

The first nested staff command sees:

- namespace: ``TestKitchen``
- registered parent: ``Recipe``
- generated child: ``CookStep``

So it builds:

- model: ``CookStep``
- controller: ``StaffRecipeCookStepController``
- routes: ``/test-kitchen/recipes/<int:recipe_id>/cook-steps``

The second nested staff command sees:

- namespace: ``TestKitchen``
- registered parents: ``Recipe`` and ``CookStep``
- generated child: ``Tip``

So it builds:

- model: ``Tip``
- controller: ``TestKitchenRecipeCookStepTipController``
- routes: ``/test-kitchen/recipes/<int:recipe_id>/cook-steps/<int:cook_step_id>/tips``

The rule is the same as before:

- namespaces come before the registered model chain
- registered models become parents
- ``--nest`` generates the next child
- ``--crud`` gives each controller its RESTful scaffolding

As you have already seen, order matters.

 First build the top-level model. Then
 add the namespaced controller around that model. Once the namespace is in place,
 generate each nested child one level at a time so the whole nested chain lives
 under that namespace.

That wraps up the controller-first path.  We started with the controller name,
used ``--crud`` when we wanted all the RESTful actions, used ``-m`` when we
wanted model generation, and used ``--flat`` and ``--nest`` when the
controller name carries more than one possible meaning.  The last part
was the key to let you choose whether Flask-Commands should keep words
together as one model or build a nested relationship from the registered
model chain.

Next we will look at the same choice from the model-first side. Instead of
starting with a controller name and asking for a model, we will start with a
model name and ask Flask-Commands to build the CRUD structure around it.