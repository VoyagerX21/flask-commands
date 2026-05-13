The Basics of make:model
========================

Sometimes the cleanest place to begin is the data structure itself. If the 
model is the first structure you know your application will contain, then  
``flask make:model`` is a very nice place to start.  

If you are newer to web development, a model is the part of your web 
application that stores your data in a structured way.  This approach is 
especially useful when the data shape is the clearest thing in
your head and you want to start there before thinking about controllers,
routes, or views.  As a data engineer and mathematican, this is where I 
find myself starting a project. 

Make a Basic Model
------------------

.. youtube_embed:: make-a-basic-model

If I was building the cooker application we have been working on from scratch,
I would start by thinking, *"A cooking application will need a place to store 
all the recipes."*  Consequently, my first thought would be to build a 
``Recipe`` model. The simplest way to scaffold out a model is with 
this command:

.. code-block:: bash

   flask make:model Recipe


.. admonition:: For those following along

   If you have been following this documentation from the beginning, you already 
   created a ``Recipe`` model earlier.  We did this either with 
   ``flask make:view recipes.index -rcm`` or 
   ``flask make:controller RecipeController --crud -m``.  Because of this you are 
   receiving a warning in the terminal saying that the ``Recipe`` model already 
   exists.

   .. rst-class:: terminal-warning
   .. code-block:: text

      ⚠️  Warning: Model Already Exists
         - Model Recipe already exists
         - No changes were made to the existing model

      ⚠️  Warning: One or more make model steps produced a warning or failure.

   Don't be alarmed if you see this, it's **not a problem**.  This warning 
   means Flask-Commands is protecting the file that already exists instead
   of overwriting it.    

   If you are seeing this warning and you would like to run the above command 
   without the warning simply spin up a fresh project with 
   something like:

   .. code-block:: bash

      flask new example_model_the_basics
   
   then cd into your new project 

   .. code-block:: bash

      cd example_model_the_basics
   
   and now you can run your model building command without any warnings

   .. code-block:: bash

      flask make:model Recipe

This generates:

- ``app/models/recipe.py``
- an registers the model in ``app/models/__init__.py``

The regisration part is important because it helps with clean imports into 
other parts of our application, mainly in controller files.  It also helps 
Flask-Commands locate your application's data structures.  We have already
seen how import it is for Flask-Commands to know about your data structure when
you ask Flask-Commands to generate models based on relationship between the
data structures.  But i'm getting ahead of myself, for now let's take a 
closer look at the model file and see what we can do with a freshly generated 
model file.

What the Model Includes
-----------------------

.. youtube_embed:: what-the-model-includes

Let's look at the model file ``app/models/recipe.py`` that was generated 
for us and understand each line.  

.. code-block:: python

   from app import db
   from datetime import datetime, timezone

   class Recipe(db.Model):
      __tablename__ = 'recipes'

      # Columns
      id = db.Column(db.Integer, primary_key=True)
      created_at = db.Column(db.DateTime(timezone=True),
                              index=True, 
                              default=lambda: datetime.now(timezone.utc))
      updated_at = db.Column(db.DateTime(timezone=True),
                              default=lambda: datetime.now(timezone.utc), 
                              onupdate=lambda: datetime.now(timezone.utc))

      # Methods
      def store_in_database(self):
         db.session.add(self)
         db.session.commit()

      def delete_from_database(self):
         db.session.delete(self)
         db.session.commit()

      def __repr__(self):
         """Model representation for Code Debugging"""
         return f'<Recipe id:{self.id}>'



While the generated model file might look a little scary 🫣 at first, it is 
actually a small starting point.  This is one of the main features in 
Flask-Commands that I wanted for myself.  Often when building out a new 
data structure, the first mental hurdle is just sketching out the model 
file structure.  

Let's go though each line of this model file, and debunk the mystery.
The first observation is to notice that a model is just a python class that 
extends ``db.Model``.  After declaring the class name we define the table name.
As a convention Flask-Commands using a plural version of the singular model 
name.  After that there are three columns that every new model file ships with:

- ``id``
- ``created_at``
- ``updated_at``

The first column is an integer column called ``id``.  The ``id`` column 
is your table unique identify on each row in your table, and is used to
make relationships between models.  The next two columns are datetime columns:
``created_at``and ``updated_at``.  When a new instance is created and stored in 
the database, these datetimes are set to populate without you doing any 
additional work.  In addition, if you modify the instance, ``update_at`` 
will receive a new timestamp when you save the changes to the database.

Being able to save changes to the database is exactly where the last part of 
the model comes into play. In addition to the three columns, there are three 
methods that finish off our class definition:

- ``store_in_database``
- ``delete_from_database``
- ``__repr__``

Once you have create a new model instance, you can call ``store_in_database`` 
to push that new data onto the database.  In addition, if you change any of the
instances attributes you can use ``store_in_database`` again to persist 
those change in the database. 

If you ever need to remove an instance from the database, 
``delete_from_database`` will remove the row of data.

Finally, ``__repr__`` is a great tool for debugging.  It is the magic 🪄 method
that runs when you print a model instance.      

This gives you a clean base to build from, but is by no means a complete data
structure.  You will have to fill out all your additional columns that 
are needed to make the data structure meaningful.  In the next sections we look
at how we might edit a models structure so that we can create, edit, and delete
instances of the model all while saving the changes to our application's 
database.

Edit the Model and Migrate the Database
---------------------------------------

.. youtube_embed:: edit-the-model-and-migrate-the-database

At some point you will want to modify your model by adding new columns, changing
the structure of your columns, or deleting columns.  

I will briefly demonstrate how to add a column to a model, and then I will send 
you off to lean more about model manipulation for other sources as this is not 
a feature of Flask-Commands.

In our ``Recipe`` model lets update the columns by adding a ``name`` column.  
To do this we just add the following line of code to the model class.

.. code-block:: python

   name = db.Column(db.String(128), nullable=False)

That was easy; however, changing the Python model file does not automatically 
change the database schema by itself.  That is where a database migration 
comes into play.  

.. admonition:: Thank you Miguel Grinberg for Flask-Migrate

   Thanks to Miguel Grinberg we can use 
   `Flask-Migrate <https://flask-migrate.readthedocs.io/>`_ to make this 
   process seemless!  Miguel's package Flask-Migrate is amazing at keeping 
   track of all the database changes and applying them,  so you can focus on 
   the final shape of your model file.  
   
   If you use. ``flask new myproject`` to build your application, then 
   Flask-Migrate is already wired up.  Otherwise, you will need to visit
   Miguel's documentation to lean how to wire up Flask-Migrate.  

Once you update the model, you can easily generate a migration using the 
following terminal commands:

.. code-block:: bash

   flask db migrate -m "Add name to recipe"
   flask db upgrade

That is the Flask-Migrate part of the workflow, and it is one of the reasons I
like the default project scaffold so much.  When you ran ``flask new myproject``
Flask-Commands wires up Flask-Migrate and Flask-SQLAlchemy for you so you can
just focus on your application's database development. 

One small note: this only applies to the default database-enabled project. If
you created the project with ``flask new myproject --no-db``, then the
database and migration pieces are intentionally not there.

Create, Update, and Delete a Recipe
-----------------------------------

Now that the model has a ``name`` column and the database has been migrated,
we can use the model to start building out real instances and persist them 
in our database 🥳.

As we saw in the :ref:`Run the New Project <run-the-new-project>`
section of Starting a Project, the easiest way to start the application is to
cd into the root project directory and run:

.. code-block:: bash

   ./run.sh

That helper starts the application and opens a Flask shell for you in a
separate terminal window.

If you prefer, you can do this manually by activating your virtual
environment running ``flask shell``.  In other words, first cd into your 
project's root directory run the following commands:

.. code-block:: bash

   source venv/bin/activate
   flask shell

Inside the flask shell, there is some magic happening for you that gives you 
instant access to all your models without have to write import statements.  Normally,
to access a model, you would have to write something like 
``from app.models import Recipe``.  However, with the way Flask-Commands sets
up your project, and with the default settings of Flask-SQLAlchemy, everything 
just works!  

For those interested, the magic details are as follows:

- First, the generated project imports ``app.models`` during app startup in 
  ``create_app`` found in  ``app/__init__.py``. 
- That makes registered models like ``Recipe`` known to Flask-SQLAlchemy.
- Then, according to the 
  `Flask-SQLAlchemy documentation <https://flask-sqlalchemy.palletsprojects.com/en/stable/api/>`_ 
  the ``add_models_to_shell`` attribute is set to ``True`` by default, which 
  means our models are all adds to ``flask shell`` automatically.

The shorten version is once you are inside the Flask shell, you can type
``Recipe`` and the interprator will know that this is your ``Recipe`` model.  

Without further delay let's now create a ``Recipe`` instance by making a 
salad recipe:

.. code-block:: pycon

   >>> recipe = Recipe(name='salad')
   >>> print(recipe)
   <Recipe id:None>

Before the recipe is stored, ``id`` is ``None`` because the database has not
created a row for it yet. By typing ``print(recipe)`` show the friendly 
debugging representation from ``__repr__``.

Now let's store this instance in the database and see the ``id`` column 
populate:

.. code-block:: pycon

   >>> recipe.store_in_database()
   >>> print(recipe)
   <Recipe id:1>
   >>> Recipe.query.count()
   1

Once the recipe is committed to the database, it has an ``id``. That is the
database saying, "I know this instance and I have it assigned it to row 1."

We can also see ``updated_at`` do its quiet little bit of magic 🪄. First, save
the current timestamp:

.. code-block:: pycon

   >>> original_updated_at = recipe.updated_at
   >>> original_updated_at
   datetime.datetime(2026, 5, 12, 9, 55, 58, 577798)

Now let's change the recipe's name and see if ``updated_at`` changes.

.. code-block:: pycon

   >>> recipe.name = 'fruit salad'
   >>> recipe.updated_at
   datetime.datetime(2026, 5, 12, 9, 55, 58, 577798)

Notice that ``updated_at`` has not changed yet. We changed the Python object,
but we have not committed that change to the database.

When we store the recipe again, SQLAlchemy applies the ``onupdate`` value:

.. code-block:: pycon

   >>> recipe.store_in_database()
   >>> recipe.updated_at
   datetime.datetime(2026, 5, 12, 9, 57, 32, 343438)
   >>> recipe.updated_at > original_updated_at
   True

Finally, we can delete the recipe:

.. code-block:: pycon

   >>> recipe.delete_from_database()
   >>> print(recipe)
   <Recipe id:1>
   >>> Recipe.query.count()
   0

The Python object still exists in memory, so ``recipe`` can still print as
``<Recipe id:1>``. But the database row is gone, which is why
``Recipe.query.count()`` returns ``0``.


Once the model exists, the next step gets more interesting: letting ``--crud``
build the rest of the resource around it.
