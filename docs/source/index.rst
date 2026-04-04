.. flask-commands documentation master file, created by
   sphinx-quickstart on Mon Jan  5 23:04:44 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. raw:: html

   <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>

.. title:: Flask-Commands

.. raw:: html

    <section class="pt-1 text-center">
        <div class="mx-auto flex items-center justify-center gap-4">
            <img src="_static/flask-commands-logo.png" alt="Flask Commands logo" class="h-24 w-24 shrink-0 object-contain" />
            <div>
                <div class="text-[clamp(3rem,6vw,5.4rem)] leading-[0.95] tracking-[-0.04em] text-slate-800" style="font-family: 'Baskerville Old Face', 'Bookman Old Style', 'Palatino Linotype', 'Times New Roman', serif; font-weight: 600;">
                Flask-Commands
                </div>
            </div>
        </div>
    </section>

    <div class="mt-3 flex flex-wrap items-center justify-center gap-2">
        <a href="https://pypi.org/project/flask-commands/"><img src="https://img.shields.io/pypi/v/flask-commands.svg?cacheSeconds=300" alt="PyPI version badge" /></a>
        <a href="https://github.com/drewbutcher/flask-commands/actions"><img src="https://img.shields.io/github/actions/workflow/status/drewbutcher/flask-commands/tests.yml?branch=main" alt="Build status badge" /></a>
        <a href="https://codecov.io/gh/drewbutcher/flask-commands"><img src="https://codecov.io/gh/drewbutcher/flask-commands/branch/main/graph/badge.svg" alt="Coverage badge" /></a>
        <a href="https://flask-commands.readthedocs.io/"><img src="https://img.shields.io/readthedocs/flask-commands/latest" alt="Docs badge" /></a>
        <a href="https://github.com/drewbutcher/flask-commands/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/flask-commands.svg" alt="License badge" /></a>
        <a href="https://github.com/drewbutcher/flask-commands/stargazers"><img src="https://img.shields.io/github/stars/drewbutcher/flask-commands" alt="GitHub stars badge" /></a>
    </div>

    <div class="mt-4 mx-auto max-w-4xl bg-gradient-to-b from-slate-50 to-slate-100/90 p-4 rounded-2xl border border-slate-200 text-center">
        <p class="m-0 text-slate-700">
        Scaffold Flask projects, views, controllers, routes, and models in one line so you can skip the boilerplate wiring and get back to building your app.
        </p>
    </div>

    <div class="my-4 flex flex-wrap items-center justify-center gap-4">
        <a href="docs.html" class="shadow-md active:shadow-none! no-underline! bg-gradient-to-br from-violet-100 to-violet-200  text-indigo-800! flex items-start gap-2  font-extrabold px-4 py-2 rounded border-1 border-violet-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="block h-[22px] w-[22px] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M4 20h16"></path>
                <rect x="5" y="4" width="4" height="16" rx="1"></rect>
                <rect x="10" y="2" width="4" height="18" rx="1"></rect>
                <rect x="15" y="6" width="4" height="14" rx="1"></rect>
            </svg>
            <span>Read The Docs</span>
        </a>
        <a href="video_series.html" class="shadow-md active:shadow-none! no-underline! bg-gradient-to-r from-slate-100/80 to-slate-100 flex items-start gap-2  font-extrabold px-4 py-2 rounded border-1 border-slate-200 hover:text-[#0a7d91]! text-[#0a7d91]!">
            <svg xmlns="http://www.w3.org/2000/svg" class="block h-[22px] w-[22px] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M17 2 12 7 7 2"></path>
                <rect width="20" height="15" x="2" y="7" rx="2"></rect>
            </svg>
            <span>Browse YouTube Videos</span>
        </a>
    </div>

    <h1>Why Flask-Commands</h1>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 my-4">
        
        <div class="flex flex-col gap-2 bg-gradient-to-b from-slate-50 to-indigo-50 rounded-lg py-4 px-8 ring-1 ring-slate-200">
            <div class="flex gap-2 items-center">
                <div class="text-3xl ">⚡</div>
                <h3 class=" m-0">Fast Scaffolding</h3>
            </div>
            <p class="m-0 text-slate-600">One command scaffolds a working template wired to your applciation's data.</p>
        </div>

        <div class="flex flex-col gap-2 bg-gradient-to-b from-slate-50 to-indigo-50 rounded-lg py-4 px-8 ring-1 ring-slate-200">
            <div class="flex gap-2 items-center">
                <div class="text-3xl ">📂</div>
                <h3 class=" m-0">Plain Files</h3>
            </div>
            <p class="m-0 text-slate-600">Generated files stay plain, consistent, and easy to edit on disk, so you still own the app.</p>
        </div>
    
        <div class="flex flex-col gap-2 bg-gradient-to-b from-slate-50 to-indigo-50 rounded-lg py-4 px-8 ring-1 ring-slate-200">
            <div class="flex gap-2 items-center">
                <div class="text-3xl ">😇</div>
                <h3 class=" m-0">Honest Nesting</h3>
            </div>
            <p class="m-0 text-slate-600">Nested resources read truthfully in folders, routes, controllers, and endpoint names.</p>
        </div>

        <div class="flex flex-col gap-2 bg-gradient-to-b from-slate-50 to-indigo-50 rounded-lg py-4 px-8 ring-1 ring-slate-200">
            <div class="flex gap-2 items-center">
                <div class="text-3xl ">🧱</div>
                <h3 class=" m-0">Less Boilerplate</h3>
            </div>
            <p class="m-0 text-slate-600">Spend less time typing boilerplate code in your routes, controllers, views, and models.</p>
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
