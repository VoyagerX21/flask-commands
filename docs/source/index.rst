.. flask-commands documentation master file, created by
   sphinx-quickstart on Mon Jan  5 23:04:44 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

================
Flask-Commands
================

**Flask-Commands** is a local-first CLI tool that scaffolds Flask projects and keeps generating views, routes, controllers, and models for you so you can stay in flow.

.. toctree::
   :maxdepth: 3


Introduction
------------

Flask-Commands bundles a few opinionated conveniences:

- ``flask new`` bootstraps a ready-to-run Flask project with virtualenv, dotenv, Tailwind wiring, and optional SQLite + migrations.
- ``flask make:view`` generates HTML views and can optionally add controllers, routes/blueprints, and SQLAlchemy models to match.

The goal is to remove the repetitive setup work while keeping everything local and transparent.


Quick Start
-----------

.. code-block:: bash

   pip install Flask-Commands
   flask new myproject          # add --no-db if you want to skip SQLite/migrations
   cd myproject
   source venv/bin/activate
   flask run --debug            # or ./run.sh on macOS to open terminals + Tailwind watcher

Add a first page with controller and route wiring:

.. code-block:: bash

   flask make:view posts.index -cr
   flask make:view admin.users.show -cr   # nested example

Tailwind is installed automatically when ``npm`` is available; otherwise the tool skips it with a warning.


Command: ``flask new``
----------------------

After installing Flask-Commands globally you will have access to a new command 'flask' which will allow you to quickly scaffold out flask applications.  By running

.. code-block:: bash
   flask new myproject

You will create a folder called ``myproject`` and the folder will contain your new flask application with the following already setup. A virtual enviroment ``venv/`` with core Flask dependencies already installed and listed in``requirements.txt``. When you include ``--db`` (default unless ``--no-db``), it also installs ``Flask-Migrate``/``Flask-SQLAlchemy``, seeds a SQLite database, and runs the initial migration.

What you get:

- Blueprint-based app skeleton (``app/``),
- The projects entrypoint is ``run.py``.
- Configuration setup up under ``config/``,
- Tailwind-ready static pipeline under ``app/static/src/`` with npm scripts to watch/build CSS.
- Environment files ``.env`` and ``.env.example``
- One Blueprint defined in ``app/__init__.py`` called ``mains`` and the corresponding route set at ``app/routes/mains`` also called ``mains``.
- One Controller set up at ``app/controllers/main_controller`` called ``MainController``
- One ``Hello World`` view template under ``app/templates/mains/index.html``
- A macOS-friendly ``run.sh`` helper you start your application with a one line in the terminal.

.. code-block:: bash

   ./run.sh


Command: ``flask make:view``
----------------------------

Generates template files under ``app/templates/`` from dotted paths (e.g., ``posts.index`` -> ``app/templates/posts/index.html``). Optional flags wire up matching components:

- ``-c/--generate-controller`` or ``--controller NAME`` creates or extends the controller class.
- ``-r/--generate-route`` or ``--route PATH`` adds blueprint routes (CRUD verbs inferred when possible).
- ``-m/--generate-model`` or ``--model NAME`` seeds a SQLAlchemy model and import stub.

Examples:

.. code-block:: bash

   flask make:view button                    # view-only snippet
   flask make:view posts.index -crm          # view + controller + route + model
   flask make:view posts.show --route /posts/<int:post_id> --controller PostController
