flask make:controller
=====================

.. youtube_embed:: intro-to-flask-make-controller

``flask make:controller`` is the quickest way to scaffold controller behavior
for a resource when you already know the application logic belongs at the
controller layer.

At its simplest, it creates a controller class. But it can also generate
RESTful actions, routes, templates for the ``GET`` actions, and even the model
when you want the surrounding structure built with it.

That makes it useful in two very common situations:

- you already know the resource behavior you want and want the controller first
- you want all seven RESTful actions scaffolded without creating each one by hand

The bigger takeaway is that ``make:controller`` is not only about controller
files. It is a strong starting point when you are thinking from application
behavior outward.

Everything in these sections builds on itself one step at a time.

.. toctree::
   :maxdepth: 1
   :hidden:

   The Basics <make_controller/the_basics>
   Controllers and Models <make_controller/controllers_and_models>
   Flat vs Nested <make_controller/flat_vs_nested>
