make:model Basics
=================

Sometimes the cleanest place to begin is the data itself. If the model is the
first thing you know for sure, ``flask make:model`` is a very nice place to
start.

If you are newer to web development, a model represents application data,
usually something stored in the database.

Make a Basic Model
------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: Make a basic model.*

The simplest model command looks like this:

.. code-block:: bash

   flask make:model Recipe

This generates:

- ``app/models/recipe.py``
- an import registration in ``app/models/__init__.py``

That is it. Nice and simple.

This command is especially useful when the data shape is the clearest thing in
your head and you want to start there before thinking about controllers,
routes, or views.

What the Model Includes
-----------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: What the model includes.*

The generated model includes a small but useful starter shape:

- ``id``
- ``created_at``
- ``updated_at``
- ``store_in_database``
- ``delete_from_database``
- a simple ``__repr__`` for debugging

That gives you a clean base to build from without pretending the model is
finished.

Edit the Model and Migrate the Database
---------------------------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: Edit the model and migrate the database.*

At some point you will want to add real columns to the model.

For example, you might update ``Recipe`` to include a ``name``:

.. code-block:: python

   name = db.Column(db.String(128), nullable=False)

Changing the Python model file does not change the database schema by itself.
That is why the migration step matters.

Once you update the model, generate a migration:

.. code-block:: bash

   flask db migrate -m "Add name to recipe"

Then apply it:

.. code-block:: bash

   flask db upgrade

That is the Flask-Migrate part of the workflow, and it is one of the reasons I
like the default project scaffold so much. Miguel Grinberg’s
`Flask-Migrate <https://flask-migrate.readthedocs.io/>`_ package is already
wired in for you.

One small note: this only applies to the default database-enabled project. If
you created the project with ``flask new myproject --no-db``, then the
database and migration pieces are intentionally not there.

Once the model exists, the next step gets more interesting: letting ``--crud``
build the rest of the resource around it.
