GET vs POST for RESTful Actions
===============================

Now that we have talked through prompts, routes, models, and how
``flask make:view`` tries to help when the structure is a little unclear, we
need to stop and talk more about RESTFul actions and how the actions themselve 
can be partictioned into two distinct groups.

- Some actions exist to show a page in the browser.
- Other actions exist to make data changes, and then send the browser elsewhere.

Flask-Commands follows this structural flow. If the action is meant to
render a page, it makes sense to generate a template.  However, if the action 
is meant to process a data change, then generating a template file would 
actually be the wrong thing to create.

In this chapter we look at why:

- ``index``, ``show``, ``create``, and ``edit`` generate view templates
- while ``store``, ``update``, and ``destroy`` do not generate view templates
- how ``flask make:view`` follows the traditional browser flow

Once this clicks, a lot of the generated output starts to feel much more
predictable.

GET Actions Render Pages
------------------------

.. youtube_embed:: get-actions-render-pages

The ``GET`` actions in a RESTful resource are the actions that exist to show a
page.

That means:

- ``index``
- ``show``
- ``create``
- ``edit``

all make sense as template-backed views.

These are the actions where the browser is asking for a page to display.
So when Flask-Commands scaffolds one of these actions, it creates a view file
because the whole point of the action is to render something.

In controller terms, these actions usually return something like:

.. code-block:: python

   return render_template('recipes/index.html')

That is why a command like this:

.. code-block:: bash

   flask make:view recipes.create -rcm

creates a template file along with the related controller and route wiring.

POST Actions Change State
-------------------------

.. youtube_embed:: post-actions-change-state

The ``POST`` actions in a RESTful resource are doing a different job.

That means:

- ``store``
- ``update``
- ``destroy``

are not really page-rendering actions.

These actions are usually triggered by a form submission or some other user
interaction that application state changes. They create, update, or delete some
object in your database.

Because of that, Flask-Commands does not generate a template file for these
actions. The action is not supposed to display a page directly. It is supposed
to do some work and then send the browser to the next page.

In controller terms, these actions usually return something like:

.. code-block:: python

   return redirect(url_for('recipes.index'))

That is why a command like this:

.. code-block:: bash

   flask make:view recipes.store -rcm

do not create a template file they just wire up the route and controller.  

The Browser Flow
----------------

.. youtube_embed:: the-browser-flow

I always think of the normal browser lifecycle like this:

.. centered:: **Get -> Post -> Redirect**

First you ``GET`` a page so the browser has something to show.

Then you ``POST`` data back to the server when the user submits a form.

When the ``POST`` is finish it redirected to another page so the user can see 
the result.

That is why a ``create`` action and a ``store`` action belong together even
though they do not generate the same kinds of files.

- ``create`` shows the form
- ``store`` handles the submitted form
- ``index`` often shows the updated result after the redirect

A Real Example with ``recipes.create`` and ``recipes.store``
------------------------------------------------------------

.. youtube_embed:: a-real-example-with-recipes-create-and-recipes-store

Let's walk throught this concept slowly with and example.  Say you want to 
add a new recipe to our cooker site.

First, we show the page to ``create`` a new recipe so the user visits:

.. code-block:: text

   recipes.create

That is a ``GET`` action, so it makes sense to have a template such as:

.. code-block:: text

   app/templates/recipes/create.html

That page contains the form the user fills out.

Then the user press the save button which submits the form.  The submission is
sent to a ``POST`` route where you application processes the data:

.. code-block:: text

   recipes.store

At that point the browser is no longer asking for a page to display. It is
sending your application a bundle of incoming data and saying, more or less,
"here is everything for a new recipe, please check it and store it if it is
valid."

That is why ``store`` does not need its own template file. Its job is to review
the submitted data, decide whether it is valid, and then respond by telling the
browser where to go next.

After your application reviews the incoming data, it usually goes one of two
ways. If everything looks good, the object is created and the user gets an
all-good new object created 👍 outcome. If something is wrong or missing, the
user gets a warning ⚠️ telling them what needs to be fixed.

In the successful case the application creates the new recipe and usually
redirects the browser to:

.. code-block:: text

   recipes.index

That way the user can see the full list of recipes, including the new one they
just created.

In the case something is wrong or missing, the application usually redirects 
the user back to the ``create`` page so they can fix the form and try again.

So even though ``create`` and ``store`` are tightly connected, only one of them
exists to render a visible page. The other exists to process data and redirect
the browser to the next useful page.


No Template for POST Actions
----------------------------

.. youtube_embed:: no-template-for-post-actions

This is the part that can feel surprising at first.

You run a command like:

.. code-block:: bash

   flask make:view recipes.store -rcm

and you do not see a new template appear.

But that does not mean Flask-Commands skipped something.

It means Flask-Commands understood that ``store`` is a ``POST`` action and
generated the parts that actually belong to that action:

- route wiring
- controller wiring
- redirect behavior

In other words, no template was generated because no template was supposed to
exist for that action in the first place.

What GET vs Post Means When Using ``make:view``
-----------------------------------------------

.. youtube_embed:: what-get-vs-post-means-when-using-make-view

Try to remove: A quick way to think about it is this:

- GET a page
  - shows a page so you expect a template
- POST a from
  - is meant to process data, so expect route and controller wiring with a redirect 

In our example above these two commands are doing different kinds of work:

.. code-block:: bash

   flask make:view recipes.create -rcm
   flask make:view recipes.store -rcm


The ``create`` action scaffolds a page the browser can display, so it makes
sense for Flask-Commands to generate a template for it.

The ``store`` action scaffolds the behavior that handles incoming data, so it
does not need a template of its own.


Consequently, while ``store`` is closely tied to ``create``, its job is not to
render a page, but to process the submitted data and redirect the browser to
the next page.

Once you start thinking in those terms, the generated output from 
Flask-Commands for RESTful action feels less mysterious and more
predictable.

Now that the command behavior makes sense, let’s use it to build a real
resource.