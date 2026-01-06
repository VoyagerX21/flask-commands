# flask-commands

Local-first CLI that scaffolds a Flask project (venv, dotenv, Tailwind build scripts, blueprints, optional SQLite) and can keep generating views, routes, controllers, and models for you.

## Install
- Python 3.10+
- Optional: `npm` if you want Tailwind auto-installed; the tool will skip Tailwind if `npm` is missing.
- `pip install Flask-Commands`

> The published console script is currently `flask`. If you have a clash with Flask’s own CLI, run with `python -m flask_commands.cli ...` or rename the script to `flask-commands` in `pyproject.toml`.

## Commands at a glance
- `flask new <project_name> [--db/--no-db]` — bootstrap a new project in a sibling folder, create a venv, install deps, copy the template, wire Tailwind, and optionally initialize SQLite + migrations.
- `flask make:view <dotted_path_with_name> [options]` — create a view under `app/templates/` and optionally add a controller method, route/blueprint, and model.

## Creating a project: `flask new`
What happens:
- Creates `<project_name>/` and a virtual environment under `venv/`.
- Installs Python deps: always `Flask` + `python-dotenv`; adds `Flask-Login`, `Flask-Migrate`, and `Flask-SQLAlchemy` when `--db` (or when you accept the prompt).
- Freezes `requirements.txt` from the venv.
- Copies the starter app from `flask_commands/project` (blueprint-based app with configs, sample controller/route, Tailwind input.css, `.env` files, `run.py`, and `run.sh`), and marks `run.sh` executable.
- Installs Tailwind via npm and adds `watch:css` / `build:css` scripts (skipped with a warning if npm is absent).
- If `--db` is enabled, runs `flask db init/migrate/upgrade` using the new venv to seed SQLite.

Quickstart:
```bash
flask new myproject        # use --no-db to skip SQLite setup
cd myproject
source venv/bin/activate
flask run --debug          # or ./run.sh on macOS to open terminals + Safari and tailwind watchers
```
`run.sh` uses `osascript`/`fswatch`, so it is macOS-only.

## Generating views/routes/controllers/models: `flask make:view`
Usage:
```
flask make:view <dotted_path_with_name> [--controller NAME|-c] [--route PATH|-r] [--model NAME|-m]
```
- `dotted_path_with_name` maps folders + filename under `app/templates/`: `posts.index` → `app/templates/posts/index.html`. Nest as needed: `admin.users.show` → `app/templates/admin/users/show.html`.
- Without flags you get just the view file (a small HTML snippet with a random Python quote).
- `-c/--generate-controller` infers a controller class from the path (e.g., `PostController` from `posts.index`) and adds the action method; `--controller` lets you set it explicitly.
- `-r/--generate-route` infers a RESTful route path (CRUD actions get GET/POST as appropriate, nested resources pick up parent IDs if a matching model import exists in `app/models/__init__.py`); `--route` lets you set a path yourself. If the route folder exists, it appends a function; otherwise it creates a blueprint folder and registers it in `app/__init__.py`.
- `-m/--generate-model` infers a singular class name and creates a basic SQLAlchemy model file and import stub; `--model` lets you name it explicitly.

Examples:
- Minimal view component: `flask make:view button`
- CRUD start with inferred pieces: `flask make:view posts.index -crm`
- Nested resource with route params: `flask make:view admin.posts.comments.show -cr`
- Explicit wiring: `flask make:view posts.show --controller PostController --route /posts/<int:post_id> --model Post`

## Project template (copied by `flask new`)
- Application entrypoints: `run.py`, `run.sh`
- App package: `app/__init__.py` with blueprint registration + extensions (`LoginManager`, `SQLAlchemy`, `Migrate`)
- Default blueprint: `app/routes/mains` → `app/controllers/main_controller.py` → `app/templates/mains/index.html`
- Configs: `config/{base,development,production}_config.py`
- Static/Tailwind: `app/static/src/input.css` (Tailwind CLI builds `tailwind.css` / `tailwind.min.css`)
- Environment files: `.env`, `.env.example`

## Contributing
PRs and issues welcome. License: MIT.
