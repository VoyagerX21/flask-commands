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
   * - ``flask make:view VIEW_NAME``
     - Create a template only (no wiring).
   * - ``flask make:view admin.reports.index -r``
     - Generate a route and optionally accept/decline missing-model creation prompt.
   * - ``flask make:view VIEW_NAME -rc``
     - Create a template and wire up a route + controller method.
   * - ``flask make:view VIEW_NAME -rcm``
     - Create a template and wire up route + controller + model (when it makes sense).
   * - ``flask make:controller RecipeCommentController -m --flat``
     - Infer model from controller name and force flattened generation.
   * - ``flask make:controller CONTROLLER_NAME --crud``
     - Create a controller, routes, and templates for the seven RESTful actions.
   * - ``flask make:controller CONTROLLER_NAME --crud -m``
     - Create a controller, routes, and templates for the seven RESTful actions, plus a model.
   * - ``flask make:model MODEL_NAME``
     - Create a model and register it in ``app/models/__init__.py``.
   * - ``flask make:model MODEL_NAME --crud``
     - Create a model plus RESTful controller, routes, and views.
   * - ``flask make:model RecipeComment --crud --nest``
     - Scaffold CRUD and force nested model generation.
