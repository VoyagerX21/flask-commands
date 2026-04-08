Install and First Run
=====================

Before we build anything, let’s get Flask-Commands installed and make sure the
command is available in your terminal. This part is intentionally short so you
can get to the fun part quickly.

Install with ``pipx``
---------------------

.. youtube_embed:: install-flask-commands-with-pipx

Because Flask-Commands is a command-line tool you will probably want available
globally, ``pipx`` is a great fit.

.. code-block:: bash

   pipx install Flask-Commands

This keeps the install clean and makes the command available without asking you
to manage a dedicated project environment just to use the generator.

Install with ``pip``
--------------------

.. youtube_embed:: install-flask-commands-with-pip

If you prefer, you can also install Flask-Commands with ``pip``.

.. code-block:: bash

   pip install Flask-Commands

There are two common ways people do that.

If you install Flask-Commands with ``pip`` inside a virtual environment, then
that virtual environment must be activated any time you want to use the
``flask`` command from this package. That can be a little awkward, because the
virtual environment where Flask-Commands is installed will often live in a
different location from the new Flask application you are trying to create
with:

.. code-block:: bash

   flask new myproject

If you install Flask-Commands with ``pip`` globally, then the command will be
available system-wide, which is more convenient. That was the older
installation suggestion, and it works fine. The downside is that it dirties up
your machine’s local Python environment.

So ``pip`` absolutely works, but ``pipx`` is usually the smoother choice for
this package because Flask-Commands is meant to be used as a global CLI tool
without cluttering your global Python setup.

Confirm the Command with ``--version``
--------------------------------------

.. youtube_embed:: confirm-the-command-with-version

Once Flask-Commands is installed, the quickest way to confirm the command is
available is to check the version.

.. code-block:: bash

   flask --version

That tells you two useful things right away:

- the command is installed
- your shell can find it

For most people, checking the version is the first “yes, it worked” moment
after installation.

Read the CLI at a Glance with ``--help``
----------------------------------------

.. youtube_embed:: read-the-cli-at-a-glance-with-help

Once you know the command exists, the next step is to look at what it can do.

.. code-block:: bash

   flask --help

This gives you a quick overview of the command surface and helps you see that
Flask-Commands is intentionally small and focused.

A short help screen is a good sign. It usually means the tool is trying to help
you build faster, not trap you in a long-term relationship with sixteen
subcommands and an identity crisis.

Now that the command is working, let’s create a project and give
Flask-Commands something real to build on.
