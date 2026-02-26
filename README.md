
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

- `flask new` boots a ready-to-run Flask project with virtualenv, dotenv, Tailwind wiring, and SQLite + migrations by default. Use `--no-db` to skip DB setup.
- `flask make:view` generates HTML views and can optionally wire controllers, routes/blueprints, and SQLAlchemy models.
- `flask make:controller` scaffolds a controller class and can optionally scaffold CRUD routes/views plus model generation (`--model` or `-m`, with `--flat/--nest` for inferred nested candidates).
- `flask make:model` scaffolds a SQLAlchemy model and can optionally wire RESTful controllers, routes, and views (`--crud`, with `--flat/--nest` for nested model selection).

All generated code is plain Flask with no hidden runtime layers; every file is created on disk.
The goal is to remove repetitive setup work while keeping everything local and transparent.

## Installation

Flask-Commands is designed to be installed globally so you can create new Flask apps anywhere on your machine.

```bash
pip install Flask-Commands
```

## Quick Start

```bash
flask new myproject          # includes a SQLite DB scaffolding by default
cd myproject
# optional: flask new myproject --no-db
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

- `flask new blog_app` — New Flask project with DB scaffolding (default).
- `flask new blog_app --no-db` — New Flask project without DB setup.
- `flask make:view about` — Template only (`app/templates/about.html`).
- `flask make:view posts.index -rcm` — View + route + controller + model for blog posts.
- `flask make:view posts.show -rc` — Add/show route + controller method for an existing post resource.
- `flask make:controller PostController --crud` — Full RESTful controller/routes/views (and model if missing).
- `flask make:controller PostCommentController -m --flat` — Generate model from controller name, force flat model.
- `flask make:controller PostCommentController -m --nest` — Generate model from controller name, force nested model.
- `flask make:model Post --crud` — Model + RESTful controller/routes/views.
- `flask make:model PostComment --crud --flat` — CRUD scaffolding with flattened model generation.
- `flask make:model PostComment --crud --nest` — CRUD scaffolding with nested model generation.


## Examples

Here are a few commands and what they do so you can see the speed,
consistency gains, and how commands combine in practice.

### 1) Create a post index page with full wiring

```bash
flask make:view posts.index -rcm
```

This scaffolds:

- the view at ``index.html``
- controller with method index at ``post_controller.py``
- routes with /posts at ``routes.py``
- model at ``post.py`` plus registration in ``__init__.py``

### 2) Add a post detail page to the same resource
```bash
flask make:view posts.show -rc
```

Because Post is already registered, route inference generates the RESTful show route:

- ``/posts/<int:post_id>``
- controller method signature includes post_id


### 3) Generate a full blog post CRUD surface from controller-first workflow
```bash
flask make:controller PostController --crud
```
This scaffolds the seven RESTful actions across:

- controller (PostController)
- routes (app/routes/posts/)
- GET view templates (index, show, create, edit)
- plus model creation when the terminal resource model is missing

### 4) Handle nested post/comment model shape intentionally
```bash
flask make:model PostComment --crud
```

If nested candidates are detected, you’ll get a prompt to choose flatten vs nested.
To skip the prompt explicitly:

flask make:model PostComment --crud --flat
flask make:model PostComment --crud --nest

## Contributing

I’m keeping development closed for now, but feedback is welcome.
Please open an issue for bugs or ideas. License: MIT.
