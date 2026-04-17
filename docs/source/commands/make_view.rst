flask make:view
===============

.. youtube_embed:: into-to-flask-make-view

``flask make:view`` is the quickest way to add a new page to your Flask app
without having to wire every piece by hand.

At its simplest, it creates a template file. But it can also generate the
route, controller, and even the model that go with that page when you want the
rest of the structure to come to life 👶.

That makes it useful in two very common situations:

- you want to spin up a page quickly and come back later to fill in the details
- you already know the page belongs to a real resource and you want Flask-Commands
  to scaffold the surrounding structure for you

The bigger takeaway is that ``make:view`` is not only about templates. It is a
good starting command when you are thinking from the page outward. You know
what screen you want, and Flask-Commands helps you build the route, controller,
and resource structure around your concept instead of forcing you to wire it all
by hand first.

Everything in these sections builds on itself one step at a time.

.. toctree::
   :maxdepth: 1
   :hidden:

   The Basics <make_view_basics>
   Model Prompt <make_view_model_prompt>
   GET vs POST for RESTful Actions <make_view_get_vs_post_for_restful_actions>
   Building the First Resource <building_the_first_resource>
   Nested Resources <nested_resources_with_make_view>
