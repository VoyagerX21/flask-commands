Introduction
============

Getting Started
---------------

Flask-Commands is a productivity tool that adds a small set of **opinionated but
transparent** commands to your Flask workflow so you have consistent scaffolding,
convential route/controller/view wiring, nested resources handled cleanly, and
predictable project layout.

It focuses on removing repetitive setup work—project scaffolding, wiring views,
controllers, routes, and models while keeping everything local, readable, and
easy to customize.

Out of the box, Flask-Commands provides:

- ``flask new`` — bootstraps a ready-to-run Flask project, including:

  - an isolated virtual environment
  - dotenv support
  - Tailwind CSS wiring (when ``npm`` is available)
  - optional SQLite database with migrations (included by default; use ``--no-db`` to skip)

- ``flask make:view`` — generates HTML views and can optionally scaffold:

  - controllers
  - routes / blueprints
  - SQLAlchemy models
  - view templates
  - supports nesting (including interactive RESTful route/model prompts when using ``-r``)

- ``flask make:controller`` — generates controller files and can optionally scaffold:

  - controllers
  - RESTful routes / blueprints
  - SQLAlchemy models (explicit via ``--model`` or generated via ``-m``)
  - RESTful view templates
  - supports nesting and model-structure selection (interactive, ``--flat``, or ``--nest`` with ``-m``)

- ``flask make:model`` — generates SQLAlchemy models and can optionally scaffold:

  - controllers
  - RESTful routes / blueprints
  - SQLAlchemy models
  - RESTful view templates
  - supports nested model-structure selection with ``--crud`` (interactive, ``--flat``, or ``--nest``)


Safeguard: ``flask make:...`` commands only run from a Flask project root (the
current directory must include ``app/`` and ``run.py``).  This is to prevent
accidental file creation in the wrong directory.  Confession, I have done this
several times and the feeling is not fun 🤨 expecally on the cleanup.  While
``flask make:...`` can only run in a Flask project root directory ``flask new``
is runnable in any directory.

All generated code is plain python's lovable Flask framework—no hidden runtime
layers, no framework lock-in.
Every file is created on disk and meant to be opened, read, and edited directly.


Installation
------------

Flask-Commands is designed to be installed **globally**, allowing you to scaffold
new Flask applications from any directory on your machine.

.. code-block:: bash

   pip install Flask-Commands

Video Tutorial
~~~~~~~~~~~~~~

.. youtube_embed:: nrFk9fAaiII "Flask Commands - Part 1 - Installing"

Quick Start
-----------

Once you have installed **Flask-Commands** you are ready to use the new ``flask``
command anywhere in your terminal.  The first step is to create a new project.
Below I will create a project called *myproject* feel free to change this to your
awesome project name:

.. code-block:: bash

   flask new myproject
   cd myproject

Recommended (macOS)
~~~~~~~~~~~~~~~~~~~

On **macOS**, the recommended way to start your application is:

.. code-block:: bash

   ./run.sh

This single command brings your entire development environment online.

The ``run.sh`` script performs the following actions:

- activates the project virtual environment
- starts the Flask development server
- opens a Flask shell in a separate terminal
- starts watchers to rebuild both ``tailwind.css`` and ``tailwind.min.css``
- opens the project in Visual Studio Code
- launches Safari and navigates to the running web application

**Hot Reloading**

When you use ``run.sh`` hot reloading is enabled automatically and watches the following directories:

- ``templates/``
- ``controllers/``
- ``forms/``
- ``models/``
- ``routes/``

Any change made in these folders will **immediately trigger a browser reload**
in Safari—no manual refresh required. This allows you to edit backend logic,
HTML templates, or forms and see the results instantly.


Visual Studio Code Setup (macOS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For ``run.sh`` to open Visual Studio Code automatically, the ``code`` command must
be available in your shell.

To enable this in VS Code:

1. Open **Visual Studio Code**
2. Press ``Cmd + Shift + P`` to open the Command Palette
3. Search for and select:

   ::

      Shell Command: Install 'code' command in PATH

4. Restart your terminal

Verify the setup by running:

.. code-block:: bash

   code .

If Visual Studio Code opens the current directory, the setup is complete.


Alternative (Manual Startup)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you prefer to start the application manually (not using ``run.sh``) or are not on macOS, you can run:

.. code-block:: bash

   source venv/bin/activate
   flask run --debug

Video Tutorial
~~~~~~~~~~~~~~

.. youtube_embed:: _bFQ9TUULWA "Flask Commands – Part 2: Installing Your First Project"


Your New Project in Action
--------------------------

Once your application is running, you can begin adding pages and components
using ``flask make:view``.

Creating Your First View
~~~~~~~~~~~~~~~~~~~~~~~~

Start with something simple, like a static **About** page:

.. code-block:: bash

   flask make:view about

This creates an ``about.html`` template in your templates directory and that's it.
You are left to wire up the template 😢.  Don't worry that's why we have flags 🎉.
We will show this in more detail in the :ref:`Commands <commands>` section.
For now just check your templates folder and you should see the new ``about.html`` file.


Reusable Components
~~~~~~~~~~~~~~~~~~~

Views can also be used to create reusable UI components.

For example, to generate a button component:

.. code-block:: bash

   flask make:view components.buttons

This places the template under the ``components/`` directory, making it easy
to include across multiple pages while keeping your UI files organized.  Notice
the dot notation, in Flask-Commands for ``flask make:view`` dots translate
to folder structure while underscores translate to multi words.


Introducing Models
~~~~~~~~~~~~~~~~~~

As your application grows you will want more then just simple view files, you
will want to wire up a view to backend logic.  Flask-Commands provide simple
to remember generator flags that will scaffold and wire up all you backend
pieces.

The ``-c``, ``-r``, and ``-m`` flags allow you to automatically generate the
needed **controller** (c), **route** (r) and **model** (m) to propertly
render a view.

- ``-c`` — a controller method
- ``-r`` — a route and/or blueprint if needed
- ``-m`` — a SQLAlchemy model

For example, to create an index page backed by a ``Post`` model:

.. code-block:: bash

   flask make:view posts.index -crm

This generates:

- the HTML template
- a controller method
- a registered posts route and a URL of ``/posts``
- a corresponding ``Post`` model scaffold (boilerplate columns + helpers)


Nested Views and Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Just as views can be nested for UI organization, they can also be nested to
reflect **model relationships**.

For example, if posts have comments, you can scaffold a view for displaying
a single comment belonging to a post:

.. code-block:: bash

   flask make:view posts.comments.show -crm

This dot-notation translates directly into nested folders, URL paths, and
controller structure, making relationships in your application immediately
visible in the filesystem.


This section is meant to get you started quickly with ``flask make:view``.
For a deeper dive into flags, behavior, and examples, head over to the
:ref:`Commands <commands>` section.

Video Tutorial
~~~~~~~~~~~~~~

.. youtube_embed:: wDsC5OCgsgU "Flask Commands – Part 3: Your New Project in Action"
