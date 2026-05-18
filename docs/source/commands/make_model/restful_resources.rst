RESTful Resource with make:model
================================

Creating the model structure in an application is only the first step when 
building out a full application or application feature.

In the last section, we created a ``Recipe`` model, again 🫩.  This time, 
however, we just focused on the model-only flow: 

- createing the model with ``flask make:model``, 
- migration the database with ``flask db migrate -m 'message'`` and 
  ``flask db upgrade``, 
- testing the model in ``flask shell``.  
 
This is a greate workflow when you are testing out a new data structure.  
However, most resources need more than a model. For example, a recipe will 
need a controller, routes, and templates so people can work with it in the 
browser.  

Otherwise, the model is shouting with a megaphone 📣 saying, "Hey is there 
anyone out there? I'm ready to CRUD."  Which is why I decided to bring back 
our controller option ``--crud`` in this new make model section.

Build a Resource with ``--crud``
--------------------------------

.. youtube_embed:: build-a-resource-with-make-model-crud

In the event that you want to build a new model structure and you already know
that you are going to need the full RESTful resource structure you can just
add one optional flag to get everything built out at once.

.. admonition:: Before you run this

   If you are following long from earlier chapters, there is a 
   good chance that you already have a ``Recipe`` model in your project.

   To avoid warnings and to see the creation output from start to finish please
   spin up a fresh app with something like

   .. code-block:: bash

      flask new example_model_with_crud

By adding add ``--crud`` to our prior make command we end up with so much 
more then just a single model file.  

Let's try it out with the following:

.. code-block:: bash

   flask make:model Recipe --crud

For me this is the natural way I think about these structures and from this one 
short command I end up with the following structure:

- a ``Recipe`` model
- model registration in ``app/models/__init__.py``
- a ``RecipeController``
- controller registration in ``app/controllers/__init__.py``
- seven RESTful controller actions
- RESTful routes for ``recipes``
- blueprint registration for the new route directory
- templates for the ``GET`` actions

That is a lot of typing you did not have to type. I am personally a big fan of
not typing the same boilerplate seven times while pretending I am having fun.

If you have been following along this will look familiar.  You have actually 
already seen a command in the make controller chapters that built out these 
exact same files with this exact same structue:

.. code-block:: bash

   flask make:controller RecipeController --crud -m

The difference is not the destination. The difference is where you mentally 
start.

With ``make:controller``, you start thinking from the machanics of the object 
(controller name) and ask Flask-Commands to generate the model from it.

With ``make:model``, you start thinking from the object (model name) and ask 
Flask-Commands to build the CRUD structure around it.

Neither one is more correct. They are just different doors into the same house.
And yes, I would absolutely rather have multiple doors 🚪 than crawl through a
window 🪟 like a stressed-out raccoon 🦝. Wait, no. Ignore the raccoon 🤪. The 
point is doors are good.

For a simple resource like ``Recipe``, both approaches are easy to read. But as
soon as the model name has more than one word or become nested, the 
model-first command starts to feel much nicer.

Multi-Word Data Structures
--------------------------

Recall, in :ref:`Single Data Structures that are Multiple Words<single-data-structures-that-are-multiple-words>` from the make controller chapters we created a signal data structure, ``ShoppoingList``, that consisted of two words.

In this chapter we created this structue by explicitly defining the models name using the following command:

.. code-block:: bash

   flask make:controller ShoppingListController --crud --model ShoppingList

However, later we saw that we could allow Flask-Commands to generate the model name and use the flat flag like so:

.. code-block:: bash

   flask make:controller ShoppingListController --crud -m --flat

Both commands are valid, but they require you to explain how the controller name
should become a model.

From the model-first side, the command is simpler:

.. code-block:: bash

   flask make:model ShoppingList --crud

For me this is the ideal way of designing, and reads as:

   Make  a ``ShoppingList`` model, and build the CRUD resource around it.

That gives you the flat ``ShoppingList`` resource:

- model class: ``ShoppingList``
- model file: ``app/models/shopping_list.py``
- controller class: ``ShoppingListController``
- controller file: ``app/controllers/shopping_list_controller.py``
- route package: ``app/routes/shopping_lists/``
- template folder: ``app/templates/shopping_lists/``
- URL shape: ``/shopping-lists``

So in one command, you end up with the new model plus the controller, routes, and views
that wrap around it.

For me ``make:model --crud`` is such a natural way of building out
resources.  I can quickly build out new models and wire them into the application.  I don't have to worry about multi-word models it all just works.  

But what about model relationships like we had with ``make:controller``?  This is actually where things get interesting.

 When every segment of a Model Name is not a registered model you
 will generate a multi-word model.  

This is one of the reasons ``make:model --crud`` can be such a nice workflow.
If the data is the part you know first, the rest of the application structure
can grow outward from there.

And once the model-first CRUD workflow feels good, the next interesting
question is the same one we saw with controllers: should the structure be flat
or nested?
