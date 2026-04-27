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
need to explicit tell Flask-Commands that you want a model.  There is lots 
going on in a mature application and Flask-Commands is there to help in all the 
cases: you need a new model, you already have the model, you only want a 
namespace and not a model.

This chapter is about those naming rules and how to choose the command that 
tells the right story for your current situation.

Add a Model with ``--model`` or ``-m``
--------------------------------------

.. youtube_embed:: add-a-model-with-model-or-m

Often a controller is tied to a model. Flask-Commands gives you two methods
to handle this connection.  


.. admonition:: Before you run this

   If you are following the tutorial from the beginning, you already
   have a ``RecipeController`` and a ``Recipe`` model in your project.

   To avoid warnings and see the cration output from start to finish spin 
   up a fresh app with something like

   .. code-block:: bash

      flask new example_controller_with_model
   
Name the Model Directly
^^^^^^^^^^^^^^^^^^^^^^^

The most direct method is to explicitly name the model using ``--model``:

.. code-block:: bash

   flask make:controller RecipeController --model Recipe

With ``--model Recipe``, you choose the exact model name. Flask-Commands does
not do any model-name generation from the controller name. It uses the model
name you gave it.

Generate the Model Name
^^^^^^^^^^^^^^^^^^^^^^^

Alternatively, you can let Flask-Commands generate the model name 
for you from the controller name using the flag ``-m``:

.. code-block:: bash

   flask make:controller RecipeController -m

Flask-Commands looks at the prior segment to Controller and make a model with 
that segment.  So with ``RecipeController`` the ``-m`` flag will generate a 
``Recipe`` model because that is the part before ``Controller``.


These two commands produce the same general result:

- a plain ``RecipeController`` (notice we didn't include ``--crud``)
- an ``Recipe`` model

The important difference is who chooses the model name.

With ``--model Recipe``, you choose the exact model name.  This option allows
you to call the model anything you want.  If you prefer plural model name 
then this is your opportunity to make your model plural with 
``--model Recipes``.

On the other hand, with ``-m`` or ``--generate-model``, Flask-Commands reads 
the controller name and generates the model name following the rule:
 
 The last segment before ``Controller`` becomes the data structure.  Any
 earlier segments only become parent resources with route parameters when 
 Flask-Commands recognizes them as registered models. 

Why Both Options Matter
^^^^^^^^^^^^^^^^^^^^^^^

It is tempting to think, “Great, If both options generate the same thing I'm 
going to use the shorter ``-m`` all the time.”

For one word names that need to be data structures, that works beautifully.

But your application will need more complexity with names like:

- ``ShoppingListController``
- ``AdminUserController``
- ``RecipeIngredientController``

Those names carry more meaning. Sometimes multiple words describe one data
structure. Sometimes a leading word is a namespace. Sometimes the name describes
a parent-child relationship.

Having flexability like this is where ``--model`` gives us some speical powers 
to make more descriptive data structures.  Before that let's revisit up our 
``Recipe`` resource one more time and end it with a bang 💥 building everything 
thus far with a single command.


Generating a RESTful Controller with a Model
--------------------------------------------

.. youtube_embed:: generating-a-restful-controller-with-a-model

It's party time 🥳.  Let's put everything we have built into one nice little 
command!

.. admonition:: Before you run this

   If you are following the tutorial from the beginning, you already
   have a ``RecipeController`` and a ``Recipe`` model in your project.

   To avoid warning and see the cration output from start to finish spin 
   up a fresh app with something like

   .. code-block:: bash

      flask new example_controller_with_crud_and_model
   

We now have the full story on how to generate a new data structure and include 
all seven RESTful routes all in one command.  We just need to combine the two 
options ``--crud`` and ``-m``.

.. code-block:: bash

   flask make:controller RecipeController --crud -m

This one command scaffolds everything that the docs have discussed up to this
point. If you have been following along, take a moment to soak it all in. With
one command you have:

- a ``RecipeController`` class
- seven RESTful controller methods
- RESTful routes for the ``recipes`` resource
- templates for the ``GET`` actions
- a ``Recipe`` model
- model registration in ``app/models/__init__.py``

That is the full flat-resource story.

When the controller name is one level and there is not parent relationship or 
namespaceing, like ``RecipeController``, Flask-Commands
can generate the model name without drama 🎭. ``RecipeController`` points to a
``Recipe`` model, and the routes point to the ``recipes`` resource.

Often there is more structure involved. A recipe has ingredients. A user has 
posts. A project has tasks. A user model need to set behind an admin for 
security.  This is where controller names start carrying 
more meaning, and understanding a naming convention is where we turn our 
attention to next.

Single Data Structures that are Multiple Words
----------------------------------------------

Not everything can be described with a single word like ``Recipe`` sometimes 
you need multiple words to describe your single data structure like ``Shopping List``.

In these cases you will have to use ``--model`` and explicity tell 
Flask-Commands that you want a model with multiple words; otherwise, 
Flask-Commands will generate a model for you but only with the prior segment to 
Controller, in this case ``List`` so if you want the two word model ``ShoppingList``
you will have to tell Flask-Commands with the --model option.  

.. code-block:: bash
   
   flask make:controller ShoppingListController --crud --model ShoppingList


Understand Namespaces
---------------------

.. youtube_embed:: understand-namespaces


There is one important rule before we generate the nested resource:
Flask-Commands only treats a leading segment as a parent resource when that
segment matches a registered model.

When I say **registered model**, I mean a model that exists in your application
and is imported in ``app/models/__init__.py``.

If ``Recipe`` is registered, then Flask-Commands reads 
``RecipeIngredientController`` as we described above:

- parent resource: ``Recipe``
- child resource: ``Ingredient``

That is what lets Flask-Commands generate a nested route like:

- ``/recipes/<int:recipe_id>/ingredients``

If ``Recipe`` is not registered, Flask-Commands treats ``Recipe`` as a
namespace. Think of a namespace as a way of organizing content but it don't 
need a data structure.  A great archetypal example is  ``admin``.  We might 
need routes and views that are all hidden behind an admin structure; however,
admin is not a data structure in our database.  

Going back to our example, if ``Recipes`` was not a registered model then we 
would not end up with ``recipe_id`` as a route parameter.

- ``/recipes/ingredients``

This distinction matters because ``recipes`` can only become a parent resource
when Flask-Commands knows that ``Recipe`` is a model.


Naming Nested Controllers by the Relationship
---------------------------------------------

.. youtube_embed:: naming-nested-controllers-by-the-relationship

Let's say our cooking app needs a new data structure, ``Ingredient``.  For 
those following along I can hear the shouts of hurray 🥳 as everyone is glad I 
didn't say ``Recipe`` again 🤪. 

A Recipe has Ingredients so we need the relationship:

.. centered:: **Recipe -> Ingredient**.

This is where nesting comes into play and naming is very import.  A nested 
controller name should read from parent to child.

``RecipeIngredientController`` means:

- ``Recipe`` is the parent data structure
- ``Ingredient`` is the child data structure
- ``Controller`` tells Flask-Commands this is a controller class

That naming gives Flask-Commands enough structure to build folders, routes,
templates, and endpoint names that tell the same story.

For example, the controller name points toward structure like:

- ``app/controllers/recipe_ingredient_controller.py``
- ``app/routes/recipes/ingredients/``
- ``app/templates/recipes/ingredients/``
- ``recipes.ingredients.index`` endpoint names 

The controller name is doing more than naming a Python class. It is describing
how the resource belongs in the application.

Go Nested with ``--crud``
-------------------------

.. youtube_embed:: go-nested-with-make-controller-crud

After a lot of build up let’s go back and build the nested relationship we
discussed above **Recipe -> Ingredient**.

If you are following along you should already have a  That means we want a nested controller:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud

With this one change, you get a lot of structural benefits:

- ``app/controllers/recipe_ingredient_controller.py``
- nested routes under ``app/routes/recipes/ingredients/``
- templates under ``app/templates/recipes/ingredients/``
- nested endpoint names like ``recipes.ingredients.index``

That last part matters a lot to me.

If ingredients belong to recipes, I want the route names, folder structure,
and controller name to read that way too. The app should tell the truth about
the relationship.

So instead of a flat route like:

- ``/ingredients``

you end up with a nested route shape:

- ``/recipes/<int:recipe_id>/ingredients``

And instead of a flat endpoint name, you preserve the nesting with:

.. code-block:: python

   url_for('recipes.ingredients.index', recipe_id=1)

That saves real mental energy later.

Now we need to nest, build out all RESTful action, and generate a model with.
Now that the model naming is clear, we can look at the more interesting case:
when one controller name can describe more than one valid structure.
