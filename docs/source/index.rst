.. flask-commands documentation master file, created by
   sphinx-quickstart on Mon Jan  5 23:04:44 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. title:: Flask-Commands

.. raw:: html

   <section class="landing-hero-card">
     <div class="landing-brand-row">
       <img src="_static/flask-commands-logo.png" alt="Flask Commands logo" class="landing-brand-mark" />
       <div class="landing-brand-text">
         <div class="landing-brand-name">Flask-Commands</div>
       </div>
     </div>
   </section>

|pypi| |tests| |coverage| |docs| |license| |stars|

.. |pypi| image:: https://img.shields.io/pypi/v/flask-commands.svg?cacheSeconds=300&v=|release|
   :target: https://pypi.org/project/flask-commands/
.. |tests| image:: https://img.shields.io/github/actions/workflow/status/drewbutcher/flask-commands/tests.yml?branch=main
   :target: https://github.com/drewbutcher/flask-commands/actions
.. |coverage| image:: https://codecov.io/gh/drewbutcher/flask-commands/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/drewbutcher/flask-commands
.. |docs| image:: https://img.shields.io/readthedocs/flask-commands/latest
   :target: https://flask-commands.readthedocs.io/
.. |license| image:: https://img.shields.io/pypi/l/flask-commands.svg
   :target: https://github.com/drewbutcher/flask-commands/blob/main/LICENSE
.. |stars| image:: https://img.shields.io/github/stars/drewbutcher/flask-commands
   :target: https://github.com/drewbutcher/flask-commands/stargazers

.. raw:: html

   <div class="landing-promise-card">
     <p>
       Scaffold Flask projects, views, controllers, routes, and models in one line
       so you can skip the boilerplate wiring and get back to building your app.
     </p>
   </div>

   <div class="landing-actions">
     <a class="landing-button landing-button-primary" href="docs.html">
       <span class="landing-button-content">
         <svg class="landing-button-icon" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
           <path d="M4 20h16" />
           <rect x="5" y="4" width="4" height="16" rx="1" />
           <rect x="10" y="2" width="4" height="18" rx="1" />
           <rect x="15" y="6" width="4" height="14" rx="1" />
         </svg>
         <span>Read the docs</span>
       </span>
     </a>
     <a class="landing-button landing-button-secondary" href="video_series.html">
       <span class="landing-button-content">
         <svg class="landing-button-icon" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
           <path d="m17 2-5 5-5-5" />
           <rect width="20" height="15" x="2" y="7" rx="2" />
         </svg>
         <div class="mt-1">Browse YouTube videos</div>
       </span>
     </a>
   </div>

Why Flask-Commands
------------------

.. raw:: html

   <div class="landing-feature-grid">
     <div class="landing-feature-card">
       <div class="landing-feature-heading">
         <div class="landing-feature-icon">⚡</div>
         <h3>Fast Scaffolding</h3>
       </div>
       <p>One command can generate a real slice of working Flask structure.</p>
     </div>
     <div class="landing-feature-card">
       <div class="landing-feature-heading">
         <div class="landing-feature-icon">📂</div>
         <h3>Plain Files</h3>
       </div>
       <p>Generated code stays plain and readable on disk so you still own the app.</p>
     </div>
     <div class="landing-feature-card">
       <div class="landing-feature-heading">
         <div class="landing-feature-icon">😇</div>
         <h3>Honest Nesting</h3>
       </div>
       <p>Nested resources read truthfully in folders, routes, controllers, and endpoint names.</p>
     </div>
     <div class="landing-feature-card">
       <div class="landing-feature-heading">
         <div class="landing-feature-icon">⏱️</div>
         <h3>Save Time</h3>
       </div>
       <p>You spend less time wiring boilerplate blueprint routes, controllers, and view and more time building your application.</p>
     </div>
   </div>

Quick Start
-----------

The fastest way to feel what Flask-Commands does is to watch one command
generate a real resource and see the output for yourself.

Start a new project:

.. code-block:: bash

   flask new myproject

Then move into the project and generate a posts resource:

.. code-block:: bash

   flask make:view posts.index -rcm

Actual terminal output from ``flask make:view posts.index -rcm``:

.. code-block:: text

   $ flask make:view posts.index -rcm

   💡 Info: Generated From Flags
       - Generated controller PostController
       - Generated model Post
       - Generated route /posts

   ✅ Success: Created New Model
       - Created model Post at app/models/post.py
       - Registered Post model at app/models/__init__.py
   ✅ Success: Created New View
       - Added view file at app/templates/posts/index.html

   ✅ Success: Created Controller Class With Method
       - Created a new controller called PostController
       - Added method index to controller
       - Registered PostController at app/controllers/__init__.py
       - New controller located at app/controllers/post_controller.py

   ✅ Success: Created New Route Directory
       - Created __init__.py at app/routes/posts/__init__.py
       - Created routes.py at app/routes/posts/routes.py
       - Registered the new route directory as posts_blueprint at app/__init__.py
       - Visit the new route at /posts
       - Reference this route with url_for('posts.index')

That is the part I want people to feel right away: one command and a ton of
the boring structure is already laid out and connected for you.

Generate a Full CRUD Resource
-----------------------------

If you want the full resource story in one shot, this is where things get
especially satisfying.

Use:

.. code-block:: bash

   flask make:model Post --crud

That one command creates the model, controller, route wiring, and the GET
templates for the full RESTful resource.

Actual terminal output from ``flask make:model Post --crud``:

.. code-block:: text

   $ flask make:model Post --crud

   ✅ Success: Created Controller Class
       - Created a new controller called PostController
       - New controller located at app/controllers/post_controller.py
       - Registered PostController at app/controllers/__init__.py
       - Added controller methods: index, show, create, store, edit, update, destroy

   ✅ Success: Created New Model
       - Created model Post at app/models/post.py
       - Registered Post model at app/models/__init__.py

   ✅ Success: Created New Route Directory
       - Created __init__.py at app/routes/posts/__init__.py
       - Created routes.py at app/routes/posts/routes.py
       - Registered the new route directory as posts_blueprint at app/__init__.py
       - Added route functions: index, show, create, store, edit, update, destroy

   ✅ Success: Generated CRUD Wiring
       - index (GET)
         Added view file at app/templates/posts/index.html
         Visit the new route at /posts
         Reference this route with url_for('posts.index')
       - show (GET)
         Added view file at app/templates/posts/show.html
         Visit the new route at /posts/1
         Reference this route with url_for('posts.show', post_id=1)
       - create (GET)
         Added view file at app/templates/posts/create.html
         Visit the new route at /posts/create
         Reference this route with url_for('posts.create')
       - store (POST)
         Reference this route with url_for('posts.store')
       - edit (GET)
         Added view file at app/templates/posts/edit.html
         Visit the new route at /posts/1/edit
         Reference this route with url_for('posts.edit', post_id=1)
       - update (POST)
         Reference this route with url_for('posts.update', post_id=1)
       - destroy (POST)
         Reference this route with url_for('posts.destroy', post_id=1)

That is a lot of working structure from one command, and that is exactly the
kind of trade Flask-Commands is trying to give you.

.. toctree::
   :hidden:

   Docs <docs>
   Videos <video_series>
