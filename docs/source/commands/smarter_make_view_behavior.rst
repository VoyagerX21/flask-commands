Smarter make:view Behavior
==========================

Now that we have eased into ``flask make:view``, let’s talk about the smarter
side of the command. This is the part that quietly saves you from a lot of
little annoyances before they turn into bigger annoyances 😌

Or in more honest terms, this is where I make some confessions about what
happens behind the scenes.

``flask make:view`` is not just creating a template file and calling it a day.
It is also trying to help when your input is a little messy, when your route
shape is a little unclear, or when you are one missing model away from the
RESTful structure you actually meant to build.

So this chapter is about four things:

- input normalization
- missing-model prompts
- avoiding prompts with flags
- choosing between ``--route``, ``--model``, and ``-m``

Normalize Input Before Scaffolding
----------------------------------

.. youtube_embed:: normalize-input-before-scaffolding

Before we get too deep into the examples, I would like to make some
confessions about what happens behind the scenes with ``flask make:view``.

It’s not that I do not trust that you are going to put in a string that
Flask-Commands cannot handle, right 🤣 Well Oklahoma, the truth is I know
people will put in all kinds of non-standard inputs. So Flask-Commands kind of
normalizes 😇 the dotted input before scaffolding.

That means it will:

- allow upper or lower case anywhere
- allow ``/`` or ``.`` for segment separators
- allow ``-`` or ``_`` for multi-word resources
- collapse repeated separators

So for example:

- ``recipes/comments/index`` becomes ``recipes.comments.index``
- ``shopping-list.index`` becomes ``shopping_list.index``
- ``recipes..comments...index`` becomes ``recipes.comments.index``
- ``Recipes.Comments.Index`` becomes ``recipes.comments.index``

That little bit of cleanup matters because your brain is not always thinking
in the same format every time you type. Sometimes you are thinking in folder
paths. Sometimes you are thinking in dot notation. Sometimes you are just
typing quickly and hoping future-you will forgive present-you 😄

The nice part is that Flask-Commands tries to turn those common variations
into one clean structure before it starts generating files.

Understand Missing-Model Prompts
--------------------------------

.. youtube_embed:: understand-missing-model-prompts

When you use ``-r`` or ``--generate-route`` on a RESTful action,
Flask-Commands looks at the last resource segment and checks whether it maps to
a registered model.

If you are newer to web development, a **RESTful action** just means a common
page pattern like:

- ``index`` to show many records
- ``show`` to show one record
- ``create`` to show a form for a new record
- ``edit`` to edit an existing record

And when I say **registered model**, I mean a model that already exists in
your app and has been added to ``app/models/__init__.py``.

If that last segment is not a registered model, Flask-Commands can prompt you
to accept or decline generating the model and using the more RESTful route
shape.

For example, suppose you run:

.. code-block:: bash

   flask make:view recipes.index -r

and ``Recipe`` does not exist yet.

At that point Flask-Commands can see there are really two possible directions:

- if ``Recipe`` is treated like the resource, the route becomes ``/recipes``
- if not, Flask-Commands can fall back to the more literal ``/recipes/index``

That is why the prompt exists. I figured you might have just forgotten to make
the model you actually need to perform the RESTful action on.

Avoid Prompts with Flags
------------------------

.. youtube_embed:: avoid-prompts-with-flags

If you already know what you want, you do not have to stop for the prompt.

To avoid that prompt, provide one of:

- ``--route`` for an explicit route
- ``--model`` for an explicit model
- ``-m`` or ``--generate-model`` to generate the model first

In other words, explicitly state the route or tell Flask-Commands to generate
the model.

For example:

.. code-block:: bash

   flask make:view recipes.index --route /recipes

This says: use this route exactly.

.. code-block:: bash

   flask make:view recipes.index --model Recipe

This says: use this model name exactly.

.. code-block:: bash

   flask make:view recipes.index -m

This says: generate the model first and keep going.

You also do not have to choose only one of these flags. You can combine
``--route`` with ``--model`` or ``-m`` if you want to avoid the prompt
completely.

For example:

.. code-block:: bash

   flask make:view recipes.index --route /recipes --model Recipe

or

.. code-block:: bash

   flask make:view recipes.index --route /recipes -m

In cases like that, there is no prompt because you have already given
Flask-Commands the extra information it needs.

The important thing is this: prompts only come into play when you ask for a
generated route on a RESTful action and Flask-Commands still needs a little
more information to know exactly what structure you want.

Choose Between ``--route``, ``--model``, and ``-m``
---------------------------------------------------

.. youtube_embed:: choose-between-route-model-and-m

These options are all helpful, but they help in different ways.

Use ``--route`` when:

- the URL shape is the part you care about most
- you want to say exactly what the route should be
- you do not want route generation deciding that part for you

Use ``--model`` when:

- you know the exact model name
- you want to explicitly connect the view to that model
- you do not want Flask-Commands to do the naming for you

Use ``-m`` when:

- the model name is already obvious from the view structure
- you want Flask-Commands to generate the model as part of the command flow
- you do not want to repeat yourself more than necessary

And remember, these do not have to be isolated choices. You can mix them
together if that gives Flask-Commands the exact information you want it to
use.

A simple way to think about it is:

- ``--route`` controls the route directly
- ``--model`` controls the model name directly
- ``-m`` tells Flask-Commands to generate the model as part of the command flow

One Small but Important Note
----------------------------

.. youtube_embed:: get-templates-vs-post-actions

Templates are generated for ``GET`` actions.

That means actions like:

- ``index``
- ``show``
- ``create``
- ``edit``

can produce view templates.

But ``POST`` actions like:

- ``store``
- ``update``
- ``destroy``

wire controller and route behavior without creating a template file.

That is worth saying out loud because otherwise it can be a little surprising
the first time you scaffold a RESTful action and do not see a new template
appear.

Why This Matters
----------------

.. youtube_embed:: why-the-smarter-behavior-matters

All of this smarter behavior matters because it makes ``make:view`` more
forgiving without making it fuzzy.

You can type naturally.
You can be explicit when you want.
You can let the package help when the structure is obvious.
And when there is a meaningful decision to make, Flask-Commands can stop and
ask instead of charging ahead and leaving you with cleanup work later.

That is really the sweet spot I want for a command like this:

- helpful, but not pushy
- smart, but not mysterious
- willing to do some work for you, but still honest about what is happening

Now that the command behavior makes sense, let’s use it to build a real
resource.
