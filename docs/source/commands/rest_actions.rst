RESTful actions
===============

``Flask-Commands`` follows the seven RESTful actions. They is one for each
day of the week and they are forgivable 77 time over.

- ``index``
- ``show``
- ``create``
- ``store``
- ``edit``
- ``update``
- ``destroy`` (or ``delete`` if you prefer — frankly, I would have called it *nuke* 😜)

If you’re new to these actions (or just need a refresher), here’s a quick review
of what each one does and which HTTP method it uses.

There *are* other HTTP methods (PUT, PATCH, DELETE), but browsers traditionally
only understand GETs and POSTs. I always think of the browser lifecycle as:

**Get → Post → Redirect**

You *get* the page, you *post* a form, and then you *redirect* to a new page to
give feedback about what just happened.

.. table:: The Seven RESTful Actions

   ======= ====== ============================= ============================================================
   Action  Method URL Example                   Behavior
   ======= ====== ============================= ============================================================
   index   GET    /users                        Show all instances of a model
   show    GET    /users/<int:user_id>          Show a single instance
   create  GET    /users/create                 Show the page to create a new instance
   store   POST   /users/create                 Create a new instance (then redirect)
   edit    GET    /users/<int:user_id>/edit     Show the page to edit an instance
   update  POST   /users/<int:user_id>/edit     Update an instance (then redirect)
   destroy POST   /users/<int:user_id>/delete   Delete an instance (then redirect)
   ======= ====== ============================= ============================================================


.. youtube_embed:: 7M8sVz5rjZ4 "Flask Commands – Part 7: RESTful Actions"
