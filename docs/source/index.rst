.. flask-commands documentation master file, created by
   sphinx-quickstart on Mon Jan  5 23:04:44 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. raw:: html

   <style>
    
        .bd-main .bd-content .bd-article-container {
            max-width: none !important;
            padding-left: 0px !important;
            padding-right: 0px !important;
            width: 100% !important;
        }
        .bd-article-container {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }

        .bd-article {
            padding: 0 !important;
        }

        @media (min-width: 960px) {
            .bd-page-width {
                max-width: none !important;
            }
            .bd-header__inner.bd-page-width {

                max-width: 88rem !important;
            }
        }

        .bd-container {
            padding: 0px !important;
            margin: 0px !important;
            width: 100%;
        }
        .right-next {
            display: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }
    </style>

.. title:: Flask-Commands

.. raw:: html

    <div class="p-4 relative isolate bg-gradient-to-b from-slate-50 to-slate-100/90 lg:max-h-[600px] overflow-hidden dark:to-slate-800 dark:from-slate-800 dark:to-slate-900 ">
        <div class="max-w-6xl mx-auto ">
            <section class="pt-4 text-center">
                <div class="mx-auto flex items-center justify-center gap-4 ">
                    <img src="_static/flask-commands-logo.png" alt="Flask Commands logo" class="h-24 w-24 shrink-0 only-light" />
                    <img src="_static/flask-commands-logo.png" alt="Flask Commands logo" class="h-24 w-24 shrink-0 only-dark " />
                    <div>
                        <div class="text-[clamp(3rem,6vw,5.4rem)] leading-none text-slate-800 dark:text-slate-100" style="font-family: 'American Typewriter', 'Rockwell', 'Bookman Old Style', 'Georgia', 'Cambria', 'Palatino Linotype', 'Book Antiqua', serif; font-weight: 400;">
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

            <section class="flex flex-col lg:flex-row mt-4 gap-0 lg:gap-8">
                <div class="flex-1">
                    <h1 class="text-6xl! dark:text-slate-100!">Scaffold Flask apps in seconds.</h1>
                    <div class="mt-4 mx-auto max-w-4xl ">
                        <p class="m-0 text-slate-700 dark:text-slate-100">
                            Skip the boilerplate and get straight to coding.
                            Flask-Commands plugs into Flask’s CLI so you can scaffold projects and app
                            structure without a separate toolchain.
                        </p>
                    </div>
                    <div class="my-4 flex flex-col md:flex-row items-stretch  gap-2 items-center justify-center md:gap-4 whitespace-nowrap">
                        <a href="docs.html" class="no-underline! bg-gradient-to-br from-violet-100 to-violet-200  text-indigo-800! flex items-start justify-center gap-2  font-extrabold px-4 py-2 rounded border-1 border-violet-200">
                            <svg xmlns="http://www.w3.org/2000/svg" class="block h-[22px] w-[22px] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                <path d="M4 20h16"></path>
                                <rect x="5" y="4" width="4" height="16" rx="1"></rect>
                                <rect x="10" y="2" width="4" height="18" rx="1"></rect>
                                <rect x="15" y="6" width="4" height="14" rx="1"></rect>
                            </svg>
                            <span>Read The Docs</span>
                        </a>
                        <a href="video_series.html" class="no-underline! bg-gradient-to-r from-slate-100/80 to-slate-100 flex items-start justify-center gap-2  font-extrabold px-4 py-2 rounded border-1 border-slate-200 hover:text-[#0a7d91]! text-[#0a7d91]!">
                            <svg xmlns="http://www.w3.org/2000/svg" class="block h-[22px] w-[22px] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                <path d="M17 2 12 7 7 2"></path>
                                <rect width="20" height="15" x="2" y="7" rx="2"></rect>
                            </svg>
                            <span>Browse YouTube Videos</span>
                        </a>
                    </div>
                </div>

                <div class="min-w-0 w-full lg:max-w-xl font-mono text-sm bg-slate-50 p-4 rounded-md border border-slate-200 dark:border-black! bg-black text-white">
                    <div class="overflow-hidden text-ellipsis whitespace-pre">% flask make:model Post --crud</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">✅ Success: Created Controller Class</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - Created a new controller called PostController</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - New controller located at app/controllers/post_controller.py</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - Registered PostController at app/controllers/__init__.py</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - Added controller methods: index, show, create, store, edit, update, destroy</div>
                    <div class="h-4"></div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">✅ Success: Created New Model</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - Created model Post at app/models/post.py</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - Registered Post model at app/models/__init__.py</div>
                    <div class="h-4"></div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">✅ Success: Created New Route Directory</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - Created __init__.py at app/routes/posts/__init__.py</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - Created routes.py at app/routes/posts/routes.py</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - Registered the new route directory as posts_blueprint at app/__init__.py</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - Added route functions: index, show, create, store, edit, update, destroy</div>
                    <div class="h-4"></div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">✅ Success: Generated CRUD Wiring</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - index (GET)</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Added view file at app/templates/posts/index.html</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Visit the new route at /posts</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Reference this route with url_for('posts.index')</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - show (GET)</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Added view file at app/templates/posts/show.html</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Visit the new route at /posts/1</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Reference this route with url_for('posts.show', post_id=1)</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - create (GET)</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Added view file at app/templates/posts/create.html</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Visit the new route at /posts/create</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Reference this route with url_for('posts.create')</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - store (POST)</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Reference this route with url_for('posts.store')</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - edit (GET)</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Added view file at app/templates/posts/edit.html</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Visit the new route at /posts/1/edit</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Reference this route with url_for('posts.edit', post_id=1)</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - update (POST)</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Reference this route with url_for('posts.update', post_id=1)</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">    - destroy (POST)</div>
                    <div class="overflow-hidden text-ellipsis whitespace-pre">      Reference this route with url_for('posts.destroy', post_id=1)</div>
                </div>
            </section>
        </div>
        <div aria-hidden="true" class="hidden lg:block pointer-events-none absolute inset-x-0 bottom-0 h-[80px] bg-gradient-to-b from-white/0 to-white dark:to-slate-900"></div>

    </div>

    <div class="dark:bg-slate-900 dark:border dark:border-slate-900 p-4">
        <div class="max-w-6xl  mx-auto">
            <section>
                <h2 class="dark:text-slate-100!">Why Flask-Commands?</h2>
                <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 ">
                    <div class="flex flex-col gap-2 bg-gradient-to-b from-slate-50 to-indigo-50 rounded-lg py-4 px-8 border-1 border-slate-200 dark:from-slate-600 dark:to-black dark:border-slate-900">
                        <div class="flex gap-2 items-center">
                            <div class="text-3xl ">⚡</div>
                            <h3 class="m-0">Fast Scaffolding</h3>
                        </div>
                        <p class="m-0 text-slate-600">Commands for scaffold a working Flask project, and wiring your application's data.</p>
                    </div>
                    <div class="flex flex-col gap-2 bg-gradient-to-b from-slate-50 to-indigo-50 rounded-lg py-4 px-8 border-1 border-slate-200 dark:from-slate-600 dark:to-black dark:border-slate-900">
                        <div class="flex gap-2 items-center">
                            <div class="text-3xl ">📂</div>
                            <h3 class="m-0">Plain Files</h3>
                        </div>
                        <p plass="m-0 text-slate-600">Generated clean files ready to edit so you still own your appilcation's files.</p>
                    </div>
                    <div class="flex flex-col gap-2 bg-gradient-to-b from-slate-50 to-indigo-50 rounded-lg py-4 px-8 border-1 border-slate-200 dark:from-slate-600 dark:to-black dark:border-slate-900">
                        <div class="flex gap-2 items-center">
                            <div class="text-3xl ">😇</div>
                            <h3 class="m-0">Honest Nesting</h3>
                        </div>
                        <p class="m-0 text-slate-600">Neatly nested structure for routes, models, and controllers that represent your data structures.</p>
                    </div>
                    <div class="xl:col-span-3 flex flex-col gap-2 bg-gradient-to-b from-slate-50 to-indigo-50 rounded-lg py-4 px-8 border-1 border-slate-200 dark:from-slate-600 dark:to-black dark:border-slate-900">
                        <div class="flex gap-2 items-center">
                            <div class="text-3xl ">🧱</div>
                            <h3 class="m-0">Less Boilerplate</h3>
                        </div>
                        <p>Spend less time typing boilerplate code in your routes, controllers, views, and models.</p>
                    </div>
                </div>
            </section>
        </div>
    </div>

    <div class="p-4 pt-2 dark:pt-0 bg-gradient-to-b from-slate-100/90 to-white dark:from-gray-900 dark:to-gray-900 dark:border dark:border-gray-900">
        <div class="max-w-6xl  mx-auto">
            <section>
                <h2 class="mt-4 dark:text-slate-100!">Get Started in 3 Easy Steps</h2>
                <div class="rounded-lg px-4 py-2 border-1 border-slate-200 shadow-md">
                    <div class="flex gap-2">
                        <div class="border-r border-slate-200 flex-1 rounded-xl p-1 text-center">1. Create a new Flask project</div>
                        <div class="border-r border-slate-200 flex-1 rounded-lg p-1 text-center">2. Move into your project directory</div>
                        <div class=" flex-1 rounded-lg p-1 text-center">3. Generate a resource</div>
                    </div>
                    <div class="text-white rounded-lg flex flex-col md:flex-row overflow-hidden my-2">
                        
                        <div class="font-mono text-sm flex-1 bg-black px-4 py-2 flex flex-col justify-center">
                            <div>$ flask new myproject</div>
                            <div>$ cd myproject</div>
                            <div>$ flask make:view posts.index -rcm</div>
                        </div>
                        <div class="flex-1 bg-gray-800 px-4 py-2 flex flex-col justify-center">
                            In three commands, Flask-Commands takes you from zero to generated your owns application's routes, controllers, models, and views.
                        </div>   
                    </div>
                </div>
            </section>

            <section>
                <h2 class="m-0 text-2xl font-bold text-slate-900 dark:text-slate-100! text-center mt-4">
                    Supercharge your Flask projects today!
                </h2>
                <div class="flex flex-col md:flex-row gap-2 mt-2 mb-8 justify-center">
                    <a href="install_and_first_run.html" class="no-underline! bg-gradient-to-br from-violet-100 to-violet-200  text-indigo-800! flex items-start justify-center gap-2  font-extrabold px-4 py-2 rounded border-1 border-violet-200">
                        <span>Start With Installation</span>
                    </a>
                    <a href="docs.html" class="no-underline! bg-gradient-to-r from-slate-100/80 to-slate-100 flex items-start justify-center gap-2  font-extrabold px-4 py-2 rounded border-1 border-slate-200 hover:text-[#0a7d91]! text-[#0a7d91]!">                        
                        <span>Browse Commands</span>
                    </a>
                <div>
            </section>            
        </div>
    </div>


.. toctree::
   :hidden:

   Docs <docs>
   Videos <video_series>
   
    