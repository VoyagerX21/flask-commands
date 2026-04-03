make:model --crud
=================

Sometimes creating the model is only the beginning. Once you know the data
structure you want, the next question is how fast you can connect it to the
rest of the application.

Build a Resource with ``--crud``
--------------------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: Build a resource with make:model --crud.*

If you already know you want the whole resource structure, add ``--crud``:

.. code-block:: bash

   flask make:model Recipe --crud

That generates:

- ``app/models/recipe.py``
- ``app/controllers/recipe_controller.py``
- ``app/routes/recipes/``
- ``app/templates/recipes/`` for the ``GET`` actions

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
