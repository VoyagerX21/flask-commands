flask make:model
================

.. youtube_embed:: intro-to-flask-make-model

``flask make:model`` is the quickest way to scaffold a model when the data is
the first part of the application you know for sure.

At its simplest, it creates a model file and registers it for you. But it can
also grow into much more. With ``--crud``, Flask-Commands can build the
controller, routes, and templates that wrap around that model so the rest of
the resource comes to life too.

That makes it useful in two very common situations:

- you know the data shape first and want a clean place to begin
- you want to grow a full resource outward from the model in one command

The bigger takeaway is that ``make:model`` is not only about creating a Python
class. It is a strong starting point when you are thinking from the data
outward. You know what kind of data structure your app needs to store, and
Flask-Commands helps build the surrounding structure from there.

Everything in these sections builds on itself one step at a time.

.. toctree::
   :maxdepth: 1
   :hidden:

   The Basics <make_model/the_basics>
   make:model --crud <make_model/crud>
   Flat vs Nested <make_model/flat_vs_nested>
