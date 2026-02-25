Scaffolding a New Project (flask new)
=====================================

After installing **Flask-Commands** globally, you’ll have access to a new
command called ``flask``, which lets you scaffolds a Flask application from
the terminal in less time then it takes to make a cup of tea.

To create a new project named ``myproject``, run:

.. code-block:: bash

   flask new myproject

Once the command completes, you’ll see a new directory called ``myproject/``.
This directory contains everything you need to get a Flask application up and
running.

Database option
---------------

``flask new`` includes database support by default.

To skip DB setup, use:

.. code-block:: bash

   flask new myproject --no-db

With default DB setup enabled, Flask-Commands installs DB-related packages,
creates ``app/models/``, and runs the initial migration/upgrade steps.
With ``--no-db``, those DB-specific pieces are skipped. A use case for this
is if you are developing a static site that does not customize the user's
experience.

What you get
------------

The generated project includes a clean, opinionated structure with sensible
defaults:

- A Python virtual environment ``venv/`` with core Flask dependencies
  pre-installed and listed in ``requirements.txt``.
- With default DB setup (that is, unless ``--no-db`` is used), the following are included:

  - Flask-Login
  - Flask-Migrate
  - Flask-SQLAlchemy
  - A seeded SQLite database with a users table
  - An initial migration already applied
- A Blueprint-based application skeleton under ``app/``, organized by
  responsibility:

  - **Model** ``app/models/`` Defining all your applications data
    models/structure along with their methods.
  - **View** ``app/templates/`` Containing all HTML templates (including
    macros/components) used by the application.
  - **Controller** ``app/controllers/`` Housing controller classes responsible
    for the logic to gather and serve the requested data.
  - **URL** ``app/routes/`` Declaring and naming URL paths and connects them
    to controllers.
- The project entry point at ``run.py``
- Centralized configuration files under ``config/``
- If npm is installed on your machine then a Tailwind ready static asset
  pipeline located at ``app/static/src/``, including npm scripts for watching
  and building CSS
- Environment configuration files:

  - ``.env``
  - ``.env.example``
- A default Blueprint named ``mains``, defined in ``app/__init__.py``

  - Routes located at ``app/routes/mains``
  - A controller at ``app/controllers/main_controller`` named
    ``MainController``
  - A starter “Hello World” template at
    ``app/templates/mains/index.html``
- A macOS-friendly helper script run.sh for starting the application with a
  single command:

.. code-block:: bash

   ./run.sh

You can review this structure directly in the Flask-Commands source by exploring
the files and folders under: ``flask_commands/project``.

When you come back to your project after closing everything down the
``./run.sh`` will quickly get you back up and and running quickly.

.. youtube_embed:: p4Fk141vAjc "Flask Commands – Part 6: How to Restart Your Project Quickly"
