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

CRUD Scaffolding (Optional)
---------------------------

Add ``--crud`` to generate a matching controller, routes, and views for the
seven RESTful actions.

.. code-block:: bash

   flask make:model Comment --crud

This uses the pluralized model name for the route group (``comments``) and
creates:

- ``app/controllers/comment_controller.py``
- ``app/routes/comments/`` with ``routes.py`` and ``__init__.py``
- ``app/templates/comments/`` with views for the GET actions

The generated routes cover:

- ``index`` (GET)
- ``show`` (GET)
- ``create`` (GET)
- ``store`` (POST)
- ``edit`` (GET)
- ``update`` (POST)
- ``destroy`` (POST)

Wrap-up
-------

Use ``flask make:model`` when you want a clean model scaffold, and add
``--crud`` when you want the full controller + routes + views wiring in one go.
