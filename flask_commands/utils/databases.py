import os
import click
import shutil
import subprocess
from flask_commands.utils.venv import venv_executable

def install_sqlitedb(project_path):
    """Initializes the sqlite database for a project by running the Flask
    migrations in the project's virtual environment.  Raises a Click
    Exception if venv/bin/flask is not found.
    """
    click.secho("Setting up sqlite database for development...", bold=True)

    venv_dir = os.path.join(project_path, "venv")
    venv_flask = venv_executable(venv_dir, "flask")


    if not os.path.exists(venv_flask):
        raise click.ClickException("venv/bin/flask not found")

    subprocess.run(
        [venv_flask, "db", "init"],
        check=True,
        cwd=project_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    subprocess.run(
        [venv_flask, "db", "migrate", "-m", "Initial migration."],
        check=True,
        cwd=project_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    subprocess.run(
        [venv_flask, "db", "upgrade"],
        check=True,
        cwd=project_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    click.secho("    - ✅ Success: sqlite database initialized", fg="green")
