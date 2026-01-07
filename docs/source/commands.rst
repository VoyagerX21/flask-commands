Commands
========

flask new
---------

After installing Flask-Commands globally you will have access to a new command ``flask`` which will allow you to quickly scaffold out flask applications. Run the following command to scaffold out a new project called myproject.

.. code-block:: bash

   flask new myproject

If you look at your directory folders you will see a new folder called ``myproject``.  This folder contains all the files for your new flask application.

What you get:

A virtual enviroment ``venv/`` with core Flask dependencies already installed and listed in ``requirements.txt``. When you include ``--db`` (default unless ``--no-db``), it also installs ``Flask-Migrate``/``Flask-SQLAlchemy``, seeds a SQLite database, and runs the initial migration.

- Blueprint-based app skeleton (``app/``),
- The projects entrypoint is ``run.py``.
- Configuration setup up under ``config/``,
- Tailwind-ready static pipeline under ``app/static/src/`` with npm scripts to watch/build CSS.
- Environment files ``.env`` and ``.env.example``
- One Blueprint defined in ``app/__init__.py`` called ``mains`` and the corresponding route set at ``app/routes/mains`` also called ``mains``.
- One Controller set up at ``app/controllers/main_controller`` called ``MainController``
- One ``Hello World`` view template under ``app/templates/mains/index.html``
- A macOS-friendly ``run.sh`` helper you start your application with a one line in the terminal.

.. code-block:: bash
   ./run.sh

flask make:view
---------------

Generates template files under ``app/templates/`` from dotted paths (e.g., ``posts.index`` -> ``app/templates/posts/index.html``). Optional flags wire up matching components:

- ``-c/--generate-controller`` or ``--controller NAME`` creates or extends the controller class.
- ``-r/--generate-route`` or ``--route PATH`` adds blueprint routes (CRUD verbs inferred when possible).
- ``-m/--generate-model`` or ``--model NAME`` seeds a SQLAlchemy model and import stub.

Examples:

.. code-block:: bash

   flask make:view button                    # view-only snippet
   flask make:view posts.index -crm          # view + controller + route + model
   flask make:view posts.show --route /posts/<int:post_id> --controller PostController
