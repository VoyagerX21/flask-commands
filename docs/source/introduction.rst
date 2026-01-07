Introduction
============

Getting Started
---------------

Flask-Commands bundles a few opinionated conveniences:

- ``flask new`` bootstraps a ready-to-run Flask project with virtualenv, dotenv, Tailwind wiring, and optional SQLite + migrations.
- ``flask make:view`` generates HTML views and can optionally add controllers, routes/blueprints, and SQLAlchemy models to match.

The goal is to remove the repetitive setup work while keeping everything local and transparent.


Installation
------------
Flask Commands was designed to be installed globally on your machine so you can have access to create a new flask application in any folder you on your machine.

.. code-block:: bash

   pip install Flask-Commands


Quick Start
-----------

.. code-block:: bash

   flask new myproject          # add --no-db if you want to skip SQLite/migrations
   cd myproject
   source venv/bin/activate
   flask run --debug            # or ./run.sh on macOS to open terminals + Tailwind watcher

Add a first page with controller and route wiring:

.. code-block:: bash

   flask make:view posts.index -cr
   flask make:view admin.users.show -cr   # nested example

Tailwind is installed automatically when ``npm`` is available; otherwise the tool skips it with a warning.
