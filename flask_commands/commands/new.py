import os
import click
import shutil
from flask_commands.utils.venv import create_venv
from flask_commands.utils.files import copy_templates
from flask_commands.utils.css import install_tailwind

@click.command()
@click.argument("project_name")
def new(project_name):
    """Create a new Flask project"""
    if os.path.exists(project_name):
        click.echo(f"Error: '{project_name}' already exists in this directory. "
                    "Please pick a new name.")
        return

    os.makedirs(project_name)

    # Create a Virtual Enviroment and install dependancies and
    # generate a requirments file
    create_venv(
        project_name,
        packages=["Flask", "python-dotenv", "python-slugify"],
        freeze_requirements=True)

    copy_templates(project_name, replacements={"project_name": project_name})

    # Make run.sh executable
    os.chmod(os.path.join(project_name, "run.sh"), 0o755)

    install_tailwind(project_name)
    click.echo("Your project is all ready!!! Run the following:")
    click.echo(f"1) cd {project_name}")
    click.echo(f"2) ./run.sh")
