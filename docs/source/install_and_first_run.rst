Install and First Run
=====================

Before we build anything, let’s get Flask-Commands installed and make sure the
command is available in your terminal. This part is intentionally short so you
can get to the fun part quickly.

Install the Prerequisites
-------------------------

.. youtube_embed:: install-the-prerequisites-for-flask-commands

Before installing Flask-Commands, I recommend having two tools available on
your machine:

- ``pipx``
- ``npm``

If you use Homebrew, both are easy to install. If Homebrew is not installed,
visit the `official Homebrew site <https://brew.sh/>`_ first.


Because Flask-Commands plugs into Flask's CLI, the recommended way
to install this package is through a global ``pipx`` install that also
exposes dependency apps. You can check whether ``pipx`` is installed by
running:

.. code-block:: bash

   pipx --version

If that prints a version number, you are all set. If the command is not found,
you can follow the `official pipx installation guide <https://pipx.pypa.io/stable/how-to/install-pipx/>`_.
On macOS with Homebrew, that usually looks like this:

.. code-block:: bash

   brew install pipx
   pipx ensurepath

You will also want ``npm`` available because the generated Flask project includes
Tailwind CSS tooling. To check whether ``npm`` is installed, run:

.. code-block:: bash

   npm --version

If that prints a version number, you are good to go. If not, you
will need to install Node.js because ``npm`` comes with Node.js. Install Node.js
from the `official Node.js download page <https://nodejs.org/en/download>`_ or
the unofficial community installation using Homebrew:

.. code-block:: bash

   brew install node

Install Flask-Commands with ``pipx``
------------------------------------

.. youtube_embed:: install-flask-commands-with-pipx

.. code-block:: bash

   pipx install Flask-Commands --include-deps

This is the recommended way to install Flask-Commands. ``pipx`` keeps the
installation isolated and makes Flask's ``flask`` command, with Flask-Commands
extras, available anywhere.

What is ``--include-deps`` doing? Flask-Commands is a Flask CLI plugin.
``pipx`` needs to expose Flask’s ``flask`` executable from the installed
dependencies so your plugin commands appear under the real Flask CLI.

Install Flask-Commands with ``pip``
-----------------------------------

.. youtube_embed:: install-flask-commands-with-pip

Alternatively, if you prefer not to use ``pipx``, you can install
Flask-Commands with ``pip``. This can be done either globally or inside a
virtual environment. Even with a ``pip`` install, you will still want ``npm``
installed so Tailwind CSS works in the generated Flask project.

.. code-block:: bash

   pip install Flask-Commands

There are two common ways people handle a ``pip`` install.

If you install Flask-Commands inside a virtual environment, that environment
must be activated any time you want to use Flask-Commands through Flask’s CLI.
That can be a little awkward for ``flask new``, because the environment where
Flask-Commands is installed may live in a different place from the Flask app
you want to create.

.. code-block:: bash

   flask new myproject

A second approach would be to install Flask-Commands globally with ``pip``,
then the command will be available system-wide. This is more convenient, but it
also adds packages directly to your machine’s Python environment, which is why
``pipx`` is still the recommended option.

So ``pip`` absolutely works, but ``pipx`` is usually the smoother choice for
this package because Flask-Commands is meant to be available as a global
scaffolding tool.

Confirm the Command with ``--version``
--------------------------------------

.. youtube_embed:: confirm-the-command-with-version

Once Flask-Commands is installed, the quickest way to confirm the plugin is
available is to check its version directly:

.. code-block:: bash

   flask commands -v

You can also use:

.. code-block:: bash

   flask commands --version

That confirms two useful things right away:

- Flask-Commands is installed
- your shell can find the plugin through Flask’s CLI

For most people, checking the version is the first “yes, it worked” moment
after installation.

Notice that Flask-Commands is not exposed as a separate top-level executable.
Instead Flask-Commands plugs into Flask’s CLI, which means there are two
useful version checks:

.. code-block:: bash

   flask --version        # Flask version
   flask commands -v      # Flask-Commands version

Read the CLI at a Glance with ``--help``
----------------------------------------

.. youtube_embed:: read-the-cli-at-a-glance-with-help

Once you know Flask-Commands is installed, the next step is to look at the
commands it adds to Flask’s CLI.

To see the full command list, run:

.. code-block:: bash

   flask --help

This is the command that shows the Flask-Commands commands alongside Flask’s
built-in commands.

If you run ``flask --help`` outside a Flask project, Flask may also print a
message saying it could not locate an application. That is normal. The help
output still shows the commands Flask-Commands has registered.

To inspect an individual Flask-Commands command in more detail, run:

.. code-block:: bash

   flask new --help
   flask make:view --help
   flask make:controller --help
   flask make:model --help

This gives you a quick overview of the command surface and helps you see that
Flask-Commands is intentionally small and focused.

A short help screen is a good sign. It usually means the tool is trying to help
you build faster, not trap you in a long-term relationship with sixteen
subcommands and an identity crisis.

Now that the command is working, let’s create a project and give
Flask-Commands something real to build on.
