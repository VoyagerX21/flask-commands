Generating Controllers (flask make:controller)
==============================================

A simple controller
-------------------

Use ``flask make:controller`` to scaffold a controller class under
``app/controllers/`` and register it in ``app/controllers/__init__.py``.

.. code-block:: bash

   flask make:controller RecipeController

This creates ``app/controllers/recipe_controller.py`` with a class stub:

.. code-block:: python

   class RecipeController:
       pass

In fact, if you are following this tutorial from the beginning, you should receive a warning that this controller already exists. It does, and it's much better than a simple class with a ``pass``. Question: So why would we use the ``make:controller`` command? One answer: You might create a new set of routes that you need a plain controller for the logic.  But I love flags so let's see some real scaffolding come into play.


A Controller with RESTful actions (--crud)
------------------------------------------

Life is all about the options and ``--crud`` is a life saving option. This
option produces injects the seven RESTful actions, into the controller file,
and the routes, plus it wires everything up with matching templates.

For our cooking website suppose we need to have an 'ingredient' object. Here
is one way to wire up a ton of content ready to use right away with the
following command:


.. code-block:: bash

   flask make:controller IngredientController --crud

With the ``--crud`` flag you receive:

- A controller file under ``app/controllers/ingredient_controller.py`` with all
  seven RESTful methods ready for you.
- The controller file registered propertly in ``app/controllers/__init__.py``.
- A blueprint routes file under ``app/routes/ingredients``
- The routes file contains all seven RESTful routes.
- The new blueprint registered with the create_app in ``app/__init__.py``
- Four templates under ``app/templates/ingredients`` (``index``, ``show``,
  ``create``, ``edit``).

Here is what the controller file looks like:

.. code-block:: python

   from flask import render_template
   from flask import redirect, url_for

   class IngredientController:

       @staticmethod
       def index() -> str:
           return render_template('ingredients/index.html')

       @staticmethod
       def show(ingredient_id: int) -> str:
           return render_template('ingredients/show.html')

       @staticmethod
       def create() -> str:
           return render_template('ingredients/create.html')

       @staticmethod
       def store() -> str:
           return redirect(url_for('ingredients.index'))

       @staticmethod
       def edit(ingredient_id: int) -> str:
           return render_template('ingredients/edit.html')

       @staticmethod
       def update(ingredient_id: int) -> str:
           return redirect(url_for('ingredients.index'))

       @staticmethod
       def destroy(ingredient_id: int) -> str:
           return redirect(url_for('ingredients.index'))

Here is what the routes file looks like:

.. code-block:: python

   from app.controllers import IngredientController
   from app.routes.ingredients import bp

   @bp.route('/ingredients', methods=['GET'])
   def index():
       return IngredientController.index()

   @bp.route('/ingredients/<int:ingredient_id>', methods=['GET'])
   def show(ingredient_id: int):
       return IngredientController.show(ingredient_id)

   @bp.route('/ingredients/create', methods=['GET'])
   def create():
       return IngredientController.create()

   @bp.route('/ingredients', methods=['POST'])
   def store():
       return IngredientController.store()

   @bp.route('/ingredients/<int:ingredient_id>/edit', methods=['GET'])
   def edit(ingredient_id: int):
       return IngredientController.edit(ingredient_id)

   @bp.route('/ingredients/<int:ingredient_id>', methods=['POST'])
   def update(ingredient_id: int):
       return IngredientController.update(ingredient_id)

   @bp.route('/ingredients/<int:ingredient_id>/delete', methods=['POST'])
   def destroy(ingredient_id: int):
       return IngredientController.destroy(ingredient_id)

This is awesome!!! I can litterly see you jumping up and down shouting with
celebration in joy 🥳.  But wait, what about an **Ingrediant model**?

A controller with a Model (-m / --model)
----------------------------------------

Often a controller is tied to a model, like in your ingredient example. You
have two options here you can either use an optional variable ``--model``
or have Flask-Commands infer your model with a generator flag ``-m``.   The
following two commands are equivlant

.. code-block:: bash

   flask make:controller IngredientController --model Ingredient

and

.. code-block:: bash

   flask make:controller IngredientController -m

both will sub out a plain Ingredient controller class and an Ingrediant model.

Here is what the controller file looks like:

.. code-block:: python

   class IngredientController:
       pass

Here is what the model file looks like:

.. code-block:: python

   from app import db
   from datetime import datetime, timezone

   class Ingredient(db.Model):
       __tablename__ = 'ingredients'
       # Columns
       id = db.Column(db.Integer, primary_key=True)
       created_at = db.Column(db.DateTime(timezone=True),
                           index=True,
                           default=lambda: datetime.now(timezone.utc))
       updated_at = db.Column(db.DateTime(timezone=True),
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

       def store_in_database(self):
           db.session.add(self)
           db.session.commit()

       def delete_from_database(self):
           db.session.delete(self)
           db.session.commit()

       def __repr__(self):
           """Model representation for Code Debugging"""
           return f'<Ingredient id:{self.id}>'

Ok now you are all set to combine these optional variables and create nested
datastructures, right 🤔?  What did I hear you say, you want all the RESTful
actions nested over multiple models!!!!  Ya, of course you want to connect a
recipe to it's ingrediants with RESTful actions.

Nested Controllers with --crud
------------------------------

If we wanted to build the relationship **Recipe → Ingredient** Flask-Commands is
up for the task.  In this case we would PascalCase case (UppserCamelCase)
the controller and then add the crud flag as in this command:

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud

With this small change you recieve a lot of structure benefits in your code.

- A controller file under ``app/controllers/recipe_ingredient_controller.py``  with all seven RESTful methods ready for you.
    - The controller file registered propertly in ``app/controllers/__init__.py``.
- A blueprint routes folder under ``app/routes/recipes/ingredients``
    - The routes file contains all seven RESTful routes.
    - The new ingredients blueprint registered in the recipes blueprint
- Four templates under ``app/templates/recipes/ingredients`` (``index``, ``show``, ``create``, ``edit``).


Here is what the controller file looks like:

.. code-block:: python

   from flask import render_template
   from flask import redirect, url_for

   class RecipeIngredientController:

       @staticmethod
       def index(recipe_id: int) -> str:
           return render_template('recipes/ingredients/index.html')

       @staticmethod
       def show(recipe_id: int, ingredient_id: int) -> str:
           return render_template('recipes/ingredients/show.html')

       @staticmethod
       def create(recipe_id: int) -> str:
           return render_template('recipes/ingredients/create.html')

       @staticmethod
       def store(recipe_id: int) -> str:
           return redirect(url_for('recipes.ingredients.index', recipe_id=recipe_id))

       @staticmethod
       def edit(recipe_id: int, ingredient_id: int) -> str:
           return render_template('recipes/ingredients/edit.html')

       @staticmethod
       def update(recipe_id: int, ingredient_id: int) -> str:
           return redirect(url_for('recipes.ingredients.index', recipe_id=recipe_id))

       @staticmethod
       def destroy(recipe_id: int, ingredient_id: int) -> str:
           return redirect(url_for('recipes.ingredients.index', recipe_id=recipe_id))

Here is what the routes file looks like:

.. code-block:: python

   from app.controllers import RecipeIngredientController
   from app.routes.recipes.ingredients import bp

   @bp.route('/recipes/<int:recipe_id>/ingredients', methods=['GET'])
   def index(recipe_id: int):
       return RecipeIngredientController.index(recipe_id)

   @bp.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>', methods=['GET'])
   def show(recipe_id: int, ingredient_id: int):
       return RecipeIngredientController.show(recipe_id, ingredient_id)

   @bp.route('/recipes/<int:recipe_id>/ingredients/create', methods=['GET'])
   def create(recipe_id: int):
       return RecipeIngredientController.create(recipe_id)

   @bp.route('/recipes/<int:recipe_id>/ingredients', methods=['POST'])
   def store(recipe_id: int):
       return RecipeIngredientController.store(recipe_id)

   @bp.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>/edit', methods=['GET'])
   def edit(recipe_id: int, ingredient_id: int):
       return RecipeIngredientController.edit(recipe_id, ingredient_id)

   @bp.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>', methods=['POST'])
   def update(recipe_id: int, ingredient_id: int):
       return RecipeIngredientController.update(recipe_id, ingredient_id)

   @bp.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>/delete', methods=['POST'])
   def destroy(recipe_id: int, ingredient_id: int):
       return RecipeIngredientController.destroy(recipe_id, ingredient_id)

If you are missing all the recipe_id's it's because you are missing the recipe
model.  From the top you would do

.. code-block:: bash

   flask make:controller RecipeController --crud -m

Notice the ``-m`` generator flag to create the Recipe Model, and then you would follow it with the command from above (probably with a model generator flag)

.. code-block:: bash

   flask make:controller RecipeIngredientController --crud -m

Wrap-up
-------

That is the controller story in brief: start simple, add ``--crud`` when you
want the full set of actions, and use ``-m`` when you want a matching model
scaffolded alongside the controller. The next command, ``flask make:model``,
will cover the rest of the story and make those relationships flag generators feel
feel deliberate rather than accidental.
