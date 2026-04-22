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
data is transfered from into object instances in your database. In other 
words, it is the part of the app where request behavior starts to take life.

A Simple Controller
-------------------

.. youtube_embed:: create-a-simple-controller

Use ``flask make:controller`` to scaffold a controller class under
``app/controllers/`` and register it in ``app/controllers/__init__.py``.

.. code-block:: bash

   flask make:controller RecipeController

This creates:

- ``app/controllers/recipe_controller.py``
- an import in ``app/controllers/__init__.py``

And the controller starts out very simple:

.. code-block:: python

   class RecipeController:
       pass


That might feel a little underwelmed at first, and honestly that is okay.

This command is showing you the smallest possible controller shape before we
start adding the more interesting structure on top of it with flags.

If you have been following this documentation from the beginning, you already 
created ``RecipeController`` earlier while working with ``flask make:view``. 
Because of this you are recieving  a warning in the terminal saying that 
``RecipeController`` already exists.

.. rst-class:: terminal-warning
.. code-block:: text

   ⚠️  Warning: Controller Already Exists
       - Controller File for RecipeController already exists
       - No changes were made

Don't be alarmed it you see this, this is **not a problem**.  It just means Flask-Commands is protecting the file that already exists instead
of overwriting it. 


Add RESTful Actions with ``--crud``
-----------------------------------

.. youtube_embed:: add-restful-actions-with-crud

Life is all about the options, and ``--crud`` is a very handy option.

This flag injects the seven RESTful actions into the controller file, creates
matching routes, and wires up templates for the ``GET`` actions.

Suppose our cooking app needs an ``Ingredient`` resource:

.. code-block:: bash

   flask make:controller IngredientController --crud

With the ``--crud`` flag you get:

- ``app/controllers/ingredient_controller.py`` with seven RESTful methods
- controller registration in ``app/controllers/__init__.py``
- a routes folder under ``app/routes/ingredients/``
- RESTful routes inside ``app/routes/ingredients/routes.py``
- blueprint registration in ``app/__init__.py``
- four templates under ``app/templates/ingredients/``:
  ``index``, ``show``, ``create``, and ``edit``

Templates are only created for the ``GET`` actions. The ``POST`` actions
(``store``, ``update``, and ``destroy``) wire the controller and route
behavior, but they do not generate templates.  If you would like a refresher 
on why ``POST`` routes do not need templates please check out why POST 
actions do not generate templates in the section
:ref:`No Template for POST Actions <no-template-for-post-actions>`.


That is one of the nice things about this command. You can start at the
controller layer and recieve a ton of the surrounding structure built for
you.

Why ``--crud`` Feels Like a Big Deal
------------------------------------

.. youtube_embed:: why-crud-feels-lika-a-big-deal

If you have been following along with ``flask make:view``, this is where
``flask make:controller`` starts to feel like a little bit of a party 🎉

With ``flask make:view``, building a RESTful resource usually means thinking
one action at a time. That can be very helpful when you are learning or if you 
just need a simple component of a resource.  When building one action at a time
you watch that action come to life with a route, controller method, and 
template all wired together.

But once that pattern clicks, typing the same idea seven times starts to feel
a extremely monotonous 🫩.

For the single command above we would have had to type the seven below commands 
to end up with the same result.

.. code-block:: bash

   flask make:view ingredients.index -rc
   flask make:view ingredients.show -rc
   flask make:view ingredients.create -rc
   flask make:view ingredients.store -rc
   flask make:view ingredients.edit -rc
   flask make:view ingredients.update -rc
   flask make:view ingredients.destroy -rc

In practice there are time when you need to scafold out  all the actions and 
there are time where you just need a single action.  You now have the tool set
to do both.



But once you understand that those seven actions belong together, this:

.. code-block:: bash

   flask make:controller IngredientController --crud

starts to feel amazing.

It is the same resource idea, just expressed at a higher level.

Instead of saying:

- make this action
- now make this action
- now make this action too

you are saying:

- this resource needs a real controller
- give me the standard RESTful shape
- wire the surrounding structure for me

That is the real magic of ``--crud``. It does not just save keystrokes. It lets
you think in terms of the whole resource instead of manually rebuilding the
pattern one action at a time.

Once the controller flow feels comfortable, the next question is how models
fit into that story.