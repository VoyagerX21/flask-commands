Generating Models (flask make:model)
====================================

The ``flask make:model`` command seeds a SQLAlchemy model with a small, useful
starter shape: timestamps, helpers, and a registered import in
``app/models/__init__.py``.

Basic Example
-------------

.. code-block:: bash

   flask make:model Post

This generates:

- ``app/models/post.py`` with ``Post`` boilerplate
- an import entry in ``app/models/__init__.py``

If the ``__init__.py`` file is missing, the model still gets created, and you
will see a warning so you can register the import manually.

Model Contents
--------------

The file includes:

- ``id``, ``created_at``, and ``updated_at`` columns
- ``store_in_database`` and ``delete_from_database`` helpers
- a simple ``__repr__`` for debugging

CRUD Scaffolding and Nested Model Selection
-------------------------------------------

Add ``--crud`` to generate a matching controller, routes, and views for the
seven RESTful actions.

.. code-block:: bash

   flask make:model Recipe --crud

This creates:

- ``app/models/recipe.py``
- ``app/controllers/recipe_controller.py``
- ``app/routes/recipes/`` with ``routes.py`` and ``__init__.py``
- ``app/templates/recipes/`` for GET actions (``index``, ``show``, ``create``, ``edit``)

Prompt behavior for nested candidates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the model name can be interpreted as nested (for example
``RecipeIngredient`` with ``Recipe`` already registered), Flask-Commands prompts
for structure:

.. code-block:: text

   Detected nested model structure:
     1) (flat model) = RecipeIngredient
     2) (nest leaf model) = Ingredient
   Choose model structure (1/2, flat/nest) [1]:

If you choose flat (``1``/``flat``):

- Models generated: ``RecipeIngredient``
- Controller layer: ``RecipeIngredientController``
- Route layer: flat CRUD routes under ``/recipe-ingredients``
- View layer: ``app/templates/recipe_ingredients/``

If you choose nest (``2``/``nest``):

- Models generated: ``Ingredient`` (with existing ``Recipe`` as parent model)
- Controller layer: ``RecipeIngredientController``
- Route layer: nested CRUD routes under ``/recipes/<int:recipe_id>/ingredients``
- View layer: ``app/templates/recipes/ingredients/``

Skip the prompt with overrides:

.. code-block:: bash

   flask make:model RecipeIngredient --crud --flat
   flask make:model RecipeIngredient --crud --nest

Rules:

- ``--flat`` and ``--nest`` are mutually exclusive.
- ``--flat`` and ``--nest`` require ``--crud``.

Wrap-up
-------

Use ``flask make:model`` when you want a clean model scaffold, and add
``--crud`` when you want the full controller + routes + views wiring in one go.
