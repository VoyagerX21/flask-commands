make:controller Basics
======================

There are times when the controller is the best place to begin. Maybe you
already know the behavior your resource needs and just want the structure on
disk without writing the same pieces by hand again.

If you are newer to web development, a controller method is just Python code
that decides what response should be returned for a route.

A Simple Controller
-------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: Create a simple controller.*

Use ``flask make:controller`` to scaffold a controller class under
``app/controllers/`` and register it in ``app/controllers/__init__.py``.

.. code-block:: bash

   flask make:controller RecipeController

This creates:

- ``app/controllers/recipe_controller.py``
- an import in ``app/controllers/__init__.py``

And the controller starts out very simple:

.. code-block:: python

   class RecipeController:
       pass

If you are following this documentation from the beginning, you will probably
get a warning that ``RecipeController`` already exists. It does, and that is
fine. This simple example is really here so you can see the baseline before we
start turning on the more interesting flags.

Add RESTful Actions with ``--crud``
-----------------------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: Add RESTful actions with --crud.*

Life is all about the options and ``--crud`` is a very handy option.

This flag injects the seven RESTful actions into the controller file, creates
matching routes, and wires up templates for the ``GET`` actions.

Suppose our cooking app needs an ``Ingredient`` resource:

.. code-block:: bash

   flask make:controller IngredientController --crud

With the ``--crud`` flag you get:

- ``app/controllers/ingredient_controller.py`` with seven RESTful methods
- controller registration in ``app/controllers/__init__.py``
- a routes folder under ``app/routes/ingredients/``
- RESTful routes inside ``app/routes/ingredients/routes.py``
- blueprint registration in ``app/__init__.py``
- four templates under ``app/templates/ingredients/``:
  ``index``, ``show``, ``create``, and ``edit``

Templates are only created for the ``GET`` actions. The ``POST`` actions
(``store``, ``update``, and ``destroy``) wire the controller and route
behavior, but they do not generate templates.

That is one of the nice things about this command. You can start at the
controller layer and still get a lot of the surrounding structure built for
you.

Once the controller flow feels comfortable, the next question is how models
fit into that story.
