Starting a Project
==================

Now that the command is available, let’s create a project. This is where
Flask-Commands starts doing real work for you instead of just sitting there
looking helpful.

Create a Project with ``flask new``
-----------------------------------

.. youtube_embed:: create-a-project-with-flask-new

The fastest way to begin is to scaffold a new project directory and move into
it.  First open a terminal and navigate to where you want the new project.  
Then type the follow where ``myproject`` is the name of your new project:

.. code-block:: bash

   flask new myproject
   cd myproject

This creates a Flask application scaffold in a new folder called
``myproject``.

What the Default Scaffold Gives You
-----------------------------------

.. youtube_embed:: what-the-default-scaffold-gives-you

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
starting structure that you can open, read, and build from right away.

Create a Project Without a Database
-----------------------------------

.. youtube_embed:: create-a-project-without-a-database

Sometimes you want the Flask structure without the database pieces. Introducing 
the optional flag ``--no-db``.

.. code-block:: bash

   flask new myproject --no-db

This gives you the same general Flask project structure above without the database
support, models, and migration setup.

That can be useful when:

- you are building a marketing site and not collect data
- you want to delay database decisions until later 
- you know the project does not need persistent data yet
- you have a very specific way of handling data collection and don't want to use MySql or SQLite

Run the New Project
-------------------

.. youtube_embed:: run-the-new-project

Once the project has been created, the recommended way to lauch 🚀 the application 
on macOS is:

.. code-block:: bash

   ./run.sh

This little helper script is meant to get you back up and running quickly. It 
brings the local development environment online without making you remember 
every step by hand.

The ``run.sh`` script performs the following actions:

- activates the project virtual environment
- starts the Flask development server
- opens a Flask shell in a separate terminal
- starts watchers to rebuild both tailwind.css and tailwind.min.css
- opens the project in Visual Studio Code
- launches Chrome and navigates to the running web application

Hot Reloading
~~~~~~~~~~~~~

Flask handles reloading of your server with ''--debug'' but not reloading of 
your web browser. In other words, you would need to refresh your browser 
every time you make a change to your application to see the new effect.  
However, when you use ``run.sh`` browser reloading is enabled automatically 
and watches the following directories:

- templates/
- controllers/
- forms/
- models/
- routes/

Any change made in these folders will **immediately trigger a browser reload** 
in Chrome—no manual refresh required. This allows you to edit backend logic, 
HTML templates, or forms and see the results instantly.

Please note, ``fswatch`` will need to be install on your machine in order for 
this to work.  To install ``fswatch`` you can use brew.

Visual Studio Code Setup (macOS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For ``./run.sh`` to open Visual Studio Code automatically, the code command 
must be available in your shell.

To enable this in VS Code:

#. Open Visual Studio Code

#. Press Cmd + Shift + P to open the Command Palette

#. Search for and select:

.. code-block:: bash

   Shell Command: Install 'code' command in PATH

#. Restart your terminal

#. Verify the setup by running the following in your terminal:

.. code-block:: bash
   
   code .

If Visual Studio Code opens the current directory, the setup is complete.

Alternative (Manual Startup)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you perfer to start up manually (not using ``run.sh``), or if you are not 
on macOS, the manual startup path is still available through the project 
virtual environment and the usual Flask run commands.

.. code-block:: bash
   
   source venv/bin/activate
   flask run --debug

With the project in place, the next step is understanding the small set of
rules that make the generators feel predictable.
