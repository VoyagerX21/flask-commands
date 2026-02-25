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

Nested model selection (with ``--crud``)
----------------------------------------

When a model name can be interpreted as nested (for example ``UserComment``),
Flask-Commands can prompt you to choose between flattened and nested generation:

.. code-block:: bash

   flask make:model UserComment --crud

You can skip the prompt with:

.. code-block:: bash

   flask make:model UserComment --crud --flat
   flask make:model UserComment --crud --nest

Rules:

- ``--flat`` and ``--nest`` are mutually exclusive.
- ``--flat`` and ``--nest`` require ``--crud``.


Wrap-up
-------

Use ``flask make:model`` when you want a clean model scaffold, and add
``--crud`` when you want the full controller + routes + views wiring in one go.
