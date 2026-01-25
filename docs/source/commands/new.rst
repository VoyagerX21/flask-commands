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

Database prompt
---------------

During the installation process you will be prompted to include a SQLite
Database:

.. code-block:: bash

   Include a SQLite Database? [Y/n]:

If you press enter without typing anything the default setting of *yes* will
apply. If you type *n* and press enter then the project will load as normal;
however, you will not get a models folder and a few python dependances will not
be installed. A use case for this is if you are developing a static site that
does not customize the user's experience.

What you get
------------

The generated project includes a clean, opinionated structure with sensible
defaults:

- A Python virtual environment ``venv/`` with core Flask dependencies
  pre-installed and listed in ``requirements.txt``.
- When using --db (enabled by default unless --no-db is specified as an option
  with the new command), the following are also included:

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
