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

During the installation process you will be prompted to include a SQLite Database.

.. code-block:: bash

    Include a SQLite Database? [Y/n]:

If you press enter without typing anything the default setting of *yes* will apply.  If you type *n* and press enter then the project will load as normal; however, you will not get a models folder and a few python dependances will not be installed.  A use case for this is if you are developing a static site that does not customize the user's experience.




What you get
~~~~~~~~~~~~~

The generated project includes a clean, opinionated structure with sensible defaults:

- A Python virtual environment ``venv/`` with core Flask dependencies pre-installed and listed in ``requirements.txt``.
- When using --db (enabled by default unless --no-db is specified as an option with the new command), the following are also included:
    - Flask-Migrate
    - Flask-SQLAlchemy
    - A seeded SQLite database with a users table
    - An initial migration already applied
- A Blueprint-based application skeleton under ``app/``, organized by responsibility:
    - **Model** ``app/models/`` Defining all your applications data models/structure along with their methods.
    - **View** ``app/templates/`` Containing all HTML templates (including macros/components) used by the application.
    - **Controller** ``app/controllers/`` Housing controller classes responsible for the logic to gather and serve the requested data.
    - **URL** ``app/routes/`` Declaring and naming URL paths and connects them to controllers.
- The project entry point at ``run.py``
- Centralized configuration files under ``config/``
- If npm is installed on your machine then a Tailwind ready static asset pipeline located at ``app/static/src/``, including npm scripts for watching and building CSS
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

Now for the fun part and powerful part of this package.  Make sure you are at the root of your new project.  The ``flask make:view`` command is designed to generate template files under ``app/templates/`` which follows a dot paths for nexting folders (for example, ``posts.index`` will create the following file ``app/templates/posts/index.html``).  While creating template files is great fun they do not serve much purpose unless they are being used by a route and controller to render content and or specific application data.  To make this possible there are optional flags wire up so you can easly integergate your view files:

- ``-c/--generate-controller`` or ``--controller NAME`` creates or extends a controller class in your application.
- ``-r/--generate-route`` or ``--route PATH`` adds blueprint routes (allows the the seven RESTful actions (index, show, create, store, edit, update, destroy/delete) actions).
- ``-m/--generate-model`` or ``--model NAME`` seeds a SQLAlchemy model and sets up a boiler plate columns id, created_at, updated_at.

Let's work throug a few examples starting with the basics and ended with nested relationships using RESTful actions.

No Dot Examples
~~~~~~~~~~~~~~~

Suppose you want an about view for your company:

.. code-block:: bash

    flask make:view about

That is it, you now have a new html file located at ```app/templates/about.html```.  This issue is that this page is not appearing in your application.  You can't just put ```about``` or ```about.html``` into the url and see the pages content because the page is not wired up to a route in your application.

Adding a Route and Controller (Manually)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To solve the above issue we could have explicity told the command to wire up our new view with a route and controller using the following command:

.. code-block:: bash

    flask make:view about --route /about --controller MainController

In this example, I used ``MainController`` because the fresh application ships with a ``MainController`` and a *route* called ``mains``.  Consequently, the above command not only creates the ``about.html`` file in ``app/templates`` but it also adds an ``about`` method to the ``MainController``  located at ``app/controllers/main_controller.py``.  In addition, the command updates the ``mains`` ``routes.py`` file located at ``app/routes/mains/routes.py`` with a ``GET`` route named ``about`` using url ``/about``.  This is great but a lot of typing in the terminal 😵‍💫.  Don't worry in comes the route and controller generators flag ``-r`` and ``-c`` or as a combo ``-rc``.

Adding a Route and Controller (with Generators)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same files as above will be generate with the generators flags using the following command:

.. code-block:: bash

    flask make:view about -rc

Nesting Views
~~~~~~~~~~~~~
The name value used dot-notation for a nested structure.

.. code-block:: bash

   flask make:view button                    # view-only snippet
   flask make:view posts.index -crm          # view + controller + route + model
   flask make:view posts.show --route /posts/<int:post_id> --controller PostController
