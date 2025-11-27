import os
import click
from flask_commands.utils import create_venv, copy_templates

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
    dependencies = [
        "Flask",
        "python-dotenv",
        "python-slugify"
    ]
    create_venv(project_name, packages=dependencies, freeze_requirements=True)

    copy_templates(project_name, replacements={"project_name": project_name})

    # Make run.sh executable
    run_sh_path = os.path.join(project_name, "run.sh")
    os.chmod(run_sh_path, 0o755)
