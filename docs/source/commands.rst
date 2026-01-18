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

Now for the fun (and powerful) part of this package.  First make sure you are
at the root of your new project.

The ``flask make:view`` command generates template files under ``app/templates/``.
It supports *dot notation* for nested folders. For example, ``posts.index`` creates:

- ``app/templates/posts/index.html``

While creating template files is great fun templates themselve don’t do
much on their own unless they are rendered by a route and a controller
class. To make that wiring easier, ``flask make:view`` includes optional
generator flags:

- ``-c / --generate-controller`` or ``--controller NAME``
  Creates (or extends) a controller **class** in your application.
- ``-r / --generate-route`` or ``--route PATH``
  Adds blueprint routes and supports the seven RESTful actions:
  ``index``, ``show``, ``create``, ``store``, ``edit``, ``update``,
  ``destroy`` (or ``delete`` if you prefer).
- ``-m / --generate-model`` or ``--model NAME``
  Seeds a SQLAlchemy model with boilerplate columns:
  ``id``, ``created_at``, and ``updated_at``.

Let’s work through a few examples, starting with the basics and ending with
nested relationships using RESTful actions.

No Dot Examples
~~~~~~~~~~~~~~~

Suppose you want an ``about`` view for your company:

.. code-block:: bash

   flask make:view about

That’s it — you now have a new template at ``app/templates/about.html``.

The issue is that this page is not appearing in your application. You can’t just
type ``/about`` or ``about.html`` into the browser and expect it to work because
the view is not wired up to a route or controller class.

Adding a Route and Controller (Explicit)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To solve the above issue, we can explicitly tell the command to wire up a
route and controller class:

.. code-block:: bash

   flask make:view about --route /about --controller MainController

In this example, ``MainController`` is used because a fresh application ships
with a ``MainController`` and a blueprint named ``mains``.

This command:

- creates ``app/templates/about.html``
- adds an ``about`` method to the ``MainController`` class
  (``app/controllers/main_controller.py``)
- updates the ``mains`` routes file
  (``app/routes/mains/routes.py``) with a ``GET`` route at ``/about``

This works great — but it’s a lot of typing 😵‍💫. Don’t worry, in come the
generator flags ``-r`` and ``-c`` (or combined as ``-rc``).

Adding a Route and Controller (Generators)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same result as above, using generator flags:

.. code-block:: bash

   flask make:view about -rc

Much shorter and easy to remember just think i need to wire this up
with a **route** (url) and have the **controller** serve the page.  So
**route** is the **r** and **controller** is the *c*

Nesting Views
~~~~~~~~~~~~~

The view name uses dot notation to represent nested structures.

If you want to create reusable component views, you might keep them in
a ``components`` directory. To do this, just prefix the view name
with ``components.``:

.. code-block:: bash

   flask make:view components.accordions
   flask make:view components.checkboxes
   flask make:view components.selects

These commands create:

- ``app/templates/components/accordions.html``
- ``app/templates/components/checkboxes.html``
- ``app/templates/components/selects.html``

You might use these files to house reusable macros. Notice that these views are
*not* wired up to any controller class or route because we didn’t specify any
generator flags.

In the ``about`` example from Adding a Route and Controller (Generators) I
would actually nest this because ``mains`` has it's own folder in
templates.  To keep you templates folder nice and tidy I would have used
the command:

.. code-block:: bash

   flask make:view mains.about -rc

but we didn't know about nesting at the time (now we do).

Adding Models
~~~~~~~~~~~~~

Nesting becomes essential when you start building out models.

For applications that use a database (SQLite, MySQL, PostgreSQL, …), views are
often tied directly to models. ``Flask-Commands`` follows the seven RESTful
actions:

- ``index``
- ``show``
- ``create``
- ``store``
- ``edit``
- ``update``
- ``destroy`` (or ``delete`` — frankly, I would have called it ``nuke`` 😜)

If you’re new to these actions (or just need a refresher), here’s a quick review
of what each one does and which HTTP method it uses.

There *are* other HTTP methods (PUT, PATCH, DELETE), but browsers traditionally
only understand GETs and POSTs. I always think of the browser lifecycle as:

**Get → Post → Redirect**

You *get* the page, you *post* a form, and then you *redirect* to a new page to
give feedback about what just happened. We’ll look at this more closely when we
discuss controller classes. For now, just familiarize yourself with the seven
actions.

.. table:: The Seven RESTful Actions

   ======= ====== ============================= ============================================================
   Action  Method URL Example                   Behavior
   ======= ====== ============================= ============================================================
   index   GET    /users                        Show all instances of a model
   show    GET    /users/<int:user_id>          Show a single instance
   create  GET    /users/create                 Show the page to create a new instance
   store   POST   /users/create                 Create a new instance (then redirect)
   edit    GET    /users/<int:user_id>/edit     Show the page to edit an instance
   update  POST   /users/<int:user_id>/edit     Update an instance (then redirect)
   destroy POST   /users/<int:user_id>/delete   Delete an instance (then redirect)
   ======= ====== ============================= ============================================================

To demonstrate this let’s suppose you have a cooking website and you want to list all your recipes.
That’s the ``index`` action.

This means we need:

- a ``recipes.index`` view
- a ``Recipe`` model
- a ``RecipeController`` controller class to handle the actions

To create the index page and wire up the route, controller, and model:

.. code-block:: bash

   flask make:view recipes.index --route /recipes --controller RecipeController --model Recipe

This one command creates **five files** and updates **three more** 😮

Created files
^^^^^^^^^^^^^

- ``app/templates/recipes/index.html`` — the recipes index view
- ``app/controllers/recipe_controller.py`` — the controller class
- ``app/routes/recipes/__init__.py`` — the recipes blueprint package
- ``app/routes/recipes/routes.py`` — the recipes routes file
- ``app/models/recipe.py`` — the Recipe model

Updated files
^^^^^^^^^^^^^

- ``app/controllers/__init__.py`` — registers ``RecipeController``
- ``app/models/__init__.py`` — registers ``Recipe``
- ``app/__init__.py`` — registers the recipes blueprint in ``create_app``

Now you know why I wrote this package — that’s a *lot* to wire up just to get one
model-backed view.

But wait it get's better!!! The above is just to much to type so I shortened it to the command

.. code-block:: bash

   flask make:view recipes.index -rcm

If you use ``-r``, ``-c``, and ``-m`` (in any order), Flask-Commands assumes the
standard setup above and does exactly the same thing.

To create the ``show`` page for a single recipe, you could write:

.. code-block:: bash

   flask make:view recipes.show --route /recipes/<int:recipe_id> --controller RecipeController

Or, using the generators:

.. code-block:: bash

   flask make:view recipes.show -rc

Notice we didn’t include ``-m`` here because the model already exists. In this
case, the only new file is the view template — the route and controller class
are updated in place.  If you forgot and added the ``-m`` then you would have received a warning saying that the recipe model already exists and was left alone (which is what you want expecally if you have gone in and made changes to the model)

Nesting Models
~~~~~~~~~~~~~~

This is where the package really shines! Let's continue with our cooking website
example and suppose we are going to allow users to make comments on the recipes.
This is a one-to-many relationship (a single recipe might have many comments).
First let's write out the long command to understand what we need and then we
will provide the shortened version.

.. code-block:: bash

   flask make:view recipes.comments.index --route '/recipes/<int:recipe_id>/comments' --controller RecipeCommentController --model Comment

When you run that command, Flask-Commands sets up the nested comments view and
route under recipes, creates the RecipeCommentController, and seeds the Comment
model. The key part of the story is that the comments blueprint gets registered
inside the recipes blueprint (in ``app/routes/recipes/__init__.py``), which is
why you can reference the route as
``url_for('recipes.comments.index', recipe_id=1)``.

Here is the shortened command for the same thing:

.. code-block:: bash

   flask make:view recipes.comments.index -rcm

Let’s dive a little deeper down this rabbit hole with another relationship.
Suppose that on our cooking website we allow users to upload images when they
make a comment. In this case, we need a new Image model and an ``images``
blueprint. The cool thing that Flask-Commands does is register the ``images``
blueprint inside ``comments`` at
``app/routes/recipes/comments/__init__.py``, and ``comments`` is already
registered in ``recipes``, which is registered with the application. That chain
gives you natural dot notation (similar to SQLAlchemy’s relationships) when you
reference the view as ``recipes.comments.images``, so your ``url_for`` looks
like ``url_for('recipes.comments.images.index', recipe_id=1, comment_id=1)``.
Here is the simple command that sets everything up:

.. code-block:: bash

   flask make:view recipes.comments.images.index -rcm
