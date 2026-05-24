Cheat Sheet
===========

Not every visit to the documentation needs to be a full lesson. Sometimes you
just want the command pattern, the flag, and a little reassurance that you are
not inventing a workflow that makes no sense.

Naming Conventions
------------------

- **Views** use dotted names and follow plural resource naming (for example,
  ``posts.comments.images.show`` or ``components.buttons``).
- **Controllers** use PascalCase (Upper CamelCase) and are singular, ending in
  ``Controller`` (for example, ``RecipeCommentController``).
- **Models** use PascalCase (Upper CamelCase) and are singular (for example,
  ``Recipe``, ``Comment``, ``Image``).

Common Patterns
---------------

.. list-table::
   :header-rows: 1

   * - Pattern
     - What it does
   * - ``flask new myproject``
     - Scaffold a new Flask project with a database and migrations.
   * - ``flask new myproject --no-db``
     - Scaffold a Flask project without the database packages, models, or migrations.
   * - ``flask make:view about``
     - Create a template only.
   * - ``flask make:view about -rc``
     - Create a template and wire a route and controller.
   * - ``flask make:view mains.about -rc``
     - Keep the template under ``mains`` while still generating the public route ``/about``.
   * - ``flask make:view recipes.index -rcm``
     - Start a recipe resource with a list page, route, controller, and model.
   * - ``flask make:view recipes.show -rc``
     - Add a detail page to the existing recipe resource.
   * - ``flask make:view recipes.create -rcm``
     - Add a ``GET`` action that renders a recipe form template.
   * - ``flask make:view recipes.store -rcm``
     - Add a ``POST`` action that wires behavior without creating a template.
   * - ``flask make:view recipes.comments.index -rcm``
     - Create a nested comments resource under recipes.
   * - ``flask make:controller RecipeController --crud``
     - Generate RESTful controller methods, routes, and templates for recipes.
   * - ``flask make:controller RecipeController -m``
     - Create the controller and infer a matching model from the controller name.
   * - ``flask make:controller ShoppingListController --crud --model ShoppingList``
     - Keep a multi-word model name together while generating RESTful scaffolding.
   * - ``flask make:controller RecipeIngredientController --crud -m --nest``
     - Force the nested model interpretation for a controller-first ``--crud`` flow.
   * - ``flask make:model Recipe``
     - Create and register a single model scaffold.
   * - ``flask make:model Recipe --crud``
     - Create the model and scaffold the controller, routes, and templates around it.
   * - ``flask make:model ShoppingList --crud --flat``
     - Force a flat RESTful structure for a model name that could also be nested.
   * - ``flask make:model RecipeIngredient --crud --nest``
     - Force a nested RESTful structure for a model name that could also be flat.