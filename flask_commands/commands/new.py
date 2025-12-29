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
        click.echo(click.style(f"💣 Error: '{project_name}' already exists in this directory. "
                    "Please pick a new name.", fg="red"))
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
    click.echo(click.style(f"{project_name.title()} is ready!!! Run the following:", bold=True, underline=True))
    click.echo(f"{click.style(f"cd {project_name}", fg="cyan")}")
    click.echo(f"{click.style("./run.sh", fg="cyan")}")
