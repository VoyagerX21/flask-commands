# flask-commands

Lightweight CLI scaffolding to generate a ready-to-run Flask project with sensible defaults (dotenv, Tailwind build scripts, logs, basic blueprint layout). The generator is intended to be used locally per-project (editable install / project venv) rather than as a globally installed tool.

Key files
- Package metadata: [pyproject.toml](pyproject.toml)
- CLI entrypoint: [`flask_commands.cli.cli`](flask_commands/cli.py)
- Generator command: [`flask_commands.commands.new.new`](flask_commands/commands/new.py)
- Helpers: [`flask_commands.utils.create_venv`](flask_commands/utils.py), [`flask_commands.utils.copy_templates`](flask_commands/utils.py)
- Project template used when scaffolding: [flask_commands/project](flask_commands/project)
- License: [LICENSE](LICENSE)

Why local-first
- Avoids polluting global Python installs.
- Lets each project keep its own copy of the scaffold (and modify it).
- Works well with virtual environments and CI workflows.

Quickstart (development)
1. Create and activate a development venv for this tool:
```sh
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```
2. Install the tool in editable mode and install Flask for testing:
```sh
pip install -e .
pip install Flask
```
3. Run the generator:
```sh
# preferred (if you change the console script name in pyproject.toml)
flask-commands new myproject

# or run module directly (no console script needed)
python -m flask_commands.cli new myproject
```

Notes on console script
- Current package [pyproject.toml](pyproject.toml) registers a `flask` console script. That will conflict with the official Flask `flask` script. Rename the script in [pyproject.toml](pyproject.toml) (for example to `flask-commands`) or call the module directly as shown above.

What the generator does
- Creates a project folder and a venv inside it using the same Python interpreter that runs the generator (see [`flask_commands.utils.create_venv`](flask_commands/utils.py)). This avoids guessing `python` vs `python3`.
- Installs default Python dependencies into the new venv and writes a `requirements.txt` (if enabled).
- Copies the template tree from [flask_commands/project](flask_commands/project) into the new project using [`flask_commands.utils.copy_templates`](flask_commands/utils.py).
- Optionally runs `npm install` for Tailwind and injects package.json scripts for building/watching CSS.
- Makes `run.sh` executable in POSIX environments.

Generated project (high level)
- run script: `run.sh` / `run.py`
- app package: `app/__init__.py`, `controllers/`, `routes/`, `static/`, `templates/`
- config: `config/{base,development,production}_config.py`
- example env files: `.env`, `.env.example`

Customization
- Edit the template files under [flask_commands/project](flask_commands/project) to change the generated structure or defaults.
- If you want generator commands to register on the project's Flask CLI (so commands appear under the project's `flask`), add an `init_app_cli(app)` helper that calls `app.cli.add_command(...)` and scaffold a small `manage.py` that wires it in.

Development tips
- Use `pip install -e .` when hacking on this package so local changes are reflected immediately in an active venv.
- The generator uses the current interpreter (`sys.executable`) to create project venvs, so it works whether the user runs `python` or `python3`.

Contributing
- Open issues or pull requests; follow the project license: [LICENSE](LICENSE).

License
- MIT — see [LICENSE](LICENSE)

