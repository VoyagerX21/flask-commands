Nested resources
================

To demonstrate a RESTful nesting, let’s suppose we are designing a cooking
website and you want to list all your recipes. That’s the ``index`` action.

This means we need:

- a ``recipes.index`` view
- a ``Recipe`` model
- a ``RecipeController`` controller class to handle the logic of what is viewed

To create the index page and wire up the route, controller, and model:

.. code-block:: bash

   flask make:view recipes.index --route /recipes --controller RecipeController --model Recipe

This one (really lonnnnng....) command creates **five files** and updates **three files** 😮

Created files
-------------

- ``app/templates/recipes/index.html`` — the recipes index view
- ``app/controllers/recipe_controller.py`` — the controller class
- ``app/routes/recipes/__init__.py`` — the recipes blueprint package
- ``app/routes/recipes/routes.py`` — the recipes routes file
- ``app/models/recipe.py`` — the Recipe model

Updated files
-------------

- ``app/controllers/__init__.py`` — registers ``RecipeController``
- ``app/models/__init__.py`` — registers ``Recipe``
- ``app/__init__.py`` — registers the recipes blueprint in ``create_app``

You didn't think I was going to make you keep putting everything in ``mains`` did you?
Now you know why I wrote this package — that’s a *lot* to wire up just to get one
model-backed view.

But wait, it get's better!! The above is just too much to type so Flask-Commands
can infer the **route**, **controller**, and **model** based off of the dotted
name. That means this really long command can be written as:

.. code-block:: bash

   flask make:view recipes.index -rcm

If you use ``-r``, ``-c``, and ``-m`` (in any order), Flask-Commands assumes the
standard setup above and does exactly the same thing.

Video Tutorial
~~~~~~~~~~~~~~

.. youtube_embed:: e_rhD1al8A4 "Flask Commands – Part 8: Our First RESTful View"

To create the ``show`` page for a single recipe, you could write:

.. code-block:: bash

   flask make:view recipes.show --route '/recipes/<int:recipe_id>' --controller RecipeController

Or, using the generators:

.. code-block:: bash

   flask make:view recipes.show -rc

Notice, we didn’t include ``-m`` here. This is because the Recipe model already
exists.  In this case, the only new file is the view template — the
route and controller class are updated to include the show logic.  If you
forgot to remove the ``-m`` then you would receive a warning saying
that the recipe model already exists and was left alone (which is what you
want, expecally if you have gone in and made changes to the model to include
specific columns).

Video Tutorial
~~~~~~~~~~~~~~

.. youtube_embed:: b9WqM3Wi1J8 "Flask Commands – Part 9: A Second RESTful View"

Nesting Models
--------------

This is where the package really shines ☀️! Let's continue with our cooking
website example and suppose we are going to allow users to make comments on
the recipes. This is a one-to-many relationship (a single recipe might have
many comments).

.. code-block:: bash

   flask make:view recipes.comments.index --route '/recipes/<int:recipe_id>/comments' --controller RecipeCommentController --model Comment

When you run that command, Flask-Commands sets up the nested comments view and
route under recipes, creates the RecipeCommentController, and builds the Comment
model. The key part of the story is that the comments blueprint gets registered
inside the recipes blueprint (in ``app/routes/recipes/__init__.py``).  So weired
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

Video Tutorial
~~~~~~~~~~~~~~

.. youtube_embed:: ar7tdbvqVSc "Flask Commands – Part 10: Nesting Relationships (Nested RESTful Routes in Flask)"

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

Video Tutorial
~~~~~~~~~~~~~~

.. youtube_embed:: 9PpSvadbKIc "Flask Commands – Part 11: Nesting Relationships 3 Levels Deep"
