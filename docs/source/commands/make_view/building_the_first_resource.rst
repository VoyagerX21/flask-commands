Building the First Resource with make:view
==========================================

Now that we have looked at prompts and generator flags, we are ready to build 
something that feels like a real part of an application. 

We will start with ``recipes.index`` because it is one of the clearest ways to
see how Flask-Commands can scaffold a resource instead of just a template.

We are still going to keep the templates intentionally plain. The point here
is not to build a pretty website. The point is to see how the route,
controller, view, and model come together without wiring each piece by hand.

Build ``recipes.index``
-----------------------

.. youtube_embed:: build-recipes-index-as-the-first-resource

Let’s start by building the first real resource page for our recipe app:

.. code-block:: bash

   flask make:view recipes.index -rcm

This is a great first resource because it gives us something familiar and
useful right away: a page to list all recipes.

That one command creates and wires quite a bit:

- a view template for ``recipes.index``
- a controller method
- a route
- a model

That is where the command starts to shine ✨

Instead of making one file and then wiring the rest by hand, you get a real
working slice of the application structure in one compact command that is easy
to remember.

Understand What ``-rcm`` Created
--------------------------------

.. youtube_embed:: understand-what-rcm-created

Let’s break that command down:

- ``-r`` generates the **route**
- ``-c`` generates the **controller**
- ``-m`` generates the **model**

So with:

.. code-block:: bash

   flask make:view recipes.index -rcm

you should expect to see structure like:

- ``app/templates/recipes/index.html``
- ``app/controllers/recipe_controller.py``
- ``app/routes/recipes/__init__.py``
- ``app/routes/recipes/routes.py``
- ``app/models/recipe.py``

and the related registration updates needed to connect those pieces into the
app.

If you are new to RESTful naming, think of ``index`` as the page that list
all the instances of a single object.  This pages is a great place to start 
when building a new object because it keeps the focus on the core pieces 
working together:

- the route handles the URL namespace for requesting this object
- the controller is the logic that connects the model to the view
  - It gets all the instances from the model (the data)
  - It sends that data to the view
- the view renders the response to the user

Now that we have seen how the resource fits together, let’s look at building
the ``show`` page, a detail view for a single recipe.

Add ``recipes.show``
--------------------

.. youtube_embed:: add-recipes-show-to-the-resource

Once the resource exists, adding another RESTful page is much lighter.

For example:

.. code-block:: bash

   flask make:view recipes.show -rc

Notice that we did **not** use ``-m`` here.

That is because the ``Recipe`` model was already created in the earlier
command:

.. code-block:: bash

   flask make:view recipes.index -rcm

So now we only need to add:

- the ``show`` template
- the ``show`` controller method
- the ``show`` route

This is a nice moment in the workflow because it shows the resource starting
to grow naturally. You do not need to keep regenerating the same model once it
already exists. Flask-Commands can keep building on the structure that is
already there.

Why ``show`` Matters
--------------------

.. youtube_embed:: why-recipes-show-matters

The ``index`` page shows many recipes.

The ``show`` page shows one recipe.

That may sound obvious, but it is worth saying out loud because this is where
RESTful actions start feeling practical instead of theoretical.

With just these two commands:

.. code-block:: bash

   flask make:view recipes.index -rcm
   flask make:view recipes.show -rc

you now have the start of a resource that can:

- list all recipes
- show one specific recipe
- follow a clear route/controller/view pattern
- tie back to a real model

That is a lot of structure from very little typing, which is exactly the kind
of trade I like.

Keep the Templates Intentionally Plain
--------------------------------------

.. youtube_embed:: keep-the-templates-intentionally-plain

At this point, it can be tempting to start decorating everything.

Resist the urge 😄

Or at least resist it for now.

The point of this documentation is to show how Flask-Commands helps you build
the structure of the application quickly. So the templates in this section
should stay plain on purpose.

That means:

- basic HTML is fine
- simple layout is fine
- almost ugly is fine
- the important thing is seeing how the files connect

If the templates become too fancy, they start stealing attention from the real
lesson, which is how the data structure and application layers fit together.

Flask-Commands is here to make your life easier when building structure. It is
not here to win a beauty pageant 💃

Wrap-Up
-------

With these two commands:

.. code-block:: bash

   flask make:view recipes.index -rcm
   flask make:view recipes.show -rc

you now have the beginning of a real resource.

That means:

- the model exists
- the controller exists
- the routes exist
- the views exist
- the structure is starting to feel like an actual application

That is a big step.

With ``recipes.index`` and ``recipes.show`` in place, you have now seen the
basic shape of a resource and two of its page-rendering actions.

That naturally leads to the next question: why do some RESTful actions generate
templates while others do not?

To answer that, we need to look at the difference between ``GET`` actions that
render pages and ``POST`` actions that process data and redirect the browser.
