import os
import click
import subprocess
from flask_commands.utils import create_venv, read_template, write_file

@click.command()
@click.argument("project_name")
def new(project_name):
    """Create a new Flask project"""
    if os.path.exists(project_name):
        click.echo(f"Error: '{project_name}' already exists in this "
                    "directory.  Please pick a new name.")
        return

    os.makedirs(project_name)

    # Create a Virtual Enviroment and install dependancies and generate a requirments file
    dependencies = ["flask"]
    create_venv(project_name, packages=dependencies, freeze_requirements=True)

    # Create Folder Structure
    folders = [
        f"{project_name}/app",
        f"{project_name}/app/controllers",
        f"{project_name}/app/forms",
        f"{project_name}/app/middleware",
        f"{project_name}/app/models",
        f"{project_name}/app/routes",
        f"{project_name}/app/static",
        f"{project_name}/app/templates",
        f"{project_name}/config",
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # Create Boiler Plate Files
    dot_env_file_string = read_template(".env")\
        .replace('project_name', project_name)
    write_file(f"{project_name}/app/__init__.py", read_template("__init__.py"))
    write_file(f"{project_name}/run.py", read_template("run.py"))
    write_file(f"{project_name}/.env.example", read_template(".env.example"))
    write_file(f"{project_name}/.env", dot_env_file_string)
    write_file(f"{project_name}/run.sh", read_template("run.sh"))

    # Make run.sh executable
    if os.name == "posix":
        run_sh_path = os.path.join(project_name, "run.sh")
        os.chmod(run_sh_path, 0o755)
