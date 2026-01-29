Generating Views (flask make:view)
==================================

Now for the fun (and powerful) part of this package. **First make sure you are
at the root of your new project.** This is not a correncting behavioral
choice; it’s a life saving choice to make sure you don't create a ton of
files in the wrong location 😥.

The ``flask make:view`` command generates template files under
``app/templates/``. It supports *dot notation* for nested folders. For example,
``posts.index`` creates:

- ``app/templates/posts/index.html``

While creating template files is great fun templates themselve don’t do much on
their own unless they are rendered by a route and a controller class.  To
make that wiring easier, ``flask make:view`` includes optional generator flags:

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

Basic Example (No Dots)
-----------------------

Suppose you want an ``about`` view for your company:

.. code-block:: bash

   flask make:view about

That’s it — you now have a new template at ``app/templates/about.html``.

The issue is that this page does not appear anywhere in your application. You
can’t just type ``/about`` or ``about.html`` into the browser and expect it to
work because the view is not wired up to a route or controller class.

Adding a Route and Controller (Explicit)
----------------------------------------

To solve the above issue, we can explicitly tell the command to wire up a route
and controller class:

.. code-block:: bash

   flask make:view about --route /about --controller MainController

In this example, ``MainController`` is used because a fresh application ships
with a ``MainController`` and a blueprint named ``mains``.

This command:

- creates ``app/templates/about.html``
- adds an ``about`` method to the ``MainController`` class
  (``app/controllers/main_controller.py``)
- updates the ``mains`` routes file (``app/routes/mains/routes.py``) with a
  ``GET`` route at ``/about``

This works great — but it’s a lot of typing 😵‍💫.  Don’t worry, generator flags to the
rescue: ``-r`` and ``-c`` (or combined as ``-rc``).

Adding a Route and Controller (Generators)
------------------------------------------

The same result as above, using generator flags:

.. code-block:: bash

   flask make:view about -rc

Much shorter and easy to remember just think I need to wire this up
with a **route** (url) and have a **controller** (logic serving the route) to
serve the page.  So **route** is shortened to **r** and **controller** is
shortend to *c*

Video Tutorial
~~~~~~~~~~~~~~

.. youtube_embed:: 3uZEtSSAUzE "Flask Commands – Part 4: Adding a View (No Dot Notation)"


Nesting Views
-------------

The view naming convention uses dot notation to represent nested structures.
This is similar to how an ORM (object relational mapping, like SQLAlchemy)
works.

If you want to create reusable component views, you might keep them in a
``components`` directory. To nest your styled tages, just prefix the view name
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
generator flags. In this case this not wired up views is what you want because
the files will be called from within other view files.

In the ``about`` example above, where we added the route and controller
generator to wire up the page, I would actually nest this in the ``mains``
folder to keep my templates folder everything nice and tidy. In other words, I
would use the command:

.. code-block:: bash

   flask make:view mains.about --route /about -c

This will keep everything in a ``mains`` theme directory or class structure.

- creates ``app/templates/mains/about.html`` (new)
- adds an ``about`` method to the ``MainController`` class
  (``app/controllers/main_controller.py``) (happens with our without adding ``mains.``)
- updates the ``mains`` routes file
  (``app/routes/mains/routes.py``) with a ``GET`` route at ``/about`` (happens with our without adding ``mains.``)

I would have said this earlier, but we didn't know about nesting at the time (now we do).

Notice that if we wrote the command

.. code-block:: bash

   flask make:view mains.about -rc

Then we would have all the same behavior as above; however, the url would be ``/mains/about``.  This is by design as the infered generator flags will use your dot notation to sturucture your route and controller.

Video Tutorial
~~~~~~~~~~~~~~

.. youtube_embed:: r6NmtDCquoE "Flask Commands – Part 5: Nesting Views (Dot Notation & Folder Structure in Flask)"

Adding models (and why REST shows up here)
------------------------------------------

Nesting becomes essential when you start building out models.

For applications that use a database (SQLite, MySQL, PostgreSQL, …), views are
often tied directly to models. ``Flask-Commands`` follows the seven RESTful
actions; see :doc:`rest_actions` if you want a quick refresher.
