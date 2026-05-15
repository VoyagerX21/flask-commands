make:model --crud
=================

Creating the model structure in an application is only the first step when 
building out a full application or application feature.

In the last section, we created a ``Recipe`` model, again 🫩.  This time 
however, we just focused on the model-only flow, not additional resources: 

- from model creation with ``flask make:model``, 
- to migration with ``flask db migrate -m 'message'`` and ``flask db upgrade``, 
- to testing with ``flask shell``.  
 

But most resources need more than a model. A recipe usually needs a controller,
routes, and templates so people can work with it in the browser.

So once the model structure is in place the next question is usualy how fast can 
you connect up the new model to the rest of your application so users can start
CRUDing with the new model.  You said it, we are going to bring back our old
controller option ``--crud`` in this new make model section.

Build a Resource with ``--crud``
--------------------------------

.. youtube_embed:: build-a-resource-with-make-model-crud


.. admonition:: Before you run this

   If you are following long from a prior part in this tutorial there is a 
   goog change that you already have a ``Recipe`` model in your project.

   To avoid warnings and to see the creation output from start to finish please
   spin up a fresh app with something like

   .. code-block:: bash

      flask new example_model_with_crud

If you already know you want the whole resource structure, add ``--crud``:

.. code-block:: bash

   flask make:model Recipe --crud

If you have been following along you will notice that this command build out 
the exact same files in the exact same structue as our following make controller
command:


That generates:
.. code-block:: bash

   flask make:controller RecipeController --crud -m

Both commands create the same general structure:

- a ``Recipe`` model
- a ``RecipeController``
- seven RESTful controller actions
- RESTful routes for ``recipes``
- templates for the ``GET`` actions
- model and controller registration

The difference is not the destination. The difference is where you start.

With ``make:controller``, you start with the controller name and ask
Flask-Commands to generate the model from it.

With ``make:model``, you start with the model name directly and ask
Flask-Commands to build the CRUD structure around it.

For a simple resource like ``Recipe``, both approaches are easy to read. But as
soon as the model name has more than one word, the model-first command starts to
feel much nicer.

Multiple Word Data Structure
-----------------------------
For example, suppose your application needs a ``ShoppingList`` model.

From the controller-first side, you have to be more explicit because
``ShoppingListController`` could be read in more than one way:

.. code-block:: bash

   flask make:controller ShoppingListController --crud --model ShoppingList

or:

.. code-block:: bash

   flask make:controller ShoppingListController --crud -m --flat

Both commands are valid, but they require you to explain how the controller name
should become a model.

From the model-first side, the command is simpler:

.. code-block:: bash

   flask make:model ShoppingList --crud

That reads almost exactly like the idea in your head:

   Make me a ``ShoppingList`` model, and build the CRUD resource around it.

That gives you the flat ``ShoppingList`` resource:

- model class: ``ShoppingList``
- model file: ``app/models/shopping_list.py``
- controller class: ``ShoppingListController``
- controller file: ``app/controllers/shopping_list_controller.py``
- route package: ``app/routes/shopping_lists/``
- template folder: ``app/templates/shopping_lists/``
- URL shape: ``/shopping-lists``

So in one command, you get the model plus the controller, routes, and views
that wrap around it.

Flask-Commands creates templates for ``GET`` actions, while ``POST`` actions
are wired without generating templates.

This is one of the reasons ``make:model --crud`` can be such a nice workflow.
If the data is the part you know first, the rest of the application structure
can grow outward from there.

And once the model-first CRUD workflow feels good, the next interesting
question is the same one we saw with controllers: should the structure be flat
or nested?
