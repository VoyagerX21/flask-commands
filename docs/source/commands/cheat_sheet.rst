Cheat Sheet
===========

If you only remember one thing, remember this: you can type the long command,
or you can type the short command and get back to building your app.

Naming conventions
------------------

Flask-Commands assumes a few conventions. They are simple, and they save you
from surprises later.

- **Views** use dotted names and are pluralized by convention (for example,
  ``posts.comments.images.show`` or ``components.buttons``).
- **Controllers** use PascalCase (Upper CamelCase) and are singular, ending in ``Controller`` (for
  example, ``PostCommentImageController``).
- **Models** use PascalCase (Upper CamelCase) and are singular (for
  example, ``Post``, ``Comment``, ``Image``).

Common patterns
---------------

.. list-table::
   :header-rows: 1

   * - Pattern
     - What it does
   * - ``flask new myproject``
     - Scaffold a new Flask project with a database and migrations.
   * - ``flask new myproject --no-db``
     - Scaffold a Flask project without DB packages/models/migrations.
   * - ``flask make:view about``
     - Create a template only (no wiring).
   * - ``flask make:view recipes.index -rcm``
     - Create recipe index view + route + controller + model in one command.
   * - ``flask make:view recipes.ingredients.show -rcm``
     - Add a nested show template for ingredients under recipes and wire route + controller + model.
   * - ``flask make:view admin.recipes.comments.index -rc``
     - Generate a route + controller method and optionally accept/decline missing-model creation prompt.
   * - ``flask make:controller RecipeController --crud -m``
     - Scaffold full RESTful recipe controller/routes/views and create a recipe model.
   * - ``flask make:controller RecipeIngredientController --crud``
     - Scaffold nested RESTful ingredient routes/views under recipes.
   * - ``flask make:controller RecipeIngredientController -m --flat``
     - Infer model from controller name and forces flattened model generation.
   * - ``flask make:controller RecipeIngredientController -m --nest``
     - Infer model from controller name and forces nested model generation.
   * - ``flask make:model Ingredient``
     - Create and register a single ``Ingredient`` model scaffold.
   * - ``flask make:model Ingredient --crud``
     - Create and register a single ``Ingredient`` model scaffold plus RESTful controller, routes, and views.
   * - ``flask make:model RecipeIngredient --crud --flat``
     - Create ``RecipeIngredient`` and scaffold flat CRUD layers.
   * - ``flask make:model RecipeIngredient --crud --nest``
     - Create nested ``Ingredient`` model flow with nested CRUD routes/views.
