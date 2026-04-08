Nested Resources with make:view
===============================

This is where the package really starts to shine ☀️

Up to this point we have built a simple resource with ``recipes.index`` and
``recipes.show``. That already gives us something real. But now we get to the
part that makes Flask-Commands feel especially useful: nested resources.

And if you are newer to web development, do not let the phrase “nested
resources” scare you off. All it really means is this:

- one thing belongs to another thing

In our cooking app:

- a comment belongs to a recipe
- an image can belong to a comment

That is it. That is the whole big idea.

A nested URL usually means the child depends on the parent, not that the child
stands alone.

The nice part is that Flask-Commands lets the folder structure, route
structure, controller structure, and endpoint naming all tell the truth about
those relationships. So when you come back to the code six months later, you
can quickly see how the data structures relate without guessing. That is one
of the things I was unwilling to compromise on while building this package.

Build ``recipes.comments.index``
--------------------------------

.. youtube_embed:: build-recipes-comments-index

Let’s continue with our cooking app and suppose we are going to allow users to
leave comments on recipes.

That means we now have a parent-child relationship:

- parent: ``Recipe``
- child: ``Comment``

So the nested view we want is:

.. code-block:: bash

   flask make:view recipes.comments.index -rcm

That dotted name:

.. code-block:: text

   recipes.comments.index

means:

- ``recipes`` is the parent resource
- ``comments`` is the child resource
- ``index`` is the action

And the flags mean:

- ``-r`` generates the **route**
- ``-c`` generates the **controller**
- ``-m`` generates the **model**

When you run that command, Flask-Commands sets up the nested comments view and
route under recipes, creates the ``RecipeCommentController``, and builds the
``Comment`` model.

The key part of the story is that the ``comments`` blueprint gets registered
**inside** the ``recipes`` blueprint in:

- ``app/routes/recipes/__init__.py``

So weird 🤪 who would have thought to register a blueprint in another
blueprint!!!!

That is one of the cool things I love about Flask. It is not so opinionated
that it gets in your way, which gives you the freedom to try structures like
this.

Ok, you’re saying, that’s great but why would I do this?

Because by registering the ``comments`` blueprint inside the ``recipes``
blueprint, we get to use the dotted naming convention when referencing a route
like:

.. code-block:: python

   url_for('recipes.comments.index', recipe_id=1)

And that is a big deal.

Now the route name, the folders, the controller name, and the relationship
itself are all telling the same story. Comments belong to recipes, so the
application reads that way too.

That structure gives you:

- ``app/templates/recipes/comments/index.html``
- ``app/controllers/recipe_comment_controller.py``
- ``app/routes/recipes/comments/``
- ``app/models/comment.py``

That is a lot to get from one command, and more importantly, it is structure
that reads honestly.

Add ``recipes.comments.show``
-----------------------------

.. youtube_embed:: add-recipes-comments-show

Now that the nested comments resource exists, adding another page works the
same way it did before:

.. code-block:: bash

   flask make:view recipes.comments.show -rc

Notice that we did **not** use ``-m`` here.

That is because the ``Comment`` model was already created in the earlier
command:

.. code-block:: bash

   flask make:view recipes.comments.index -rcm

So now we only need to add:

- the ``show`` template
- the ``show`` controller method
- the nested ``show`` route

This is one of the nice patterns in the package. Once the resource exists,
Flask-Commands keeps building on top of what is already there instead of
making you recreate the same pieces over and over again.

Why the Nested Structure Matters
--------------------------------

.. youtube_embed:: why-the-nested-structure-matters

This is the part I really care about.

When the comments live under recipes in the route folders, template folders,
and controller naming, the structure itself starts teaching you what belongs
to what.

That means when you come back later and see something like:

- ``app/templates/recipes/comments/``
- ``app/routes/recipes/comments/``
- ``RecipeCommentController``

you do not have to wonder:

- “Do comments belong to recipes?”
- “Is this a standalone resource?”
- “How is this supposed to fit together?”

The project structure already answers those questions for you.

That kind of clarity is not flashy, but it saves real mental energy later.

Go Three Levels Deep with Images
--------------------------------

.. youtube_embed:: go-three-levels-deep-with-images

Now let’s dive a little deeper down this rabbit hole 🐇

Suppose that in our cooking app, users can upload images when they leave a
comment.

Now the relationship becomes:

- ``Recipe``
- ``Comment``
- ``Image``

Or in plain English:

- images belong to comments
- comments belong to recipes

So the command becomes:

.. code-block:: bash

   flask make:view recipes.comments.images.index -rcm

Three levels, what? **Recipes -> Comments -> Images**. That hurts my brain
just thinking about how we would wire all those parts together to work as we
would expect. 🧐

But here is the nice part: you do not have to wire all of that by hand.

With this command, Flask-Commands builds a structure like:

- ``app/templates/recipes/comments/images/index.html``
- ``app/controllers/recipe_comment_image_controller.py``
- ``app/routes/recipes/comments/images/``
- ``app/models/image.py``

And the same nesting idea keeps working here too. In order to keep the dotted
naming convention, the ``images`` blueprint gets registered inside
``comments``, which is already registered inside ``recipes``. That chain is
what gives you endpoint naming like:

.. code-block:: python

   url_for('recipes.comments.images.index', recipe_id=1, comment_id=2)

That is one of the coolest parts of the package to me. You tell
Flask-Commands the relationship structure with dots, throw in your generated
flags of route ``-r``, controller ``-c``, and model ``-m``, and preso 🪄
everything is built for you.

You can keep going deeper if you want. Flask-Commands will support it. That
said, as a rule of thumb for myself, I rarely go over three levels deep. Once
things get deeper than that, the structure can start feeling harder to read
even if it is technically correct.

Understand Dotted Endpoint Naming
---------------------------------

.. youtube_embed:: understand-dotted-endpoint-naming

This is one of the parts of the package I was unwilling to compromise on.

If the structure is nested in the application, I want it to read as nested in
the endpoint naming too.

So with:

.. code-block:: bash

   flask make:view recipes.comments.images.index -rcm

you get endpoint names like:

.. code-block:: python

   url_for('recipes.comments.images.index', recipe_id=1, comment_id=2)

I love that because the endpoint itself tells the truth about the
relationship.

You do not have to guess:

- what belongs to what
- which blueprint is nested where
- how the route hierarchy fits together

The endpoint name already explains it.

And for a beginner web developer, that is a big deal. Route names, controller
names, and folder paths can all feel abstract at first. But when they all line
up with the data relationship, the app becomes much easier to read.

A Beginner-Friendly Way to Think About This
-------------------------------------------

.. youtube_embed:: a-beginner-friendly-way-to-think-about-nested-resources

If you are still learning how web apps fit together, here is a simple way to
think about what is happening.

For a nested page like:

.. code-block:: text

   recipes.comments.index

the pieces line up like this:

- route: the browser address for comments under a recipe
- controller: the Python logic for those comments
- view: the HTML template for those comments
- model: the data structure for those comments

So the relationship is not only living in one place. It is living across the
route, controller, view, and model all at the same time.

That is exactly why this structure feels so good when it is done well. The
whole app starts telling the same story.

Wrap-Up
-------

Nested resources are where dot notation really starts paying dividends 💰

With commands like:

.. code-block:: bash

   flask make:view recipes.comments.index -rcm
   flask make:view recipes.comments.show -rc
   flask make:view recipes.comments.images.index -rcm

Flask-Commands can build relationship-aware structure across:

- templates
- controllers
- routes
- models
- endpoint names

That is a big part of what makes the package useful. The structure on disk
starts matching the structure in your head.

And once that starts happening, the app no longer feels like a few
disconnected files. It starts to feel like a real application shape.
