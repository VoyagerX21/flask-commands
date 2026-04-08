make:view Basics
================

Now for the fun part of this package 🎉

Before we do anything else, **make sure you are at the root of your new
project**. This is not a correctional behavioral choice. This is a life-saving
choice to make sure you do not create a ton of files in the wrong place 😥

The ``flask make:view`` command generates template files under
``app/templates/``. At its simplest, it just makes a view file. But it can
also help wire that view into your application with a route, a controller, and
even a model if you want to keep going.

That is one of the reasons I like this command so much: you can start small
and let the structure grow as your app grows.

When you are new to web development, it helps to think of these three pieces
like this: the route is the address, the controller is the logic, and the view
is the HTML the browser eventually sees. Flask-Commands helps wire those
pieces together so you do not have to build that plumbing from scratch every
time.

The optional generator flags are:

- ``-c / --generate-controller`` or ``--controller NAME``
  Creates or extends a controller **class** in your application.
- ``-r / --generate-route`` or ``--route PATH``
  Adds a blueprint route for the view. This works for simple pages and for
  RESTful actions too.
- ``-m / --generate-model`` or ``--model NAME``
  Seeds a SQLAlchemy model with boilerplate columns: ``id``, ``created_at``,
  and ``updated_at``.

Let’s ease into this one step at a time.

Create a Simple Template
------------------------

.. youtube_embed:: create-a-simple-template-with-flask-make-view

Suppose you want an ``about`` page for your company:

.. code-block:: bash

   flask make:view about

That’s it. You now have a new template at:

- ``app/templates/about.html``

Nice and simple 😌

No route.
No controller.
No model.
Just the file.

That may sound a little underwhelming at first, but sometimes that is exactly
what you want. Maybe you are making a basic page. Maybe you are sketching
something out. Maybe you just want the file on disk first and want to think
about the wiring after your coffee kicks in ☕️

The important thing to know is this: the template now exists, but it does
**not** appear anywhere in your application yet. You cannot just type
``/about`` into the browser and expect it to work, because the view has not
been wired up to a route or a controller.

Understand the ``mains`` Namespace
----------------------------------

.. youtube_embed:: understand-the-mains-namespace

Before we wire up that ``about`` page, we should talk about ``mains``.

Flask-Commands gives you a built-in namespace called ``mains`` for the main
document-style pages in your application. Think things like:

- landing page
- about page
- contact page
- terms page
- privacy page

In other words, the pages that feel like the “main” pages of the site.

There are a couple things to notice here:

- the template folder is ``mains`` with an ``s``
- the controller is ``MainController`` in the singular

That is by design.

So when you see something like:

.. code-block:: text

   app/templates/mains/
   app/controllers/main_controller.py
   app/routes/mains/

you are looking at the built-in organizing namespace Flask-Commands created
for those main document pages.

This is also why ``mains`` is a little special. It helps organize your
internal project structure, but it is **not** meant to be a public URL
segment.

So ``mains`` helps keep things tidy on disk, while the public URL can still
stay nice and clean.

Wire a Page Explicitly
----------------------

.. youtube_embed:: wire-a-page-explicitly

Now let’s wire up that ``about`` page.

If you already know exactly how you want the page wired, you can say so
directly:

.. code-block:: bash

   flask make:view about --route /about --controller MainController

In this example, ``MainController`` is a natural fit because a fresh
Flask-Commands project already ships with a ``MainController`` and a
``mains`` namespace.

This command:

- creates ``app/templates/about.html``
- adds an ``about`` method to ``MainController``
- updates the ``mains`` routes file with a ``GET`` route at ``/about``

So the pieces line up like this:

- route: ``/about``
- controller method: ``MainController.about()``
- view: ``app/templates/about.html``

A browser request for ``/about`` hits the route, the route calls the
controller method, and the controller renders the view.

This is the “say exactly what you mean” version of the command. Very clear.
Very direct. Very doctor emoji 👨‍⚕️

It also involves a little more typing.

Use Generator Flags
-------------------

.. youtube_embed:: use-generator-flags-with-make-view

Generator flags to the rescue and make this long command into a shortcut 🎉
with ``-r`` and ``-c`` (or even shorter by combining them as ``-rc``).

The same general result as above can be written like this:

.. code-block:: bash

   flask make:view about -rc

Here:

- ``-r`` means generate the **route**
- ``-c`` means generate the **controller**

Much shorter. Much easier to remember.

I think of it like this: if I want the page to actually work, I probably need
a **route** and a **controller**. So ``-rc`` becomes a nice little habit 😌

This is one of the small pleasures of the package. Once the naming conventions
are familiar, the short flags become very easy to remember.

Use ``mains`` Intentionally
---------------------------

.. youtube_embed:: use-mains-intentionally

Now let’s use the ``mains`` namespace on purpose.

Suppose you want that same ``about`` page to live under ``mains`` so your
templates stay a little more organized:

.. code-block:: bash

   flask make:view mains.about --route /about -c

This creates:

- ``app/templates/mains/about.html``

and also:

- adds an ``about`` method to ``MainController``
- updates the ``mains`` routes file with a ``GET`` route at ``/about``

This is a nice pattern because it keeps the template organized under
``mains``, but the route still stays clean at ``/about`` because you
explicitly told Flask-Commands the route you wanted.

Now compare that with this:

.. code-block:: bash

   flask make:view mains.about -rc

This time, because you did **not** explicitly provide the route,
Flask-Commands generates the route for you. And since ``mains`` is an
internal organizing namespace for main document pages, it does **not** become
part of the public URL.

So the URL is still:

- ``/about``

not:

- ``/mains/about``

That is an important distinction.

When you explicitly say:

.. code-block:: bash

   --route /about

you are in charge of the route.

When you rely on:

.. code-block:: bash

   -r

Flask-Commands generates the route for you, but it still respects the idea
that ``mains`` is an internal namespace and not a public URL segment.

That means dot notation can affect more than just the template path. It can
also shape the controller and route wiring around the page, while still
keeping the public URL clean for the ``mains`` namespace.

I would have said this earlier, but we did not know about ``mains`` yet. Now
we do 😎

A Quick Peek at Nested Views
----------------------------

.. youtube_embed:: a-quick-peek-at-nested-views

Dot notation also becomes handy when you want to organize reusable templates.

For example:

.. code-block:: bash

   flask make:view components.accordions
   flask make:view components.checkboxes
   flask make:view components.selects

These create:

- ``app/templates/components/accordions.html``
- ``app/templates/components/checkboxes.html``
- ``app/templates/components/selects.html``

Because we did not add any generator flags, these are just templates. That is
usually exactly what you want for partials, macros, or little reusable
building blocks.

So before we ever get into nested resources like ``recipes.comments.index``,
dot notation is already helping keep the template structure nice and tidy.

When ``make:view`` Is the Right Starting Point
----------------------------------------------

.. youtube_embed:: when-make-view-is-the-right-starting-point

A view-first workflow makes sense when the page is the clearest thing in your
head.

For example, maybe you know:

- you need an ``about`` page
- you need a ``contact`` page
- you want to create the template first and worry about wiring second
- you want to build outward from the page instead of starting from the model

That is where ``flask make:view`` really shines ☀️

It lets you start small and add structure only when you need it. You do not
have to jump straight into models, controllers, and RESTful actions just
because you wanted one page on disk before lunch.

And that matters because sometimes the simplest step really is the best step.

With the basic flow down, we can now talk about the smarter behavior hiding
behind the command.
