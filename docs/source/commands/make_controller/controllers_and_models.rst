Controllers and Models with make:controller
===========================================

Controllers usually exist because some kind of data needs to be shown,
updated, or organized.

In the last chapter we introduced ``--crud``, which scaffolds out a ton of
structure in our controller, routes, and templates.  Notice I said nothing
about our models.

While the ``--crud`` option treats the last segment like a RESTful resource,
it does not generate a data structure for us; creating a model is a separate
option.

That is by design.  To have Flask-Commands generate the model class you will
need to explicitly tell Flask-Commands that you want a model.  This is because
in most mature applications there are a lot of custom designs and I wanted
Flask-Commands to be helpful in all the cases: if you need a new model, if you
already have the model but need more structure, if you only want a namespace
instead of a model, or if you want some combination of these options.

In this chapter we will delve into these naming rules and how to choose the
command that tells the right story for your current situation.

Add a Model with ``--model`` or ``-m``
--------------------------------------

.. youtube_embed:: add-a-model-with-model-or-m

Often a controller is tied to a model. Flask-Commands gives you two methods
to handle this connection.


.. admonition:: Before you run this

   If you have followed the tutorial from the beginning, you already
   have a ``RecipeController`` and a ``Recipe`` model in your project.

   To avoid warnings and to see the creation output from start to finish,
   please spin up a fresh app with something like

   .. code-block:: bash

      flask new example_controller_with_model

Name the Model Directly
^^^^^^^^^^^^^^^^^^^^^^^

.. youtube_embed:: name-the-model-directly

The most direct method is to explicitly name the model using ``--model``:

.. code-block:: bash

   flask make:controller RecipeController --model Recipe

With ``--model``, you choose the exact model name. Flask-Commands does
not do any model-name generation from the controller name. Instead,
Flask-Commands uses the exact model name you provided.  If you prefer
plural model names then this is your opportunity to make your model plural
with ``--model Recipes``.

Generate the Model Name
^^^^^^^^^^^^^^^^^^^^^^^

.. youtube_embed:: generate-the-model-name

Alternatively, you can let Flask-Commands generate the model name
for you from the controller name using the flag ``-m``:

.. code-block:: bash

   flask make:controller RecipeController -m

Flask-Commands has a model-name generation rule that we will discuss more.  In
this example, Flask-Commands looks at the segment before Controller and makes
a model with that segment.  So with ``RecipeController`` the ``-m`` flag will
generate a ``Recipe`` model because that is the only segment before ``Controller``.

In this case, these two commands produced the same general result:

- a plain ``RecipeController`` (notice we didn't include ``--crud``)
- a ``Recipe`` model

The important difference is who chooses the model name.

With ``--model Recipe``, you choose the exact model name.  This option puts
you in the driver seat 🚗, you can call the model anything you want.

On the other hand, with ``-m`` or ``--generate-model``, Flask-Commands reads
the controller name and generates the model name following the rule:

 The last segment before ``Controller`` becomes the data structure.

We will add on to this rule when we discuss adding the ``--crud`` option.
But first let's expand on the difference in more complex examples.

Why Both Options Matter
^^^^^^^^^^^^^^^^^^^^^^^

.. youtube_embed:: why-both-options-matter

It is tempting to think, “Great, if both options generate the same thing I'm
going to use the shorter ``-m`` all the time.”

For one-word data structure names this logic works beautifully.

But your application will need more complexity with names like:

- ``ShoppingListController``
- ``AdminUserController``
- ``RecipeIngredientController``

Those names carry more meaning. Sometimes multiple words describe one data
structure. Sometimes a leading word is a namespace. Sometimes the name describes
a parent-child relationship.

Having flexibility like this is where ``--model`` gives us some special powers
to make more descriptive data structures.  In the above example, we built
a plain Controller class that just contains ``pass``.  Admittedly, this is
pretty weak.  Let's tie in our RESTful superpowers to scaffold out a
logic-filled controller class and see how ``--model`` and ``-m`` can help us
address all the above cases.  We will start by revisiting our old friend the
``Recipe`` resource one more time and end it with a bang 💥 by building
everything thus far with a single command.


Generating a RESTful Controller with a Model
--------------------------------------------

.. youtube_embed:: generating-a-restful-controller-with-a-model

It's party time 🥳.  Let's put everything we have built into one nice little
command!

.. admonition:: Before you run this

   If you have followed the tutorial from the beginning, you already
   have a ``RecipeController`` and a ``Recipe`` model in your project.

   To avoid warnings and to see the creation output from start to finish,
   please spin up a fresh app with something like

   .. code-block:: bash

      flask new example_controller_with_crud_and_model


We now have the full story on how to generate a new data structure (``-m``)
and include all seven RESTful routes (``--crud``) in one command.  I always say
'trust but verify', so let's combine the two options to see what happens:

.. code-block:: bash

   flask make:controller RecipeController --crud -m

This one command scaffolds everything that the docs have discussed thus far.
If you have been following along, take a moment to soak in what just happened.
With one command you have:

- a ``RecipeController`` class
- seven RESTful controller methods
- RESTful routes for the ``recipes`` resource
- templates for the ``GET`` actions
- a ``Recipe`` model
- model registration in ``app/models/__init__.py``

That is the full flat-resource story 🥳.

When the controller name is one level and there is no parent relationship or
namespacing, like ``RecipeController``, Flask-Commands
can generate the model name without drama 🎭. ``RecipeController`` points to a
``Recipe`` model, and the routes point to the ``recipes`` resource.

The Naming Problem
^^^^^^^^^^^^^^^^^^

.. youtube_embed:: the-naming-problem

Often there is more structure involved.

A recipe has ingredients. A user has posts. A project has tasks, or a user model
may need to sit behind an admin section for security.

That is where controller names start carrying more information.

In the rest of this chapter we will turn our attention to understanding the
naming convention so we can separate the following three ideas 💡:

- one data structure with a multi-word name
- a namespace that organizes part of the app
- a nested resource relationship

.. _single-data-structures-that-are-multiple-words:

Single Data Structures that are Multiple Words
----------------------------------------------

.. youtube_embed:: single-data-structures-that-are-multiple-words

Not everything can be described with a single word like ``Recipe``.  Sometimes
you need multiple words to describe your single data structure like:

.. centered:: ``ShoppingList``

A ``ShoppingList`` is not two data structures ``Shopping`` and ``List`` that
are somehow connected. Instead a ``ShoppingList`` is one model with a two-word
name.

 When multiple words describe one data structure, use ``--model``

In this case you will have to use ``--model`` and explicitly tell
Flask-Commands that you want a model with multiple words; otherwise,
Flask-Commands will generate a model for you but only with the segment before
``Controller``, in this case ``List`` so if you want the two-word model ``ShoppingList``
you will have to tell Flask-Commands with the ``--model`` option.

.. code-block:: bash

   flask make:controller ShoppingListController --crud --model ShoppingList

This command keeps ``ShoppingList`` together as one resource.  It does **not**
create a nested ``shopping/list`` structure. Instead, the two words are
converted into the naming style throughout the application:

- model class: ``ShoppingList``
- model file: ``app/models/shopping_list.py``
- controller class: ``ShoppingListController``
- controller file: ``app/controllers/shopping_list_controller.py``
- route package: ``app/routes/shopping_lists``
- URL path: ``/shopping-lists``
- route parameter: ``shopping_list_id``

For example, the generated ``show`` route uses one ``shopping_list_id``
parameter:

.. code-block:: python

   @bp.route('/shopping-lists/<int:shopping_list_id>', methods=['GET'])
   def show(shopping_list_id: int):
       return ShoppingListController.show(shopping_list_id)

And the controller method receives that same two-word resource id:

.. code-block:: python

   class ShoppingListController:
       @staticmethod
       def show(shopping_list_id: int) -> str:
           return render_template(
               "shopping_lists/show.html",
               shopping_list_id=shopping_list_id
           )

By explicitly telling Flask-Commands that the model is ``ShoppingList`` the
two words stay together as one data structure. The route looks like

- ``/shopping-lists/<int:shopping_list_id>``

instead of something nested like

- ``/shopping/lists/<int:list_id>``.

The same idea applies to other multi-word data structures like ``UserProfile``,
``PasswordReset``, or ``MealPlan``.  In fact you can use as many words as you
like to describe your data structure; just make sure to tell Flask-Commands
with the ``--model`` option.  You will end up with a controller name that
has multiple words but still describes a single data structure.  Don't worry,
you will still understand what's going on in the application six months from
now when you look in your models directory and see the multi-word model.

In the next section we will look at a multi-word controller where the first
word is not part of the model name.  Instead we want to organize our
application by namespacing controllers under a specific word.  For example, we
want an ``Admin`` section in the application but we do not want to create an
``Admin`` model.

When To Namespace
-----------------

.. youtube_embed:: when-to-namespace

Not every leading word in a controller name should become a model, or is even
part of a model.  There are times when you just need
to keep things nice and organized.  This is the idea behind namespacing.

A namespace is not a parent model in the resource chain, it is a
wrapper around an existing resource.  Consequently, you want the resource to
exist before you add the namespace.

A common example is ``Admin``. You want routes, controllers, and templates
that are specific to administrative users but you don't need an ``Admin``
model in your database.

Let's namespace a controller that allows administrative users to modify
other users' accounts.  Every time you run ``flask new`` you receive a new
Flask application that ships with a ``User`` model.  I figured everyone
needed some data structure to start out with and ``User`` seems like a good
starting place.  Let's use that model to create routes that are specific to
admin functions.  As usual we will just stub out these routes.

To do this you would type:

.. code-block:: bash

   flask make:controller AdminUserController --crud

Let's explain what's going on behind the scenes.  Flask-Commands takes
``AdminUserController`` removes the ``Controller`` part, and breaks down
``AdminUser`` into two segments ``Admin`` and ``User`` based on the
capitalization.  From there Flask-Commands recognizes that ``Admin`` is not
a registered model while ``User`` is a registered model.  When I say
**registered model**, I mean a model that exists in your application and is
imported in ``app/models/__init__.py``.

Because ``Admin`` is not a registered model when Flask-Commands builds out the
route URLs it will not include the parameter ``<int:admin_id>``.  Conversely,
because ``User`` is a registered model when Flask-Commands builds out the
route URLs it will include the parameter ``<int:user_id>``.  Consequently,
your route patterns will look like this:

- ``/admin/users/<int:user_id>``

Often this is the structure you are looking for, not a double word like

- ``/admin-users/<int:admin_user_id>``

or a nested resource like

- ``/admin/<int:admin_id>/users/<int:user_id>``

Instead, everything has the namespace ``admin`` in front.  This helps organize
your content so that you can do things like special permission checking.  The
takeaway here is to remember that Flask-Commands namespaces any leading
segment that is not a registered model.

 Flask-Commands treats any leading non-registered segments as namespaces.

.. _make-controller-multi-word-namespaces:

Multi-Word Namespaces
^^^^^^^^^^^^^^^^^^^^^

.. youtube_embed:: multi-word-namespaces

Namespaces can also contain more than one word. When several leading segments
are not registered models, Flask-Commands keeps them together as one
hyphenated namespace segment.

Suppose your app has a test kitchen area where staff can review and adjust
recipes before they are published. You do not need a ``TestKitchen`` model. You
just need a section of the app where certain users can use can manage recipes.

.. admonition:: Before you run this

   This section assumes ``Recipe`` is already a registered model. If you do not
   have it yet, create the model-backed resource first with the following
   command:

   .. code-block:: bash

      flask make:controller RecipeController --crud -m

Once ``Recipe`` exists, you can type:

.. code-block:: bash

   flask make:controller TestKitchenRecipeController --crud

Flask-Commands reads the name like this:

- ``TestKitchen`` is the namespace
- ``Recipe`` is the registered model-backed resource
- ``Controller`` tells Flask-Commands this is a controller class

The public URL keeps the namespace together with a hyphen:

- ``/test-kitchen/recipes``
- ``/test-kitchen/recipes/<int:recipe_id>``

We will see in the next section that is different from a nested model
relationship. ``TestKitchen`` is not a parent resource, so there is no
``<int:test_kitchen_id>`` parameter. It is just a namespace that organizes
the recipe routes.

.. _make-controller-public-pages-and-private-tools:

Public Pages and Private Tools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. youtube_embed:: public-pages-and-private-tools

Namespaces often represent private or specialized tools around a resource. In
our cooking app, the public site may only need recipe browsing pages, while the
test kitchen needs full CRUD tools for managing recipe content.

.. admonition:: Before you run this

   If you have followed the tutorial from the beginning, you already
   have a ``RecipeController`` and a ``Recipe`` model in your project.

   To avoid warnings and to see the creation output from start to finish,
   please spin up a fresh app with something like

   .. code-block:: bash

      flask new example_controller_with_namespace

In a new project file, you can build this shape with the following commands:

.. code-block:: bash

   flask make:view recipes.index -rcm
   flask make:view recipes.show -rc
   flask make:controller TestKitchenRecipeController --crud

The first command creates the public recipe index and generates the ``Recipe``
model. The second command adds the public recipe show page. The final command
adds the full test kitchen CRUD controller around the already registered
``Recipe`` model.

I’d write:

That gives regular users the ordinary recipe pages:

- ``/recipes``
- ``/recipes/<int:recipe_id>``

And it gives test kitchen users the private CRUD surface:

- ``/test-kitchen/recipes``
- ``/test-kitchen/recipes/<int:recipe_id>``
- ``/test-kitchen/recipes/create``
- ``/test-kitchen/recipes/<int:recipe_id>/edit``

This is often a better production shape than giving the public side full CRUD.
The public app gets the pages it needs, and the test kitchen namespace gets the
management tools.

Now we are ready for the other side of the naming rule.  A namespace is a
leading segment that is not a registered model. A nested parent is a leading
segment that is a registered model. So without further ado, let's look at
that parent-child relationship next.

Naming Nested Controllers by Relationship
-----------------------------------------

.. youtube_embed:: naming-nested-controllers-by-relationship

Suppose our cooking app needs a new data structure, ``Ingredient``.  For
those following along I can hear the shouts of hurray 🥳 as everyone is glad I
didn't say ``Recipe`` again 🤪.

While we want an ``Ingredient`` data structure we don't want a random resource
floating around by itself.  Future you will not like a ton of random floating
resources in your application.  Instead, we need the new data structure
``Ingredient`` to connect to the current ``Recipe`` data structure.  In other
words, our application needs the ability for recipes to have ingredients.

To show this relationship in diagram form one often writes:

.. centered:: **Recipe -> Ingredient**.

This is where nesting comes into play.  A nested controller name should read
from parent to child.

``RecipeIngredientController`` means:

- ``Recipe`` is the parent data structure
- ``Ingredient`` is the child data structure
- ``Controller`` tells Flask-Commands this is a controller class

The important rule here is:

 Flask-Commands treats a leading segment as a parent resource when that
 segment matches a registered model.

Because ``Recipe`` is registered, Flask-Commands reads
``RecipeIngredientController`` as we described above:

- parent resource: ``Recipe``
- child resource: ``Ingredient``

That is what lets Flask-Commands generate nested routes like:

- ``/recipes/<int:recipe_id>/ingredients``

That naming gives Flask-Commands enough structure to build folders, routes,
templates, and endpoint names that tell the same story.

- controller file: ``app/controllers/recipe_ingredient_controller.py``
- route package: ``app/routes/recipes/ingredients/``
- template folder: ``app/templates/recipes/ingredients/``
- URL shape: ``/recipes/<int:recipe_id>/ingredients``
- endpoint name: ``recipes.ingredients.index``

The endpoint name tells Flask which nested route you want, and the
``recipe_id`` tells Flask which parent recipe the ingredient route belongs to:


- ``/recipes/<int:recipe_id>/ingredients`` (index route)
- ``/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>`` (show route)

So instead of a flat endpoint name, you preserve the nesting and references to
the parent structure.  The above routes are called with the following commands:

.. code-block:: python

   url_for('recipes.ingredients.index', recipe_id=1)
   url_for('recipes.ingredients.show', recipe_id=1, ingredient_id=2)

Go Nested with ``--crud``
^^^^^^^^^^^^^^^^^^^^^^^^^

.. youtube_embed:: go-nested-with-make-controller-crud

After a lot of build up let's now build the nested relationship we
just discussed **Recipe -> Ingredient** with a CRUD scaffolding in the
controller.

.. admonition:: Before you run this

   This section assumes ``Recipe`` is already a registered model. If you do not
   have it yet, create the model-backed resource first with the following
   command:

   .. code-block:: bash

      flask make:controller RecipeController --crud -m

If you are following along you should already have a ``Recipe`` model.
Having ``Recipe`` as a registered model before you run your next command is
really the important part.  Without ``Recipe`` as a registered model
Flask-Commands will treat ``Recipe`` as a namespace.  However, when ``Recipe``
is a model and we type:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud

we end up with the nested resource structure described above. Because
``Recipe`` is a registered model, Flask-Commands treats it as the parent
resource. Because we passed ``--crud``, the final segment, ``Ingredient``,
becomes the RESTful child resource.

Notice that we did not include ``-m`` or ``--model``. Our command builds out the
nested controller, routes, and templates, but it does not generate or register
an ``Ingredient`` model.

Now that we understand how Flask-Commands generates nested controller
structure, we can look at what happens when we add ``-m`` and ask
Flask-Commands to also generate the model.
