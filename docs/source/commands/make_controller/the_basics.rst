The Basics of make:controller
=============================


There are times when the controller is the best place to begin.

Maybe you already know the behavior your resource needs.  Maybe you are
thinking in terms of application logic before you are thinking about templates.
Maybe you have already learned the ``flask make:view`` workflow and now you
want to move one level higher.

That is really what ``flask make:controller`` is about.


If you are newer to web development, a controller method is just Python code
that decides what response should be returned for a route or it is where
data is transferred from into object instances in your database. In other
words, it is the part of the app where request behavior starts to take life.

A Simple Controller
-------------------

.. youtube_embed:: create-a-simple-controller

Use ``flask make:controller`` to scaffold a controller class under
``app/controllers/`` and register it in ``app/controllers/__init__.py``.

.. code-block:: bash

   flask make:controller RecipeController

Before we delve into what this command created, there are three naming
conventions worth noticing:

- Controllers always end with the word ``Controller``
- Controllers use ``PascalCase`` (also called Upper CamelCase)
- Controllers are singular, not plural

I intentionally lined up the naming style with Python class naming because,
at the heart of it, a controller is just a class.  Flask-Commands can handle
other naming conventions; however, throughout this tutorial series, I
will present controllers as singular and views as plural resources.

Now let's get back to what you just created.  The above command makes two
changes:

- ``app/controllers/recipe_controller.py``
- an import in ``app/controllers/__init__.py``

And the controller starts out very simple:

.. code-block:: python

   class RecipeController:
       pass


That might feel a little underwhelmed at first, and honestly that is okay.

This command is showing you the smallest possible controller shape before we
start adding the more interesting structure on top of it with flags.

.. admonition:: For those following along

   If you have been following this documentation from the beginning, you already
   created ``RecipeController`` earlier while working with ``flask make:view``.
   Because of this you are receiving a warning in the terminal saying that
   ``RecipeController`` already exists.

   .. rst-class:: terminal-warning
   .. code-block:: text

      ⚠️  Warning: Controller Already Exists
         - Controller File for RecipeController already exists
         - No changes were made

   Don't be alarmed if you see this, it's **not a problem**.  This warning
   means Flask-Commands is protecting the file that already exists instead
   of overwriting it.


Add RESTful Actions with ``--crud``
-----------------------------------

.. youtube_embed:: add-restful-actions-with-crud

Life is all about the options, and ``--crud`` is a very handy option.

This flag injects the seven RESTful actions into the controller file, creates
matching routes, and wires up templates for the ``GET`` actions.

Let's revisit the need to build the full ``Recipe`` resource in our cooking
app.

.. admonition:: Before you run this

   If you are following along from the beginning, ``RecipeController`` already
   exists. In order to avoid the the controller-already-exists warning from
   above I recommend spinning up a fresh project, something like

   .. code-block:: bash

      flask new example_controller_with_crud

   so you can see the full ``--crud``  output from
   start to finish.

.. code-block:: bash

   flask make:controller RecipeController --crud

With the ``--crud`` flag you get:

- ``app/controllers/recipe_controller.py`` with seven RESTful methods
- controller registration in ``app/controllers/__init__.py``
- a routes folder under ``app/routes/recipes/``
- RESTful routes inside ``app/routes/recipes/routes.py``
- blueprint registration in ``app/__init__.py``
- four templates under ``app/templates/recipes/``:
  ``index``, ``show``, ``create``, and ``edit``

Templates are only created for the ``GET`` actions. The ``POST`` actions
(``store``, ``update``, and ``destroy``) wire the controller and route
behavior, but they do not generate templates.  If you would like a refresher
on why ``POST`` routes do not need templates please check out why ``POST``
actions do not generate templates in the section
:ref:`No Template for POST Actions <no-template-for-post-actions>`.

That is one of the nice things about this command. You can start at the
controller layer and receive a ton of the surrounding structure built for
you.

Notice that this list does not include a model. The ``--crud`` flag builds the
RESTful controller, routes, and templates. If you want the command to create a
model too, use ``--model`` or ``-m``. We will look at that in the next chapter.

Why ``--crud`` Feels Like a Big Deal
------------------------------------

.. youtube_embed:: why-crud-feels-like-a-big-deal

If you have been following along with ``flask make:view``, this is where
``flask make:controller`` starts to feel like a party 🎉

With ``flask make:view``, building a RESTful resource means thinking
one action at a time. This is helpful when you are learning or if you
just need a simple component of a resource.  When building one action at a time
you watch that action come to life with a route, controller method, and
template all wired together.

In practice, I often only need one or two of the RESTful actions, like
``index`` and ``edit``. In this situation, ``flask make:view`` is a great
fit because it lets you build exactly what you need without generating the
rest of the resource.

However, there are also times when you already know you want the full
resource.  In these cases typing the same idea seven times is going to feel
extremely monotonous 🫩. In other words, for the single command above we
would have had to type the seven below commands to end up with the same result.

.. code-block:: bash

   flask make:view recipes.index -rc
   flask make:view recipes.show -rc
   flask make:view recipes.create -rc
   flask make:view recipes.store -rc
   flask make:view recipes.edit -rc
   flask make:view recipes.update -rc
   flask make:view recipes.destroy -rc

Please don't put yourself through this, you are likely to miss one! You now have
the tools to either produce just a few of the RESTful actions or you can
produce all seven with a single command.

Once you know that a resource is going to need all seven actions use the
command ``flask make:controller`` with the ``--crud`` flag.

.. code-block:: bash

   flask make:controller RecipeController --crud

In these cases you are going to feel like you have real superpowers 🦸‍♀️.

Both ``make:view`` and ``make:controller`` are able to build
the same resources; however, they do this in different ways.  Our new
``make:controller`` expresses the concept at a higher level.

Instead of scaffolding each action one by one, you are telling
Flask-Commands:

- this resource needs the full RESTful actions
- give it the standard RESTful shape
- wire the surrounding structure

That is the real magic of ``--crud``. It does not replace the smaller
step-by-step workflow. Instead it gives you another way to work when the
situation calls for it.

You now have both approaches at your hands:

- If you only need a few actions, ``flask make:view`` is the way to go
- If you want the whole RESTful resource, ``flask make:controller`` with
  ``--crud`` will save you time with a single command.

The choice is yours based on what your app needs.  Once the controller flow
feels comfortable, the next question is how models fit into that story.