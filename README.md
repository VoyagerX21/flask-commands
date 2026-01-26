
# <img src="https://raw.githubusercontent.com/drewbutcher/flask-commands/main/docs/source/_static/flask-commands-logo.png" alt="Flask-Commands logo" width="200" style="display:inline-block; vertical-align:middle;"> Flask-Commands


[![pypi](https://img.shields.io/pypi/v/flask-commands.svg?cacheSeconds=300)](https://pypi.org/project/flask-commands/)
[![tests](https://img.shields.io/github/actions/workflow/status/drewbutcher/flask-commands/tests.yml?branch=main)](https://github.com/drewbutcher/flask-commands/actions)
[![coverage](https://codecov.io/gh/drewbutcher/flask-commands/branch/main/graph/badge.svg)](https://codecov.io/gh/drewbutcher/flask-commands)
[![docs](https://img.shields.io/readthedocs/flask-commands/latest)](https://flask-commands.readthedocs.io/)
[![license](https://img.shields.io/pypi/l/flask-commands.svg)](https://github.com/drewbutcher/flask-commands/blob/main/LICENSE)
[![stars](https://img.shields.io/github/stars/drewbutcher/flask-commands)](https://github.com/drewbutcher/flask-commands/stargazers)

**Flask-Commands** is a local-first CLI that scaffolds Flask projects and automates the wiring between views, routes, controllers, and models so you ship faster with consistent structure.


## Getting Started

Flask-Commands bundles opinionated, productivity-focused generators:

- `flask new` boots a ready-to-run Flask project with virtualenv, dotenv, Tailwind wiring, and optional SQLite + migrations (use `--db/--no-db`).
- `flask make:view` generates HTML views and can optionally wire controllers, routes/blueprints, and SQLAlchemy models.
- `flask make:controller` scaffolds a controller class and registers it in `app/controllers/__init__.py`.
- `flask make:model` scaffolds a SQLAlchemy model and can optionally wire RESTful controllers, routes, and views.

All generated code is plain Flask with no hidden runtime layers; every file is created on disk.
The goal is to remove repetitive setup work while keeping everything local and transparent.

## Installation

Flask-Commands is designed to be installed globally so you can create new Flask apps anywhere on your machine.

```bash
pip install Flask-Commands
```

## Quick Start

```bash
flask new myproject          # prompts for SQLite; use --db/--no-db to skip the prompt
cd myproject
```

Recommended (macOS):

```bash
./run.sh
```

Manual startup:

```bash
source venv/bin/activate
flask run --debug
```

`run.sh` opens a Flask shell, starts the dev server, rebuilds `tailwind.css` and `tailwind.min.css`, opens VS Code and Safari, and hot-reloads changes in `templates/`, `controllers/`, `forms/`, `models/`, and `routes/`.


## Docs quick links

- Commands book: https://flask-commands.readthedocs.io/en/latest/commands/index.html
- Concepts: https://flask-commands.readthedocs.io/en/latest/commands/concepts.html
- REST actions: https://flask-commands.readthedocs.io/en/latest/commands/rest_actions.html
- Nested resources: https://flask-commands.readthedocs.io/en/latest/commands/nested_resources.html
- Changelog: https://flask-commands.readthedocs.io/en/latest/changelog.html

## Cheat sheet

- `flask new myproject` — Scaffold a new Flask project.
- `flask make:view posts.index -rcm` — View + route + controller + model. Nested paths supported.
- `flask make:controller PostController --crud -m` — RESTful controller, routes, templates, and a model scaffold.  Nested supported.
- `flask make:model Post --crud` — Model plus RESTful controller, routes, and views. No nesting.

## Examples

Here are a few commands and what they do so you can see the speed and consistency gains.

```bash
flask make:view about -rc
```
Creates a new template, adds a controller method, and wires up a route in one step.

```bash
flask make:view posts.index -rcm
```
Generates the view, controller method, route, and a matching model scaffold with consistent naming.

```bash
flask make:view recipes.comments.index -rcm
```
Scaffolds nested resources with dotted notation, keeping folders and routes consistent.

```bash
flask make:controller PostController --crud
```
Builds a full RESTful controller, routes, and templates so you do not hand-write seven actions.

```bash
flask make:model Comment --crud
```
Creates a model and wires a RESTful controller, routes, and views for a complete resource.


## Contributing

I’m keeping development closed for now, but feedback is welcome.
Please open an issue for bugs or ideas. License: MIT.
