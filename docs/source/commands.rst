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
- ``-r/--generate-route`` or ``--route PATH`` adds blueprint routes (allows the the seven RESTful actions -- index, show, create, store, edit, update, destroy/delete).
- ``-m/--generate-model`` or ``--model NAME`` seeds a SQLAlchemy model and sets up a boiler plate columns id, created_at, updated_at.

Let's work throug a few examples starting with the basics and ended with nested relationships using RESTful actions.

No Dot Examples
~~~~~~~~~~~~~~~

Suppose you want an about view for your company:

.. code-block:: bash

    flask make:view about

That is it, you now have a new html file located at ``app/templates/about.html``.  This issue is that this page is not appearing in your application.  You can't just put ``about`` or ``about.html`` into the url and see the pages content because the page is not wired up to a route in your application.

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
The name value uses dot-notation to represent nested structures.  If you want to make several reusable component views you might want to keep those in a components directory.  To do this just put ``components.`` before the view name consider the following commands:

.. code-block:: bash

    flask make:view components.accordions
    flask make:view components.checkboxes
    flask make:view components.selects

These commands would make the following files ``accordions.html``, ``checkboxes.html``, and ``selects.html`` you might used these files to house reusable macros.  Notice that these views are not wired up to any controller and there is no route connection because we didn't specify any of the optional flags.

Adding Models
~~~~~~~~~~~~~
Nesting becomes essential when you want to start building out models.  So for those who create a Flask application with a database (any time SQLite, MySQL, PostgreSQL, ...) you will want to often create views related to your models.  For example you might want to make an admin view that shows all your users.  ``Flask-Commands`` follows the seven RESTful actions (index, show, create, store, edit, update, destroy or delete).

If you are new to these actions or just need a little refresher here is a review of what each is used for and the request method they use in terms of GETs and POSTs.  There are other Methods such as delete but the browser only understand GETs and POSTs.  I always thing of the browser cycle as a Get the Page Post your Form and then redirect to a new page to provide feedback of what was just posted. So the traditional steps are Get -> Post -> Redirect. We will look more closely at this when we discuss controllers.  For now just familarize yourself with the 7 actions (I allow for destory to be replaced with delete if you perfer delete instead of destory).  Frakely, I would have called it ``nuke`` 😜

**The Seven Restful Actions:**

.. table:: The Seven Restful Actions

   ======= ====== =========================== ======================================================================
   Action  Method URL Example                 Behavior
   ======= ====== =========================== ======================================================================
   index   GET    /users                      Shows all instances of a model
   show    GET    /users/<int:user_id>        Shows a single instance of a model
   create  GET    /users/create               Shows the page to create a new instance of a model
   store   POST   /users/create               The act of creating a new instance of a model (then redirects)
   edit    GET    /users/<int:user_id>/edit   Shows the page to edit an instance of a model
   update  POST   /users/<int:user_id>/edit   The act of editing an existing instance of a model (the redirecting)
   destory POST   /users/<int:user_id>/delete The aact of deleting an existing instance of a model (the redirecting)
   ======= ====== =========================== ======================================================================


So lets suppose I have a cooking website and I want to list all my recipes on the website.  In this case we would use the index action.  This means we need ``recipes.index`` view and this view needs to be linked to a Recipe model and there needs to be a RecipeController that handles all the different actions on the Recipe Model.  The index page is always a great starting point so to create the index page for our recipes and wire up the controller and model we would use the following command.

.. code-block:: bash

   flask make:view recipes.index --route /recipes --controller RecipeController --model Recipe

This one command is going to make 5 files and it is going to edit 3 other files!  I know crazy 😮

.. raw:: html

   <span style="text-decoration: underline;">Created Files:</span>


- ``app/templates/recipes/index.html`` The new view file when you can show off all your recipes.
-  ``app/controllers/recipe_controller.py`` The controller which will eventually house the logic for several methods.  For now it starts off with the one we just made ``index``
- ``app/routes/recipes/__init__.py`` Created routes directory at app/routes/recipes and name the route **recipes**
- ``app/routes/recipes/routes.py`` The route file for recipes where all the recipe related urls will live.  For now it has the one we just made which is a GET route with url **/recipes** and this route uses the RecipeController which as created above.
-  ``app/models/recipe.py`` The model file which contains all the column information, all model's methods, and all the model's relationship structures.

.. raw:: html

   <span style="text-decoration: underline;">Updated Files:</span>

- ``app/controllers/__init__.py`` The new RecipeController was just register with your controllers by adding it to the bottom of this file.
-  ``app/models/__init__.py``  The new Recipe model was just register with your models by adding it to the bottom of this file.
- ``app/__init__.py`` A new recipes blueprint was just added to the create_app function

Now you know why I wrote this package.  So many thing to wire up just to have one new model's view!  But wait it get's better!!! The above is just to much to type so I shortened it to

.. code-block:: bash

   flask make:view recipes.index -rcm

If you use the flag -r, -c, and -m (in any order) then Flask-Commands will understand that you want the standard setup above and do exactly the same thing as above.  Notice that you can just run all the flags together.

To make the show page that will show off a single recipe you are write it out

.. code-block:: bash

   flask make:view recipes.show --route /recipes/<int:recipe_id> --controller RecipeController

or you can use the generators and just write the command:

.. code-block:: bash

   flask make:view recipes.show -rc

Notice that in this case we didn't have to add the -m or --model option because we already created the model in the prior command.  Also in this example the only new file is the view files.  The wiring of the view file was all done with existing files.  In other words, the route was update with the show function and the RecipeController was updated with the show method.
