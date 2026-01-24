
# <img src="https://raw.githubusercontent.com/drewbutcher/flask-commands/main/docs/source/_static/flask-commands-logo.png" alt="Flask-Commands logo" width="200" style="display:inline-block; vertical-align:middle;"> Flask-Commands


[![pypi](https://img.shields.io/pypi/v/flask-commands.svg?cacheSeconds=300)](https://pypi.org/project/flask-commands/)
[![tests](https://img.shields.io/github/actions/workflow/status/drewbutcher/flask-commands/tests.yml?branch=main)](https://github.com/drewbutcher/flask-commands/actions)
[![docs](https://img.shields.io/readthedocs/flask-commands/latest)](https://flask-commands.readthedocs.io/)
[![license](https://img.shields.io/pypi/l/flask-commands.svg)](https://github.com/drewbutcher/flask-commands/blob/main/LICENSE)
[![stars](https://img.shields.io/github/stars/drewbutcher/flask-commands)](https://github.com/drewbutcher/flask-commands/stargazers)

**Flask-Commands** is a local-first CLI tool that scaffolds Flask projects and keeps generating views, routes, controllers, and models for you so you can stay in flow. This is still very much in a beta stage, so try it out at your own risk.

## Getting Started

Flask-Commands bundles a few opinionated conveniences:

- `flask new` bootstraps a ready-to-run Flask project with virtualenv, dotenv, Tailwind wiring, and optional SQLite + migrations (prompted unless you pass `--db/--no-db`).
- `flask make:view` generates HTML views and can optionally add controllers, routes/blueprints, and SQLAlchemy models.
- `flask make:controller` scaffolds a controller class and registers it in `app/controllers/__init__.py`.

All generated code is plain Flask with no hidden runtime layers; every file is created on disk.
The goal is to remove the repetitive setup work while keeping everything local and transparent.

## Installation

Flask-Commands is designed to be installed globally so you can create new Flask apps anywhere on your machine.

```bash
pip install Flask-Commands
```

> The published console script is `flask`. If you have a clash with Flask’s own CLI, run with `python -m flask_commands.cli ...` or rename the script in `pyproject.toml`.

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

Add a first page with controller and route wiring:

```bash
flask make:view posts.index -cr
flask make:view admin.users.show -cr   # nested example
```

Tailwind is installed automatically when `npm` is available; otherwise the tool skips it with a warning.

## Commands

### flask new

After installing Flask-Commands globally, you'll have access to a new command called `flask`, which lets you quickly scaffold Flask applications from the terminal.

```bash
flask new myproject
```

Once the command completes, you'll see a new directory called `myproject/` that contains everything you need to get a Flask application up and running.

If you do not pass `--db` or `--no-db`, the command prompts you to include a SQLite database (default yes).

What you get:

- A Python virtual environment `venv/` with core Flask dependencies pre-installed and listed in `requirements.txt`.
- When using `--db` (enabled by default unless `--no-db` is specified), the following are also included:
  - Flask-Migrate
  - Flask-SQLAlchemy
  - A seeded SQLite database with a users table
  - An initial migration already applied
- A blueprint-based application skeleton under `app/`, organized by responsibility:
  - **Model** `app/models/` defining all your application’s data models/structure along with their methods.
  - **View** `app/templates/` containing all HTML templates (including macros/components) used by the application.
  - **Controller** `app/controllers/` housing controller classes responsible for the logic to gather and serve the requested data.
  - **URL** `app/routes/` declaring URL paths and connecting them to controllers.
- The project entry point at `run.py`.
- Centralized configuration files under `config/`.
- If `npm` is installed, a Tailwind-ready static asset pipeline at `app/static/src/`, including npm scripts for watching and building CSS.
- Environment configuration files:
  - `.env`
  - `.env.example`
- A default blueprint named `mains`, defined in `app/__init__.py`:
  - Routes at `app/routes/mains`
  - A controller at `app/controllers/main_controller` named `MainController`
  - A starter “Hello World” template at `app/templates/mains/index.html`
- A macOS-friendly helper script `run.sh` for starting the application with a single command:

```bash
./run.sh
```

You can review this structure directly in the Flask-Commands source under `flask_commands/project`.

### flask make:view

Generates template files under `app/templates/` from dotted paths (for example, `posts.index` maps to `app/templates/posts/index.html`). Optional flags wire up matching components:

- `-c/--generate-controller` or `--controller NAME` creates or extends the controller class.
- `-r/--generate-route` or `--route PATH` adds blueprint routes and supports RESTful actions (`index`, `show`, `create`, `store`, `edit`, `update`, `destroy`, or `delete`).
- `-m/--generate-model` or `--model NAME` seeds a SQLAlchemy model with `id`, `created_at`, and `updated_at` columns plus an import stub.

Examples:

```bash
flask make:view button                         # view-only snippet
flask make:view components.buttons             # reusable component template
flask make:view posts.index -crm               # view + controller + route + model
flask make:view recipes.comments.index -rcm    # nested relationship
flask make:view posts.show --route '/posts/<int:post_id>' --controller PostController
```

### flask make:controller

Creates a controller class under `app/controllers/` and registers it in `app/controllers/__init__.py`.

```bash
flask make:controller PostController
```

This creates `app/controllers/post_controller.py` with a class stub:

```python
class PostController:
    pass
```

Use `--crud` to scaffold all seven RESTful actions, routes/blueprints, and matching templates.

```bash
flask make:controller PostController --crud
```

With `--crud`, `app/controllers/post_controller.py` looks like:

```python
from flask import render_template
from flask import redirect, url_for

class PostController:

    @staticmethod
    def index() -> str:
        return render_template('posts/index.html')

    @staticmethod
    def show(post_id: int) -> str:
        return render_template('posts/show.html')

    @staticmethod
    def create() -> str:
        return render_template('posts/create.html')

    @staticmethod
    def store() -> str:
        return redirect(url_for('posts.index'))

    @staticmethod
    def edit(post_id: int) -> str:
        return render_template('posts/edit.html')

    @staticmethod
    def update(post_id: int) -> str:
        return redirect(url_for('posts.index'))

    @staticmethod
    def destroy(post_id: int) -> str:
        return redirect(url_for('posts.index'))
```

It also generates and wires up routes and templates:

```python
from app.controllers import PostController
from app.routes.posts import bp

@bp.route('/posts', methods=['GET'])
def index():
    return PostController.index()

@bp.route('/posts/<int:post_id>', methods=['GET'])
def show(post_id: int):
    return PostController.show(post_id)

@bp.route('/posts/create', methods=['GET'])
def create():
    return PostController.create()

@bp.route('/posts', methods=['POST'])
def store():
    return PostController.store()

@bp.route('/posts/<int:post_id>/edit', methods=['GET'])
def edit(post_id: int):
    return PostController.edit(post_id)

@bp.route('/posts/<int:post_id>', methods=['POST'])
def update(post_id: int):
    return PostController.update(post_id)

@bp.route('/posts/<int:post_id>/delete', methods=['POST'])
def destroy(post_id: int):
    return PostController.destroy(post_id)
```

And creates four view templates under `app/templates/posts/`: `index.html`, `show.html`, `create.html`, `edit.html`.

## Contributing

I’m keeping development closed for now, but feedback is welcome.
Please open an issue for bugs or ideas. License: MIT.
