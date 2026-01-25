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

Now for the fun (and powerful) part of this package.  **First make sure you are
at the root of your new project.**

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

The issue is that this page does not appear anywhere in your application. You can’t just
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

This works great — but it’s a lot of typing 😵‍💫. Don’t worry,
generator flags to the rescue ``-r`` and ``-c`` (or combined as ``-rc``).

Adding a Route and Controller (Generators)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same result as above, using generator flags:

.. code-block:: bash

   flask make:view about -rc

Much shorter and easy to remember just think I need to wire this up
with a **route** (url) and have a **controller** (logic serving the route) to
serve the page.  So **route** is shortened to **r** and **controller** is
shortend to *c*

Nesting Views
~~~~~~~~~~~~~

The view naming convention uses dot notation to represent nested structures.
This is similar to how an ORM (object relational mapping, like SQLAlchemy) works.

If you want to create reusable component views, you might keep them in
a ``components`` directory. To nest your styled tages, just prefix the view name
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
generator flags.  In this case this is what you want because the files will be
called from within other view files.

In the ``about`` example above, where we added the route and controller generator
to wire up the page I would actually nest this in the ``mains`` folder to keep
my templates folder everything nice and tidy. In other words, I would use the command:

.. code-block:: bash

   flask make:view mains.about -rc

This will keep everything in a ``mains`` theme directory or class structure.

- creates ``app/templates/mains/about.html`` (new)
- adds an ``about`` method to the ``MainController`` class
  (``app/controllers/main_controller.py``) (happens with our without adding ``mains.``)
- updates the ``mains`` routes file
  (``app/routes/mains/routes.py``) with a ``GET`` route at ``/about`` (happens with our without adding ``mains.``)

I would have said this earlier, but we didn't know about nesting at the time (now we do).

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
- ``destroy`` (or ``delete`` — frankly, I would have called it *nuke* 😜)

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
- a ``RecipeController`` controller class to handle the logic of what is viewed

To create the index page and wire up the route, controller, and model:

.. code-block:: bash

   flask make:view recipes.index --route /recipes --controller RecipeController --model Recipe

This one (really lonnnnng....) command creates **five files** and updates **three more** 😮

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

Ha ha, you didn't think I was going to make you keep putting everything in ``mains`` did you?
Now you know why I wrote this package — that’s a *lot* to wire up just to get one
model-backed view.

But wait it get's better!!! The above is just to much to type so I shortened it be able to infer the **route**, **controller**, and **model** based off of the dotted name.  So the really long command just become:

.. code-block:: bash

   flask make:view recipes.index -rcm

If you use ``-r``, ``-c``, and ``-m`` (in any order), Flask-Commands assumes the
standard setup above and does exactly the same thing.

To create the ``show`` page for a single recipe, you could write:

.. code-block:: bash

   flask make:view recipes.show --route '/recipes/<int:recipe_id>' --controller RecipeController

Or, using the generators:

.. code-block:: bash

   flask make:view recipes.show -rc

Notice, we didn’t include ``-m`` here.  This is because the Recipe model
already exists. In this case, the only new file is the view template — the
route and controller class are updated to include the show logic.  If you
forgot and added the ``-m`` then you would have received a warning saying
that the recipe model already exists and was left alone (which is what you
want, expecally if you have gone in and made changes to the model to include
specific columns).

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
route under recipes, creates the RecipeCommentController, and builds the Comment
model. The key part of the story is that the comments blueprint gets registered
inside the recipes blueprint (in ``app/routes/recipes/__init__.py``). So weired
🤪, who would have thought to register a blueprint in another blueprint!!!!
That is one of the cool things I love about the Flask framework it's not
opinionated which gives you the freedom to try new things.  Ok your saying,
that's great but why would I do this?  By register the ``comments`` blueprint
in the ``recipes`` blueprint we get to use the dotted naming convention when
reference a route such as
``url_for('recipes.comments.index', recipe_id=1)``.

Again the above is a lot to type and I don't know that people will remember
all the formating.  Because I want to make everyone's life easier (myself
included) the generates come to save the day. Here is the shortened command
that produces the same behavior.

.. code-block:: bash

   flask make:view recipes.comments.index -rcm

Let’s dive a little deeper down this rabbit hole with another relationship.
Suppose that on our cooking website we allow users to upload images when they
make a comment.  Three level, what **Recipes → Comments → Images** that's
hurts my brain just thinking about it 🧐. Here is how I would think about this.


.. epigraph::

    Ok what do we need to have o have **Recipes → Comments → Images**? Let's see,
    we need a new **Image model**, an **image controller**, an **images blueprint**,
    and **images view** folder for file like create.html. O ya, and I want to
    make sure I wire up the blueprint in such a way that I get my dotted
    naming convention to work like so ``url_for('recipes.comments.images.something', recipe_id=#, comment_id=#)``


The cool thing that Flask-Commands does for you is handle the nesting for you.
In order to have the dotted naming convention we register the ``images`` blueprint
inside ``comments`` at ``app/routes/recipes/comments/__init__.py``, and ``comments`` is already
registered in ``recipes``, which is registered with the application. That chain
gives you natural dot notation (similar to SQLAlchemy’s relationships) when you
reference the view as ``recipes.comments.images``, so your ``url_for`` looks
like ``url_for('recipes.comments.images.index', recipe_id=1, comment_id=1)``.
Here is the simple command that sets everything up:

.. code-block:: bash

   flask make:view recipes.comments.images.index -rcm

That's it that is all you have to remember tell Flask-Commands that you want
a view and how the structure/relationship should look with dots and throw in
your generated flags of route -r, controller -c, and model -m (then preso 🪄
everything is built for you).  But wait, it get's better with controllers
because we can make multiple views with one command!!!!

flask make:controller
---------------------
A Simple Controller
~~~~~~~~~~~~~~~~~~~
Use ``flask make:controller`` to scaffold a controller class under
``app/controllers/`` and register it in ``app/controllers/__init__.py``.

.. code-block:: bash

   flask make:controller RecipeController

This creates ``app/controllers/recipe_controller.py`` with a class stub:

.. code-block:: python

   class RecipeController:
       pass

In fact, if you are following this tutorial from the beginning, you should receive a warning that this controller already exists. It does, and it's much better than a simple class with a ``pass``. So why would we use the ``make:controller`` command? You might create a new set of routes that you need a plain controller for the logic.  But I love flags so let's see some real magic come into play.

A Controller with RESTful actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's all about the options like ``--crud`` which will produce a controller with the whole set of seven RESTful actions, the routes, an the matching templates wired up for you.  For our cooking website suppose we need to have an object for 'ingredients'. Here is how we can wire up a ton of content ready to use right away with the following command:


.. code-block:: bash

   flask make:controller IngredientController --crud

With the ``--crud`` flag you will also receive:

- A controller file under ``app/controllers/ingredient_controller.py``  with all seven RESTful methods ready for you.
    - The controller file registered propertly in ``app/controllers/__init__.py``.
- A blueprint routes file under ``app/routes/ingredients``
    - The routes file contains all seven RESTful routes.
    - The new blueprint registered with the create_app in ``app/__init__.py``
- Four templates under ``app/templates/ingredients`` (``index``, ``show``, ``create``, ``edit``).

Here is what the controller file looks like.

.. code-block:: python

   from flask import render_template
   from flask import redirect, url_for

   class IngredientController:

       @staticmethod
       def index() -> str:
           return render_template('ingredients/index.html')

       @staticmethod
       def show(ingredient_id: int) -> str:
           return render_template('ingredients/show.html')

       @staticmethod
       def create() -> str:
           return render_template('ingredients/create.html')

       @staticmethod
       def store() -> str:
           return redirect(url_for('ingredients.index'))

       @staticmethod
       def edit(ingredient_id: int) -> str:
           return render_template('ingredients/edit.html')

       @staticmethod
       def update(ingredient_id: int) -> str:
           return redirect(url_for('ingredients.index'))

       @staticmethod
       def destroy(ingredient_id: int) -> str:
           return redirect(url_for('ingredients.index'))


Here is what that routes file looks like:

.. code-block:: python

   from app.controllers import IngredientController
   from app.routes.ingredients import bp

   @bp.route('/ingredients', methods=['GET'])
   def index():
       return IngredientController.index()

   @bp.route('/ingredients/<int:ingredient_id>', methods=['GET'])
   def show(ingredient_id: int):
       return IngredientController.show(ingredient_id)

   @bp.route('/ingredients/create', methods=['GET'])
   def create():
       return IngredientController.create()

   @bp.route('/ingredients', methods=['POST'])
   def store():
       return IngredientController.store()

   @bp.route('/ingredients/<int:ingredient_id>/edit', methods=['GET'])
   def edit(ingredient_id: int):
       return IngredientController.edit(ingredient_id)

   @bp.route('/ingredients/<int:ingredient_id>', methods=['POST'])
   def update(ingredient_id: int):
       return IngredientController.update(ingredient_id)

   @bp.route('/ingredients/<int:ingredient_id>/delete', methods=['POST'])
   def destroy(ingredient_id: int):
       return IngredientController.destroy(ingredient_id)

This is awesome!!! I can litterly see you jumping up and down shouting with
celebration for joy 🥳.  But wait, what about an **Ingrediant model**?

A Controller with Model
~~~~~~~~~~~~~~~~~~~~~~~

Often a controller is tied to a model like in your ingredient example.  You
have two options here you can either use an optional variable ``--model`` or
have Flask-Commands infer your model with a generator flag ``-m``.  The
following two commands are equivlant

.. code-block:: bash

   flask make:controller IngredientController --model Ingredient

and

.. code-block:: bash

   flask make:controller IngredientController -m

both will sub out a plain Ingredient controller class and an Ingrediant model.

Here is what the controller file looks like.

.. code-block:: python

    class IngredientController:
        pass


Here is what the model file looks like.

.. code-block:: python

    from app import db
    from datetime import datetime, timezone

    class Ingredient(db.Model):
        __tablename__ = 'ingredients'
        # Columns
        id = db.Column(db.Integer, primary_key=True)
        created_at = db.Column(db.DateTime(timezone=True),
                            index=True,
                            default=lambda: datetime.now(timezone.utc))
        updated_at = db.Column(db.DateTime(timezone=True),
                            default=lambda: datetime.now(timezone.utc),
                            onupdate=lambda: datetime.now(timezone.utc))

        def store_in_database(self):
            db.session.add(self)
            db.session.commit()

        def delete_from_database(self):
            db.session.delete(self)
            db.session.commit()

        def __repr__(self):
            """Model representation for Code Debugging"""
            return f'<Ingredient id:{self.id}>'

Ok now you are all set to combine these optional variables and create nested
datastructures, right 🤔?  What did I hear you say, you want all the RESTful
actions nested over multiple models!!!!  Ya, of course you want to connect a
recipe to it's ingrediants.

Ok Ok, you can nest...

A Controller Nesting with --crud
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If we wanted to build the relationship **Recipe → Ingrediant** Flask-Commands
is up for the task.  In this case we would PascalCase case (UppserCamelCase)
the controller and then add the crud flag as in this command:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud

With this small change you recieve a lot of structure benefits in your code.

- A controller file under ``app/controllers/recipe_ingredient_controller.py``  with all seven RESTful methods ready for you.
    - The controller file registered propertly in ``app/controllers/__init__.py``.
- A blueprint routes folder under ``app/routes/recipes/ingredients``
    - The routes file contains all seven RESTful routes.
    - The new ingredients blueprint registered in the recipes blueprint
- Four templates under ``app/templates/recipes/ingredients`` (``index``, ``show``, ``create``, ``edit``).


Here is what the controller file looks like.

.. code-block:: python

    from flask import render_template
    from flask import redirect, url_for

    class RecipeIngredientController:

        @staticmethod
        def index(recipe_id: int) -> str:
            return render_template('recipes/ingredients/index.html')

        @staticmethod
        def show(recipe_id: int, ingredient_id: int) -> str:
            return render_template('recipes/ingredients/show.html')

        @staticmethod
        def create(recipe_id: int) -> str:
            return render_template('recipes/ingredients/create.html')

        @staticmethod
        def store(recipe_id: int) -> str:
            return redirect(url_for('recipes.ingredients.index', recipe_id=recipe_id))

        @staticmethod
        def edit(recipe_id: int, ingredient_id: int) -> str:
            return render_template('recipes/ingredients/edit.html')

        @staticmethod
        def update(recipe_id: int, ingredient_id: int) -> str:
            return redirect(url_for('recipes.ingredients.index', recipe_id=recipe_id))

        @staticmethod
        def destroy(recipe_id: int, ingredient_id: int) -> str:
            return redirect(url_for('recipes.ingredients.index', recipe_id=recipe_id))

Here is what that routes file looks like:

.. code-block:: python

    from app.controllers import RecipeIngredientController
    from app.routes.recipes.ingredients import bp

    @bp.route('/recipes/<int:recipe_id>/ingredients', methods=['GET'])
    def index(recipe_id: int):
        return RecipeIngredientController.index(recipe_id)

    @bp.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>', methods=['GET'])
    def show(recipe_id: int, ingredient_id: int):
        return RecipeIngredientController.show(recipe_id, ingredient_id)

    @bp.route('/recipes/<int:recipe_id>/ingredients/create', methods=['GET'])
    def create(recipe_id: int):
        return RecipeIngredientController.create(recipe_id)

    @bp.route('/recipes/<int:recipe_id>/ingredients', methods=['POST'])
    def store(recipe_id: int):
        return RecipeIngredientController.store(recipe_id)

    @bp.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>/edit', methods=['GET'])
    def edit(recipe_id: int, ingredient_id: int):
        return RecipeIngredientController.edit(recipe_id, ingredient_id)

    @bp.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>', methods=['POST'])
    def update(recipe_id: int, ingredient_id: int):
        return RecipeIngredientController.update(recipe_id, ingredient_id)

    @bp.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>/delete', methods=['POST'])
    def destroy(recipe_id: int, ingredient_id: int):
        return RecipeIngredientController.destroy(recipe_id, ingredient_id)

If you are missing all the recipe_id's it's because you are missing the recipe
model.  From the top you would do

.. code-block:: bash

   flask make:controller RecipeController --crud -m

Notice the ``-m`` generator flag to create the Recipe Model, and then you would follow it with the command from above (probably with a model generator flag)

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud -m
