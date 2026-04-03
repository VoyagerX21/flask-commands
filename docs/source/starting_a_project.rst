Starting a Project
==================

Now that the command is available, let’s create a project. This is where
Flask-Commands starts doing real work for you instead of just sitting there
looking helpful.

Create a Project with ``flask new``
-----------------------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: Create a project with flask new.*

The fastest way to begin is to scaffold a new project directory and move into
it.

.. code-block:: bash

   flask new myproject
   cd myproject

This creates a Flask application scaffold in a new folder called
``myproject``.

What the Default Scaffold Gives You
-----------------------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: What the default scaffold gives you.*

By default, ``flask new`` creates a ready-to-run project with database support
and a clear application structure.

The scaffold includes:

- a Python virtual environment
- a Flask application entry point
- configuration files
- routes
- controllers
- templates
- models
- Flask-Migrate wiring
- a default SQLite database setup
- a starter ``run.sh`` script

The entry point is the file Flask uses to start your application. In this
project, that file is ``run.py``.

The goal is not to hide Flask from you. The goal is to give you a clean
starting structure that you can open, read, and edit right away.

Create a Project Without a Database
-----------------------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: Create a project without a database.*

Sometimes you want the Flask structure without the database pieces. That is
exactly what ``--no-db`` is for.

.. code-block:: bash

   flask new myproject --no-db

This gives you the same general Flask project structure without the database
support, models, and migration setup.

That can be useful when:

- you are building a simple site
- you want to delay database decisions until later
- you know the project does not need persistent data yet

Run the New Project
-------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: Run the new project.*

Once the project has been created, the recommended way to start it on macOS is:

.. code-block:: bash

   ./run.sh

This helper script is meant to get you back up and running quickly. It brings
the local development environment online without making you remember every step
by hand.

If you are not using ``run.sh``, or if you are not on macOS, the manual path is
still available through the project virtual environment and the usual Flask run
commands.

How to Use This Documentation
-----------------------------

This documentation is written like a small class. You can read from top to
bottom, or you can jump around to the command family you care about.

The YouTube callout appears at the top of each teachable section:

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

That is there on purpose. The written docs are the source of truth, and the
videos are meant to act like little guided walk-throughs of that exact section.

With the project in place, the next step is understanding the small set of
rules that make the generators feel predictable.
