import os
import click
import shutil
import subprocess
from flask_commands.utils.venv import create_venv
from flask_commands.utils.files import copy_templates
from flask_commands.utils.css import install_tailwind

@click.command()
@click.argument("project_name")
def new(project_name):
    """Create a new Flask project"""
    project_dir = os.path.abspath(project_name)
    project_started = False
    if os.path.exists(project_dir):
        click.secho(f"💣 Error: Folder Already Exists.", fg="red", bold=True)
        click.secho(f"    - Folder '{project_name}' already exists in this directory", fg="red")
        click.secho(f"    - Please choose a different project name or change to a new directory", fg="red")
        return
    try:
        project_started = True
        os.makedirs(project_dir)

        # Create a Virtual Enviroment and install dependancies and
        # generate a requirments file
        create_venv(
            project_dir,
            packages=[
                "Flask",
                "Flask-Login",
                "Flask-Migrate",
                "Flask-SQLAlchemy",
                "python-dotenv"],
            freeze_requirements=True)

        copy_templates(project_dir, replacements={"project_name": project_name})

        # Make run.sh executable
        os.chmod(os.path.join(project_dir, "run.sh"), 0o755)

        install_tailwind(project_dir)

        click.secho("Setting up sqlite database for development...", bold=True)

        venv_flask = os.path.join(project_dir, "venv", "bin", "flask")

        if not os.path.exists(venv_flask):
            raise click.ClickException("venv/bin/flask not found")

        subprocess.run(
            [venv_flask, "db", "init"],
            check=True,
            cwd=project_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        subprocess.run(
            [venv_flask, "db", "migrate", "-m", "Initial migration."],
            check=True,
            cwd=project_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        click.secho("    - ✅ Success: sqlite database initialized", fg="green")

        click.secho(
            f"{project_name.title()} is ready!!! Run the following:",
            bold=True, underline=True)


        click.secho(f"cd {project_name}", fg="cyan")
        click.secho("./run.sh", fg="cyan")
    except Exception as exception:
        # if project_started and os.path.exists(project_name):
        #     shutil.rmtree(project_name, ignore_errors=True)
        click.secho("💣 Error: Project Creation Failed 😤", bold=True, fg="red")
        raise click.ClickException(f"exception:\n{exception}") from exception
