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
        click.secho("⚠️  Warning: Controller Already Exists", fg="yellow", bold=True)
        click.echo(
            click.style(f"    - Controller File for {click.style(controller_name, bold=True)}", fg="yellow") +
            click.style(" already exists", fg="yellow"))
        click.secho("    - No changes were made", fg="yellow")
        return
    # create the controller
    is_successful, message = controller_make_file(
        controller_name,
        method_name=None,
        relative_view_file_path=None,
        route_name=None)
    click.echo(message)
