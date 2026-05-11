The Basics of make:model
========================

Sometimes the cleanest place to begin is the data structure itself. If the 
model is the first structure you know your application will contain then  
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

If I was building the cooker application we have been working on from scratch.
I would start by thinking a cooking application will need a place to store 
all the recipes.  So my first through would be that we need ``Recipe`` model. 
The simplest way to scaffold out a model is with this command:

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
   without seeing the warning simply spin up a fresh project with 
   something like:

   .. code-block:: bash

      flask new example_model_the_basics
   
   then cd into your new project 

   .. code-block:: bash

      cd example_model_the_basics
   
   and now you can run your modle building command without any warnings

   .. code-block:: bash

      flask make:model Recipe

This generates:

- ``app/models/recipe.py``
- an registers the model in ``app/models/__init__.py``

The regisration part is important because it helps with clean imports into 
other parts of our application (mainly in controller files) and it helps 
Flask-Commands know about your applications data structures.  The last part 
becomes important when you start building relationship between data structures.

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
actually a small starting point.  This is one of the main feature in Flask-Commands 
that I wanted for myself.  Often when building out a new data structure the 
first mental hurdel was just sketching out the model file.  

Lets go though each line of this model file, and see it's actually very simple.
The first observation is to notice that a model is just a python class that 
extends ``db.Model``.  After declaring the class name we define the table name.
As a convention Flask-Commands using a plural version of the singular model.
After that there are three columns that every new model file ships with:

- ``id``
- ``created_at``
- ``updated_at``

The first column is ``id``.  The ``id`` column is your table unique identify 
and is used to make relationships between models.  The next two columns are 
timestamp columns, ``created_at`` and ``updated_at``.  When a new instance is 
made, in this case a new recipe, these timestamps are set to populate 
without you doing any additional work.  In addition, if you modify the instance
then the update_at will trigger a new timestamp and update the database if you 
save the changes to the database.  

Being able to save changes to the database is exactly where the last part of 
the model comes into play. In addition to the three columns there are three 
methods that finish off our class definition:

- ``store_in_database``
- ``delete_from_database``
- ``__repr__``

Once you have create a new model instance you can call ``store_in_database`` to 
push that new data onto the database.  In addion, if you change the value of 
an instances attribute you can use ``store_in_database`` up persist that change 
in the database. 

If you ever need to remove an instance from the database the 
``delete_from_database`` will remove the row of data.

Finally, ``__repr__`` is a great tool for debugging and is the magic 🪄 method
that runs when you print a model's instance.      

This gives you a clean base to build from, but is by no means a complete data
structure.  You will have to fill out all your additional data columns that 
are needed to make the data structure meaningful.  Let's look at how we might
edit a structure in the nest section.

Edit the Model and Migrate the Database
---------------------------------------

.. youtube_embed:: edit-the-model-and-migrate-the-database

At some point you will want to add new columns to the model.  

For example, you might update ``Recipe`` to include a ``name`` column by adding
the following line of code:

.. code-block:: python

   name = db.Column(db.String(128), nullable=False)

Changing the Python model file does not automatically change the database 
schema by itself.  That is where a database migration come into play.  

.. admonition:: Thank you Miguel Grinberg for Flask-Migrate

   Thanks to Miguel Grinberg we can use 
   `Flask-Migrate <https://flask-migrate.readthedocs.io/>`_ to make this 
   process seemless!  Miguel's package Flask-Migrate is amazing at keeping 
   track of all the database changes and applying them so you only have to 
   view one file, your model file.  If you use Flask-Commands 
   ``flask new myproject`` to build your application then Flask-Migrate is 
   already wired up otherwise you will need to visit Miguel's documentation 
   on how to wire up Flask-Migrate.  

Once you update the model, you can easily generate a migration using the 
following terminal commands:

.. code-block:: bash

   flask db migrate -m "Add name to recipe"
   flask db upgrade

That is the Flask-Migrate part of the workflow, and it is one of the reasons I
like the default project scaffold so much. package is already
wired in for you.

One small note: this only applies to the default database-enabled project. If
you created the project with ``flask new myproject --no-db``, then the
database and migration pieces are intentionally not there.

Once the model exists, the next step gets more interesting: letting ``--crud``
build the rest of the resource around it.
