Model Prompt for make:view 
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

When Flask-Commands cannot find a registered model for the prior segment to
a RESTful action, it asks you which route shape you mean.

For example the command

.. code-block:: console

   flask make:view recipes.index -rc

is going to prompt you like the following 

.. code-block:: console

   No registered model found for recipes
       - Accept: /recipes
       - Decline: /recipes/index
   Generate the model Recipe?
   [Y/n]:

If you answer yes, Flask-Commands generates ``Recipe`` and uses the more
RESTful route ``/recipes``.

If you answer no, Flask-Commands does not generate a model and falls back to
the more literal route ``/recipes/index``.

One small note before we get into the more detailed examples: throughout this 
section I am going to keep using ``-c`` along with route generation.

That is because the missing-model prompt is really about the route shape, not
about choosing a controller. If you leave off ``-c`` and only generate the
route, Flask-Commands will still build the route, but it will default to using
``MainController`` in the route definition.

In other words:

.. code-block:: bash

   flask make:view recipes.index -r

generates a route that returns ``MainController.index()``.  Which by default
serves your landing page template from ``mains/index.html``

So throughout this section we will include the controller generator too using:

.. code-block:: bash

   flask make:view recipes.index -rc

Here Flask-Commands generates the resource-specific controller too, so the route 
can point to ``RecipeController.index()`` instead.

Lets stay focused on the real question in this chapter: whether the route 
should become ``/recipes`` or ``/recipes/index`` when the model does not 
exist yet.  In both examples above ``Recipe`` does not exist yet.

The issue here is the generated route.  At that point Flask-Commands can see 
there are really two possible directions for a route:

- if ``Recipe`` is treated like the resource, the route becomes ``/recipes``
- if not, Flask-Commands can fall back to the more literal route ``/recipes/index``

That is why the prompt exists. I figured there is a chance the model needs to 
be created for the RESTful action to act upon, or the route you are building 
just happen to end in a RESTful action name and you don't want the action you just 
want the literal word in the url.  

Avoid Prompts with Flags
------------------------

.. youtube_embed:: avoid-prompts-with-flags

If you already know what you want, you do not have to stop for the prompt.

To avoid that prompt, provide one of:

- ``--route`` for an explicit route instead of ``-r``
- ``--model`` for an explicit model
- ``-m`` or ``--generate-model`` to generate the model first

In other words, explicitly state the route or tell Flask-Commands to generate
the model.

If you want the more literal route and do not want to generate a model,
provide the route explicitly:

.. code-block:: bash

   flask make:view recipes.index -c --route /recipes/index

Here Flask-Commands does not need to ask anything because you already told it
the exact route to use.

If you want the more RESTful result, you can either provide the route 
explicitly using the RESTful pattern or you can create the model on the fly 
when you are building the view with ``--model``

The explicity restful route would look like this:

.. code-block:: bash

   flask make:view recipes.index -c --route /recipes

In the cases above, notice that the model is not created for you because 
you have not told Flask-Commands to build a model assocated to this route.  The 
prompt was not necessary here because you explicit told Flask-Commands the 
route.  If however you would like to create the model on the fly when you 
are building the view just giving Flask-Commands the model information up 
front using ``--model``


.. code-block:: bash

   flask make:view recipes.index -rc --model Recipe

If the naming is all in the view you can let Flask-Commands do all the heavy 
lifting 🏋️‍♀️ and just use generator flags for everything like this:

.. code-block:: bash

   flask make:view recipes.index -rcm

Notice here that the order of ``r``, ``c`` and ``m`` does not matter.  



.. code-block:: bash

   flask make:view recipes.index -c --route /recipes --model Recipe

or

.. code-block:: bash

   flask make:view recipes.index --route /recipes -cm


.. code-block:: bash

   flask make:view recipes.index -rc --model Recipe 

or even better let Flask-Commands generate the model name for you with with generator ``-m``

.. code-block:: bash

   flask make:view recipes.index -rcm

This last form is the shortest way to generate the view, controller, route,
and model without stopping for a prompt.

In cases like these, there is no prompt because you have already given
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
- you do not want Flask-Commands to do the model naming for you

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

That is really the sweet spot I wanted for a command like this:

- helpful, but not pushy
- smart, but not mysterious
- willing to do some work for you, but still honest about what is happening

Now that the command behavior makes sense, let’s use it to build a real
resource.
