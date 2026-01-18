import os
import click

from flask_commands.utils.controllers import controller_make_file
from flask_commands.utils.naming import camel_to_snake
from flask_commands.utils.files import is_project_root

@click.command(name="make:controller")
@click.argument("controller_name")
def make_controller(controller_name: str) -> None:
    if not is_project_root():
        return

    controller_file_path = \
        os.path.join(
            "app",
            "controllers",
            f"{camel_to_snake(controller_name)}.py")

    # if controller exist warn the user that the controller already exist
    if os.path.exists(controller_file_path):
        click.secho("⚠️  Warning: Controller Already Exists\n", fg="yellow", bold=True)
        click.secho(f"    - Controller File for {click.style(controller_name, bold=True)}", fg="yellow") + click.style(" already exists\n", fg="yellow")
        click.secho("    - No changes were made\n", fg="yellow")
    # else create the controller and the method
    else:
        action = ''
        relative_view_file_path = ''
        route_name = None
        is_successful, message = controller_make_file(
            controller_name, action, relative_view_file_path, route_name)
    click.echo(message)
