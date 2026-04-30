Controllers and Models with make:controller
===========================================

Controllers usually exist because some kind of data needs to be shown,
updated, or organized.

In the last chapter we introduced ``--crud``, which scaffolds a out a ton of
structure in our controller, routes, and templates.  Notice I said nothing 
about our models. 

While the ``--crud`` option treats the last segment like a RESTful resource 
it does not generate data structure for us, creating a model is a separate 
choice.

That is by design.  To have Flask-Commands generate the model class you will 
need to explicitly tell Flask-Commands that you want a model.  This is because
in most mature applications there are a lot of custom designs and I wanted 
Flask-Commands to be helpful in all the cases: if you need a new model, if you 
already have the model but need more structure, if you only want a namespace 
instead of a model, or if you want some combininate of theses.

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

   To avoid warnings and to see the creation output from start to finish please
   spin up a fresh app with something like

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
plural model name then this is your opportunity to make your model plural 
with ``--model Recipes``.

Generate the Model Name
^^^^^^^^^^^^^^^^^^^^^^^

.. youtube_embed:: name-the-model-directly

Alternatively, you can let Flask-Commands generate the model name 
for you from the controller name using the flag ``-m``:

.. code-block:: bash

   flask make:controller RecipeController -m

Flask-Commands has a generating name rule that we will discuss more.  In this
example, Flask-Commands looks at the prior segment to Controller and makes a 
model with that segment.  So with ``RecipeController`` the ``-m`` flag will 
generate a ``Recipe`` model because that is the only segment before ``Controller``.

In this case, these two commands produced the same general result:

- a plain ``RecipeController`` (notice we didn't include ``--crud``)
- an ``Recipe`` model

The important difference is who chooses the model name.

With ``--model Recipe``, you choose the exact model name.  This option puts
you in the driver seat 🚗, you can call the model anything you want.  

On the other hand, with ``-m`` or ``--generate-model``, Flask-Commands reads 
the controller name and generates the model name following the rule:
 
 The last segment before ``Controller`` becomes the data structure. 

We will add on to this rule when we discuss added in the ``--crud`` option.  
But first lets expand on the difference in more complex examples. 

Why Both Options Matter
^^^^^^^^^^^^^^^^^^^^^^^

.. youtube_embed:: why-both-options-matter

It is tempting to think, “Great, If both options generate the same thing I'm 
going to use the shorter ``-m`` all the time.”

For one word data structure names this logic works beautifully.

But your application will need more complexity with names like:

- ``ShoppingListController``
- ``AdminUserController``
- ``RecipeIngredientController``

Those names carry more meaning. Sometimes multiple words describe one data
structure. Sometimes a leading word is a namespace. Sometimes the name describes
a parent-child relationship.

Having flexability like this is where ``--model`` gives us some special powers 
to make more descriptive data structures.  In the above example, we built
a plain Controller class that just contains ``pass``.  Admidatly, this is pretty 
weak.  Let's tie in our RESTful superpowers to scaffold out a logic filled controller 
class and see how ``--model`` and ``-m`` can help us address all the above 
cases.  We will start by revisiting our old friend the ``Recipe`` resource 
one more time and end it with a bang 💥 building everything thus far with a 
single command.


Generating a RESTful Controller with a Model
--------------------------------------------

.. youtube_embed:: generating-a-restful-controller-with-a-model

It's party time 🥳.  Let's put everything we have built into one nice little 
command!

.. admonition:: Before you run this

   If you have followed the tutorial from the beginning, you already
   have a ``RecipeController`` and a ``Recipe`` model in your project.

   To avoid warnings and to see the creation output from start to finish please
   spin up a fresh app with something like

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

When the controller name is one level and there is not parent relationship or 
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
Flask-Commands will generate a model for you but only with the prior segment to 
Controller, in this case ``List`` so if you want the two word model ``ShoppingList``
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
two words still as one data structure. The route look like 
``/shopping-lists/<int:shopping_list_id>`` instead of somthing nested like
``/shopping/lists/<int:list_id>``.

The same idea applies to other multi-word data structures like ``UserProfile``,
``PasswordReset``, or ``MealPlan``.  Infact you can use as many words as you
like to describe your data structure just make sure to tell Flask-Commands 
with the ``--model`` option.  You will end up with a controller name that 
has multiple words, but describing a single data structure.  Don't worry you 
will still understand what's going on in the application six months from now
when you look in your models directory and see the multi-word model.

In the next setion we will look at multi-word controller but where the first 
word is not part of the model name.  Instead we want to organize our 
application by namespacing controllers under a specific word.  For example, we
want an ``Admin`` section in the application but we do not want to create an 
``Admin`` model. 


When To Namespace
-----------------

.. youtube_embed:: when-to-namespace

Not every leading word in a controller name should become a model, or is even
part of a model.  There are times when you just need 
to keep thing nice and organized.  This is the idea behind namespacing.  

A common example is ``Admin``. You want routes, controllers, and templates 
that are specific to admimistrative users but you don't need an ``Admin`` 
model in your database.  

Let's namespace a controller for that allows admimistrative users to modify 
other user's accounts.  Every time you run ``flask new`` you receive a new 
flask application that ships with a ``User`` model.  I figured everyone 
needed some data structure to start out with and ``User`` seems like a good 
starting place.  Let's use that model to create routes that are specific to 
admin functions.  As usual we will just stub out the these routes.  

To do this you would type:

.. code-block:: bash

   flask make:controller AdminUserController --crud

Let's explain what's going on behind the scenes.  Flask-Commands take 
``AdminUserController`` removed the ``Controller`` part, and breakes down 
``AdminUser`` into two segments ``Admin`` and ``User`` based on the 
capitalization.  Form there Flask-Commands recognizes that ``Admin`` is not 
a registered model while ``User`` is a registered model.  When I say 
**registered model**, I mean a model that exists in your application and is 
imported in ``app/models/__init__.py``. 

Because ``Admin`` is not a registered model when flask command builds out the
route urls it will not include the parameter ``<int:admin_id>``.  Conversly, 
because ``User`` is a registered model when flask command builds out the 
route urls it will include the parameter ``<int:user_id>``.  Consequently, 
your route patters will look like this:

- ``/admin/users/<int:user_id>``

Often this is the structure you are looking for, not a double word like 

- ``/admin-users/<int:admin_user_id>`` 

or a nested resource like 

- ``/admin/<int:admin_id>/users/<int:user_id>``

Instead, everything has the namespace ``admin`` in front.  This help organize 
you content so that you can do thinkg like special permission checking.  The 
take away here is to remember that Flask-Commands namespaces any leading 
segment is not a registered model.  

 Flask-Commands treats any leading non-registered segments as namespaces.

Now without further ado, let's 
look closely at how we can nested resources.  

Naming Nested Controllers by the Relationship
---------------------------------------------

.. youtube_embed:: naming-nested-controllers-by-the-relationship

Suppose say our cooking app needs a new data structure, ``Ingredient``.  For 
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

That is what lets Flask-Commands generate nested route like:

- ``/recipes/<int:recipe_id>/ingredients``

That naming gives Flask-Commands enough structure to build folders, routes,
templates, and endpoint names that tell the same story.

- ``app/controllers/recipe_ingredient_controller.py``
- ``app/routes/recipes/ingredients/``
- ``app/templates/recipes/ingredients/``
- ``recipes.ingredients.index`` endpoint names 

The controller name is doing more than naming a Python class. It is describing
how the resource belongs in the application.


Go Nested with ``--crud``
^^^^^^^^^^^^^^^^^^^^^^^^^

.. youtube_embed:: go-nested-with-make-controller-crud

After a lot of build up let's now build the nested relationship we
just discussed **Recipe -> Ingredient**.

If you are following along you should already have a ``Recipe`` model.  This 
is really the important part because without ``Recipe`` as a registered model
Flask-Commands will treat ``Recipe`` as a namespace.  But when ``Recipe`` is 
a model and we type:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud

We end up with a nested resources.  Notice that we did not include the ``-m`` 
or ``--model`` options, instead we use ``--crud``. 

Because ``Recipe`` is a registered model and we added the ``--crud`` option, 
our last segment ``Ingredient`` is treated like a RESTful resource but it 
doesn't register the model for you.  

In this case, Flask-Commands has enough information to build the nested route 
resource shape like:

- /recipes/<int:recipe_id>/ingredients (index route)
- /recipes/<int:recipe_id>/ingredients/<int:ingredient_id> (show route)

So instead of a flat endpoint name, you preserve the nesting and references to
the routes include the recipe_id like this:

.. code-block:: python

   url_for('recipes.ingredients.index', recipe_id=1)

So, with ``Recipes`` as a registered model we end up with a lot of structures 
that explain the relationship:

- a ``RecipeIngredientContoller`` under ``app/controllers/recipe_ingredient_controller.py``
- nested routes under ``app/routes/recipes/ingredients/``
- templates under ``app/templates/recipes/ingredients/``
- nested endpoint names like ``recipes.ingredients.index``

Now that we understand how Flask-Commands generates nested controller structure,
we can look at what happens when we add ``-m`` and ask Flask-Commands to
generate the model too.
