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

Because Flask-Commands is a command-line tool it is recommended to install this
pacakage globally with  ``pipx``. You can check if your machine has ``pipx``
by typing, run:

.. code-block:: bash

   pipx --version

If that prints a version number, you are all set. If the command is not found,
you can follow the `official pipx installation guide <https://pipx.pypa.io/stable/how-to/install-pipx/>`_.
On macOS with Homebrew, that usually looks like this:

.. code-block:: bash

   brew install pipx
   pipx ensurepath

You will also want ``npm`` available because the generated Flask project include
Tailwind CSS tooling. ``npm`` comes with Node.js. To check whether ``npm`` is
installed, run:

.. code-block:: bash

   npm --version

If that prints a version number, you are good to go. If not, install Node.js
from the `official Node.js download page <https://nodejs.org/en/download>`_ or
the unoffically community install using Homebrew:

.. code-block:: bash

   brew install node

Install Flask-Commands with ``pipx``
------------------------------------

.. youtube_embed:: install-flask-commands-with-pipx

.. code-block:: bash

   pipx install Flask-Commands

This is the recommended way to install Flask-Commands. ``pipx`` keeps the
installation isolated and makes the command available globally.

Install Flask-Commands with ``pip``
-----------------------------------

.. youtube_embed:: install-flask-commands-with-pip

Alternatively, if you prefer not to have ``pipx`` manage global installations, 
you can install Flask-Commands with ``pip``.  This can be done either globally 
or inside a virtual environment. Please note, even with a ``pip`` install, you 
will still want ``npm`` installed so Tailwind CSS works in the generated Flask
project.

.. code-block:: bash

   pip install Flask-Commands

There are two common ways people handle a ``pip`` install.

If you install Flask-Commands inside a virtual environment, that environment
must be activated any time you want to use this package’s ``flask`` command.
That can be a little awkward, because the environment where Flask-Commands is
installed will live in a different place from the Flask app you are trying to
create with:

.. code-block:: bash

   flask new myproject

Alternatively, if you install Flask-Commands globally with ``pip``, the 
command will be available system-wide.  This is more convenient, and was 
the original installation recommendation. The downside is that it
adds packages directly to your machine’s Python environment, which is why I
now recommend ``pipx`` instead.

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
