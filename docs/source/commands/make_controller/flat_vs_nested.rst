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

Flat or Nest with the ``-m`` Option
-----------------------------------

.. youtube_embed:: flat-or-nest-with-the-m-option

We have seen using the ``--crud`` flag builds RESTful scaffolding:

- controller methods
- route handlers
- templates for the ``GET`` actions

In addition we have seen the ``-m`` flag adds model generation to that 
process. That means this command:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud -m

asks Flask-Commands to generate model names from 
``RecipeIngredientController``.  In the prior chapter, we ran this command 
without the ``-m`` option and with ``Recipe`` as a registered model.  

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

Therefore, Flask-Commands can build out complicated data 
structures under multiple setups (a registered or not registered ``Recipe``).  
In addition, if the new data structure contains the name 
of an existing data structure, choose ``--flat`` and keep the words together 
as one model. However, if the controller name is describing a parent-child 
relationship, choose ``--nest`` and let that relationship show in the 
generated CRUD structure.  

Let's revisit a command we showed in the prior chapter and show how these new
options will shorten the command.


Choose Flat for One Multi-Word Model
------------------------------------

.. youtube_embed:: choose-flat-for-one-multi-word-model

In the previous chapter we used ``ShoppingListController`` as an example of a
controller whose model name needs more than one word.

A ``ShoppingList`` is one data structure. It is not a ``Shopping`` model with a
nested ``List`` model under it.

In that chapter, we solved the problem by naming the model directly:

.. code-block:: bash

   flask make:controller ShoppingListController --crud --model ShoppingList

That works because ``--model ShoppingList`` explicitly tells Flask-Commands
that ``ShoppingList`` should stay together as one model.

Without that instruction, ``Shopping`` could become a namespace and ``List``
could become the RESTful resource. That is not the story we want for a shopping
list.

Now that we have ``-m`` and ``--flat``, we can let Flask-Commands generate the
same model from the controller name:

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
- URL shape: ``/shopping-lists``

The rule to remember here is that ``--flat`` tells Flask-Commands that the 
words before ``Controller`` describe one data structure.

Build Nested Resources One Level at a Time
------------------------------------------

Now that ``ShoppingList`` is registered as one flat model, we can build nested
resources under it.

Suppose your cooking app wants to organize a shopping list by store, and then
track ingredients inside each store section.

That relationship looks like this:

.. centered:: ``ShoppingList -> Store -> Ingredient``

Build that relationship one level at a time:

.. code-block:: bash

   flask make:controller ShoppingListController --crud -m --flat
   flask make:controller ShoppingListStoreController --crud -m --nest
   flask make:controller ShoppingListStoreIngredientController --crud -m --nest

The first command creates the top-level flat resource:

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

Flask-Commands reads the second command like this:

- registered parent: ``ShoppingList``
- generated child: ``StoreIngredient``

So you get:

.. centered:: ``ShoppingList -> StoreIngredient``

not:

.. centered:: ``ShoppingList -> Store -> Ingredient``

That is why the build-up order matters. ``--nest`` uses the registered parent
chain and generates the remaining words as the next child. If you want
``Store`` to be its own parent in the chain, generate and register ``Store``
before you generate ``Ingredient`` under it.

This is the pattern to remember:

 Build nested resources in the same order you want Flask-Commands to understand
 them.

Each command registers the next model before the following command needs it.
Because every command includes ``--crud``, every level also receives its own
controller, routes, and templates.


This is one of those spots where the tool is trying to be honest rather than
magical. Sometimes a name can describe more than one good structure, and in
that moment the command lets you decide which story your app should tell.

The same flat-versus-nested decision shows up again from the model-first side,
and it is worth seeing from that direction too.