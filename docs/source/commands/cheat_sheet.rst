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
     - Scaffold a new Flask project.
   * - ``flask make:view VIEW_NAME``
     - Create a template only (no wiring).
   * - ``flask make:view VIEW_NAME -rc``
     - Create a template and wire up a route + controller method.
   * - ``flask make:view VIEW_NAME -rcm``
     - Create a template and wire up route + controller + model (when it makes sense).
   * - ``flask make:controller CONTROLLER_NAME --crud``
     - Create a controller, routes, and templates for the seven RESTful actions.
   * - ``flask make:controller CONTROLLER_NAME --crud -m``
     - Create a controller, routes, and templates for the seven RESTful actions, plus a model.
