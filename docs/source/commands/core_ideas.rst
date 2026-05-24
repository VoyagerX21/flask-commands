Core Ideas
==========

Flask-Commands gets much easier once you understand the small set of rules it
follows.

This chapter is here to make the rest of the documentation feel predictable
instead of mysterious. In other words: fewer surprises, clearer structure, and
more time building your app instead of wondering why a command behaved the way
it did.

Project-Root Safety
-------------------

.. youtube_embed:: project-root-safety

The ``make:*`` commands are designed to run from a Flask project root.

These commands are exposed through Flask’s CLI plugin system, but they are still
meant to be run from your project root once a Flask application exists.

In practice, that means Flask-Commands expects to find:

- ``app/``
- ``run.py``

in the same directory where you run ``flask make:*``.

That safeguard exists to prevent accidental file creation in the wrong
directory. True confession: the reason I built this safeguard is because I
accidentally ran the ``flask make:*`` in the wrong place several times, resulting
in many minutes of not-so-fun cleanups 🤨.  So there is now a safeguard on
the commands for myself and others.

The one exception here is ``flask new``, which can be run from anywhere because
its job is to create the project root for you before an application exists.


RESTful Actions
---------------

.. youtube_embed:: restful-actions

Flask-Commands follows the seven RESTful actions.

- ``index``
- ``show``
- ``create``
- ``store``
- ``edit``
- ``update``
- ``destroy`` (or ``delete`` if you prefer — frankly, I would have called it
  ``nuke`` 😜)

If you’re new to these actions, or just need a refresher, here’s a quick review
of what each one does and which HTTP method it uses.

There are other HTTP methods like ``PUT``, ``PATCH``, and ``DELETE``, but
browsers traditionally only understand ``GET`` and ``POST``. I always think of
the browser lifecycle as:

.. centered:: **Get -> Post -> Redirect**

You get the page, you post a form, and then you redirect to a new page to give
feedback about what just happened.  In chart form these are the seven RESTful
actions.  This helped me, and I hope it will do the same for you.

.. table:: The Seven RESTful Actions

   ======= ====== ============================= ============================================================
   Action  Method URL Example                   Behavior
   ======= ====== ============================= ============================================================
   index   GET    /users                        Show all instances of a model
   show    GET    /users/<int:user_id>          Show a single instance
   create  GET    /users/create                 Show the page to create a new instance
   store   POST   /users                        Create a new instance (then redirect)
   edit    GET    /users/<int:user_id>/edit     Show the page to edit an instance
   update  POST   /users/<int:user_id>          Update a single instance (then redirect)
   destroy POST   /users/<int:user_id>/delete   Delete a single instance (then redirect)
   ======= ====== ============================= ============================================================

Once you know these seven names, a lot of the generated routes, controller
methods, and templates start making sense very quickly.

Dot Notation
------------

.. youtube_embed:: dot-notation

Dot notation is one of the core ideas in Flask-Commands and is used to show
structure both in your data and your filing system.

For example:

.. code-block:: text

   recipes.comments.index

In that dotted name, each part between the dots is a **segment**:

- ``recipes``
- ``comments``
- ``index``

A segment is one meaningful part of the dotted name. Depending on where it
appears, a segment might be:

- a namespace
- a resource
- an action

For example:

.. code-block:: text

   recipes.comments.index

has these segments:

- ``recipes`` -> resource
- ``comments`` -> resource
- ``index`` -> action

And:

.. code-block:: text

   admin.recipes.index

has these segments:

- ``admin`` -> namespace
- ``recipes`` -> resource
- ``index`` -> action

That matters because Flask-Commands uses those segments to understand
structure.

A dotted name can influence:

- template folders
- route folders
- blueprint nesting
- endpoint naming
- controller naming patterns

This is one of the things I care a lot about in the package. If the resource
relationship is nested, I want the naming to read as nested too. That way when
you come back to the project later, the structure mimics the data's
relationship.

Naming Conventions
------------------

.. youtube_embed:: naming-conventions

Flask-Commands assumes a few conventions. They are simple, and they save you
from surprises later.

- **Views** use dotted names and follow plural resource naming (for example,
  ``posts.comments.images.show`` or ``components.buttons``).
- **Controllers** use PascalCase (Upper CamelCase) and are singular, ending in
  ``Controller`` (for example, ``RecipeController``,
  ``RecipeCommentController``, ``MainController``).
- **Models** use PascalCase (Upper CamelCase) and are singular (for example,
  ``Recipe``, ``Comment``, ``Image``).

Here is the short version:

- dots separate structure into segments
- underscores keep multiple words together inside one segment
- controllers end in ``Controller``
- controllers and models are singular
- views follow plural resource naming

View Input Normalization
------------------------

.. youtube_embed:: view-input-normalization

For views, Flask-Commands tries to be forgiving about common input variations.

That means it can normalize things like:

- allow upper or lower case anywhere
- allow ``/`` or ``.`` for segment separators
- allow ``-`` or ``_`` for multi-word resources
- repeated separators

.. list-table::
   :header-rows: 1

   * - Input
     - Normalized Result
     - What Changed
   * - ``recipes/comments/index``
     - ``recipes.comments.index``
     - Slashes become dots
   * - ``shopping-list.index``
     - ``shopping_list.index``
     - Dashes become underscores so ``shopping_list`` stays one multi-word segment
   * - ``recipes..comments...index``
     - ``recipes.comments.index``
     - Repeated separators get cleaned up
   * - ``Recipes.Comments.Index``
     - ``recipes.comments.index``
     - Uppercase input is normalized to lowercase resource structure

Let’s look at these one at a time.

Slashes into Dotted Paths
~~~~~~~~~~~~~~~~~~~~~~~~~

If you type:

.. code-block:: text

   recipes/comments/index

Flask-Commands normalizes that to:

.. code-block:: text

   recipes.comments.index

That is helpful because sometimes your brain is thinking in folder paths, and
sometimes your brain is thinking in dot notation URL names, and sometimes
your brain is just doing its best before coffee ☕️.

Dashes into Underscores Within a Segment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A segment is one meaningful part between the dots.

For example, in:

.. code-block:: text

   shopping_list.index

the segments are:

- ``shopping_list`` -> resource
- ``index`` -> action

You often need more than one word to describe an object.  That's fine and
Flask-Commands allows for this using either ``-`` or ``_``.  I figured people
would use both so the official marker is the ``_``, but use whichever you prefer.

Here are some examples of using a double-word resource or folder:

.. code-block:: text

   shopping_list.index
   pantry_items.show
   recipe_reviews.index

Just remember, **dots separate** structure into segments and **underscores keep
multiple words together** inside one segment.

Repeated Separators
~~~~~~~~~~~~~~~~~~~

If the input gets a little messy, Flask-Commands cleans that up too.

Sometimes we re-edit something so many times that when we press the
enter key it looks like this:

.. code-block:: text

   recipes..comments...index

That's fine. Flask-Commands has your back with a little cleanup to this:

.. code-block:: text

   recipes.comments.index

In other words, don't stress about those accidental extra separators from
turning into weird project structure.

Upper and Lower Case Anywhere
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the input has any uppercase characters, Flask-Commands normalizes
that too.

For example:

.. code-block:: text

   Recipes.Comments.Index

is normalized to:

.. code-block:: text

   recipes.comments.index

That helps keep the generated structure consistent on disk.

Wrap-Up
-------

These are the ideas that make the rest of Flask-Commands easier to understand:

- ``make:*`` commands run from the project root where there must be an
  ``app/`` folder and a ``run.py`` file
- views use dotted names and follow plural resource naming
- controllers use PascalCase and end in ``Controller``
- controllers and models use singular PascalCase names
- for views dots separate structure into segments
- for views underscores keep multiple words together inside one segment

Now that the rules are clear, let’s use them in the simplest useful command:
``make:view``.
