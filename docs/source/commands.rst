.. _commands:

Commands
========

flask new
---------

After installing **Flask-Commands** globally, you’ll have access to a new command called ``flask``, which lets you quickly scaffold Flask applications from the terminal.
To create a new project named myproject, run:

.. code-block:: bash

    flask new myproject

Once the command completes, you’ll see a new directory called ``myproject/``. This directory contains everything you need to get a Flask application up and running.

What you get:
~~~~~~~~~~~~~

The generated project includes a clean, opinionated structure with sensible defaults:

- A Python virtual environment ``venv/`` with core Flask dependencies pre-installed and listed in ``requirements.txt``.
- When using --db (enabled by default unless --no-db is specified), the following are also included:
    - Flask-Migrate
    - Flask-SQLAlchemy
    - A seeded SQLite database with a users table
    - An initial migration already applied
- A Blueprint-based application skeleton under ``app/``, organized by responsibility:
    - **Model** ``app/models/`` Defining all your applications data models/structure along with their methods.
    - **View** ``app/templates/`` Containing all HTML templates (including macros/components) used by the application.
    - **Controller** ``app/controllers/`` Housing controller classes responsible for the logic to gather and serve the requested data.
    - **URL** ``app/routes/`` Declaring and names URL paths and connects them to controllers.
- The project entry point at ``run.py``
- Centralized configuration files under ``config/``
- If npm is install on your machine then a Tailwind ready static asset pipeline located at ``app/static/src/``, including npm scripts for watching and building CSS
- Environment configuration files:
    - ``.env``
    - ``.env.example``
- A default Blueprint named ``mains``, defined in ``app/__init__.py``
    - Routes located at ``app/routes/mains``
    - A controller at ``app/controllers/main_controller`` named ``MainController``
    - A starter “Hello World” template at ``app/templates/mains/index.html``
- A macOS-friendly helper script run.sh for starting the application with a single command:

.. code-block:: bash

    ./run.sh

You can review this structure directly in the Flask-Commands source by exploring the files and folders under:
``flask_commands/project``

flask make:view
---------------

Generates template files under ``app/templates/`` from dotted paths (e.g., ``posts.index`` -> ``app/templates/posts/index.html``). Optional flags wire up matching components:

- ``-c/--generate-controller`` or ``--controller NAME`` creates or extends the controller class.
- ``-r/--generate-route`` or ``--route PATH`` adds blueprint routes (CRUD verbs inferred when possible).
- ``-m/--generate-model`` or ``--model NAME`` seeds a SQLAlchemy model and import stub.

Examples:

.. code-block:: bash

   flask make:view button                    # view-only snippet
   flask make:view posts.index -crm          # view + controller + route + model
   flask make:view posts.show --route /posts/<int:post_id> --controller PostController
