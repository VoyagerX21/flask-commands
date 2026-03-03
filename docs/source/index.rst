.. flask-commands documentation master file, created by
   sphinx-quickstart on Mon Jan  5 23:04:44 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

================
Flask-Commands
================
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

**Flask-Commands** is a local-first CLI tool that scaffolds Flask projects and
generates views, routes, controllers, and models so you can stay in flow (and
spend less time wiring the same things together, impeccably, for the hundredth
time).

Quick Start
-----------

Start a new project:

.. code-block:: bash

   flask new myproject

Generate a view with controller, route, and model wiring:

.. code-block:: bash

   flask make:view posts.index -crm

Why Flask-Commands
------------------

- Local-first workflow with plain Flask output
- Fast generators for common Flask structure
- Predictable file layout you can read and own
- Minimal ceremony for repeated scaffolding work

Current Release: |release|

.. toctree::
   :maxdepth: 4
   :caption: Contents:

   introduction
   commands/index
   changelog
