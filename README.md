
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
- `flask make:view` generates template files and can optionally wire controllers, routes/blueprints, and SQLAlchemy models.
- `flask make:controller` scaffolds a controller class and can optionally add RESTful actions, routes, templates, and model generation (`--model` or `-m`, with `--flat/--nest` for inferred model choices).
- `flask make:model` scaffolds a SQLAlchemy model and can optionally wire RESTful controllers, routes, and templates (`--crud`, with `--flat/--nest` for model structure selection).

All generated code is plain Flask with no hidden runtime layers; every file is created on disk.
The goal is to remove repetitive setup work while keeping everything local and transparent.

## Installation

Flask-Commands is designed to be installed globally so you can create new Flask apps anywhere on your machine.

Recommended:

```bash
pipx install Flask-Commands --include-deps
```

Alternative:

```bash
pip install Flask-Commands
```

You will also want `npm` available because generated Flask projects include Tailwind CSS tooling. If `npm` is not installed, install Node.js first.

## Quick Start

```bash
flask new myproject          # includes a SQLite DB scaffolding by default
cd myproject
```

To create a project without database support, use:

```bash
flask new myproject --no-db
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

`run.sh` opens a Flask shell, starts the dev server, rebuilds `tailwind.css` and `tailwind.min.css`, opens VS Code and Chrome, and hot-reloads changes in `templates/`, `controllers/`, `forms/`, `models/`, and `routes/`.

Browser reloading uses `fswatch`, so install it first if it is not already available:

```bash
brew install fswatch
```

## Docs quick links

- Full guide: https://flask-commands.readthedocs.io/en/latest/docs.html
- Install and first run: https://flask-commands.readthedocs.io/en/latest/install_and_first_run.html
- Starting a project: https://flask-commands.readthedocs.io/en/latest/starting_a_project.html
- Core ideas: https://flask-commands.readthedocs.io/en/latest/commands/core_ideas.html
- Cheat sheet: https://flask-commands.readthedocs.io/en/latest/commands/cheat_sheet.html
- Changelog: https://flask-commands.readthedocs.io/en/latest/changelog.html

## Cheat sheet

- `flask new myproject` — New Flask project with DB scaffolding (default).
- `flask new myproject --no-db` — New Flask project without DB setup.
- `flask make:view about` — Template only (`app/templates/about.html`).
- `flask make:view recipes.index -rcm` — Start a recipe resource with a list page, route, controller, and model.
- `flask make:view recipes.show -rc` — Add a detail page to the existing recipe resource.
- `flask make:view recipes.create -rcm` — Add a `GET` action that renders a recipe form template.
- `flask make:view recipes.store -rcm` — Add a `POST` action that wires behavior without creating a template.
- `flask make:view recipes.comments.index -rcm` — Create a nested comments resource under recipes.
- `flask make:controller RecipeController --crud` — Generate RESTful controller methods, routes, and templates for recipes.
- `flask make:controller RecipeController --crud -m` — Generate the RESTful recipe resource and matching model in one controller-first command.
- `flask make:controller ShoppingListController --crud --model ShoppingList` — Keep a multi-word model name together while generating RESTful scaffolding.
- `flask make:controller RecipeIngredientController --crud -m --nest` — Force the nested model interpretation for a controller-first `--crud` flow.
- `flask make:model Recipe` — Create and register a single model scaffold.
- `flask make:model Recipe --crud` — Model + RESTful controller/routes/templates.
- `flask make:model ShoppingList --crud --flat` — Force a flat model interpretation and RESTful structure.
- `flask make:model RecipeIngredient --crud --nest` — Force a nested model interpretation and RESTful structure.


## Examples

Here are a few commands and what they do so you can see the speed,
consistency gains, and how commands combine in practice.

### 1) Create a recipe index page with full wiring

```bash
flask make:view recipes.index -rcm
```

This scaffolds:

- the template at `app/templates/recipes/index.html`
- a controller with an `index` method
- a RESTful route for `/recipes`
- a `Recipe` model plus registration in `app/models/__init__.py`

### 2) Add a recipe detail page to the same resource

```bash
flask make:view recipes.show -rc
```

Because `Recipe` is already registered, route inference generates the RESTful show route:

- `/recipes/<int:recipe_id>`
- the controller method signature includes `recipe_id`


### 3) Generate a full RESTful resource from the controller first

```bash
flask make:controller RecipeController --crud -m
```

This scaffolds the seven RESTful actions across:

- controller methods
- routes in `app/routes/recipes/`
- templates for the `GET` actions (`index`, `show`, `create`, and `edit`)
- a `Recipe` model plus registration

### 4) Handle nested recipe/ingredient model shape intentionally

```bash
flask make:model RecipeIngredient --crud
```

If nested candidates are detected, you will get a prompt to choose flat vs nested.
To skip the prompt explicitly:

```bash
flask make:model RecipeIngredient --crud --flat
flask make:model RecipeIngredient --crud --nest
```

## Contributing

I’m keeping development closed for now, but feedback is welcome.
Please open an issue for bugs or ideas. License: MIT.
