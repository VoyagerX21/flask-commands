Nested Resources with make:view
===============================

Now that we have built a simple resource and looked at how RESTful actions
work, the next step is to build on that structure with nested resources.

If you are newer to web development, do not let the phrase “nested
resources” scare you off. All it means is that one object belongs to another 
object.


In our cooking app let's add comments and images so we have:

- a comment belonging to a recipe
- an image belonging to a comment

Nesting like this ``Recipe -> Comment -> Image`` is the idea we are after.

In URL terms, nesting means the child's URL depends on the parent instead of 
standing alone.

One of the feature I was unwilling to compromise on when building 
Flask-Commands was making the folder structure, route structure, controller 
structure, and endpoint naming all reflect their relationships. That way, when 
you come back to the code six months later, you can quickly see how the 
data structures relate without digging through the project (or 
having an AI 🤖 dig through your files to answer how to objects are related). 


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

When I saw this the first time I thought "this is weird 🤪, who would have 
thought to register a blueprint in another blueprint!!!!"  But this is one of 
the cool things I love about Flask. Flask is not so opinionated that it gets 
in your way, which gives you the freedom to try different structures.

Ok, you’re saying, that’s great but why would I do this?

By registering the ``comments`` blueprint inside the ``recipes``
blueprint, we are able to use the dotted naming convention when referencing 
a route:

.. code-block:: python

   url_for('recipes.comments.index', recipe_id=1)

For me, this was a big deal because it mirrors how SQLAlchemy works. If we
have a recipe variable called ``recipe``, then to get all the comments for that
recipe, we would write ``recipe.comments``.

Now the route name, the folders, and the controller naming all follow that same
relationship in the data.

What makes this so useful is that all of those pieces follow the same
relationship. In our example, the story that comments belong to recipes is 
seen in the structures that are built:

- ``app/models/comment.py`` (comment building block)
- ``app/templates/recipes/comments/index.html`` (relationship recipes -> comments)
- ``app/controllers/recipe_comment_controller.py`` (relationship recipes -> comments)
- ``app/routes/recipes/comments/`` (relationship recipes -> comments)

This is a lot of structure to get out of one command, and more importantly, it
is structure that reads honestly.

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

The command to build out the index page for images and set up the relationship 
is what you would expect:

.. code-block:: bash

   flask make:view recipes.comments.images.index -rcm

Our brains 🧠 definatly link like this, **Recipes -> Comments -> Images**. 
However, it hurts my brain just thinking 🧐 about how we would wire all these
parts together in a Flask application and not break something. 

But here is the nice part: you do not have to wire all of that by hand.

With this command, Flask-Commands builds a structure like:

- ``app/models/image.py`` (image building block)
- ``app/templates/recipes/comments/images/index.html`` (relationship recipes -> comments -> images)
- ``app/controllers/recipe_comment_image_controller.py`` (relationship recipes -> comments -> images)
- ``app/routes/recipes/comments/images/`` (relationship recipes -> comments -> images)

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

You can keep going deeper if you want. Flask-Commands will support as many
levels deep as you want; however, as a rule of thumb, I rarely go 
over three levels deep. Once things get deeper than that, the structure 
can start feeling hard to read even if it is technically correct.

This structure and naming is one of the parts of the package I was unwilling 
to compromise on while developing Flask-Commands.  I always felt that if the 
structure is nested in the application, then I want it to read as nested 
in the endpoint naming too.

So with:

.. code-block:: bash

   flask make:view recipes.comments.images.index -rcm

your endpoint names is of the same form:

.. code-block:: python

   url_for('recipes.comments.images.index', recipe_id=1, comment_id=2)

I love ❤️ this, because it's easy to remember and the endpoint itself tells 
the truth about the relationship structures.

You do not have to guess:

- what belongs to what
- which blueprint is nested where
- how the route hierarchy fits together

The endpoint name already answers all these questions.

For any developer, that is a big deal. Route names, controller
names, and folder paths can end up as a hodgepodge mess if you let them. 
However, when everything line up with the data structures, the app becomes 
much more manageable to maintain.


Why Nesting Pays Off
---------------------

.. youtube_embed:: why-nesting-pays-off

Nested resources are where dot notation really starts paying dividends 💰

With just these three commands:

.. code-block:: bash

   flask make:view recipes.index -rcm
   flask make:view recipes.comments.index -rcm
   flask make:view recipes.comments.images.index -rcm

You are able to bring to life a surprising amount of relationship-aware 
structure in just a short amount of time.

From these commands, your Flask application quickly contains a mature
level of structure in the following areas:

- templates
- controllers
- routes
- models
- endpoint names

As we have shown above same idea does not stop at ``index``. You can use the
same thing for ``show`` and for the other five RESTful actions. That is where 
the structure really starts to scale, because the naming and relationships 
keeps lining up as your app grows.  Keeping your application tidy, readable,
and more importantly maintainable.

At this point I thought great but what if I already know that I want all
seven RESTful actions.  Are you telling me that I have to type in seven
different commands!  I thought this was going to save me time?

Please don't stress out 😬.  If you find yourself generating 
RESTful actions one at a time, the natural next question is: can 
Flask-Commands build all seven actions in one command?

I'm happy to say, yes 👏 and that is exactly where our next topic will take us
when we learn a new command ``flask make:controller``.
