import os
import click

from flask_commands.utils.controllers import (
    controller_make_file,
    extract_relative_path_from
)
from flask_commands.utils.files import is_project_root
from flask_commands.utils.naming import camel_to_snake
from flask_commands.utils.routes import route_infer_name_from
from flask_commands.utils.wirings import wire_controller_route_view


@click.command(name="make:controller")
@click.argument("controller_name")
@click.option("--crud", is_flag=True,
              help="Optional CRUD flag to generate all seven RESTful actions.")
def make_controller(
    controller_name: str,
    crud: bool) -> None:
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
    all_successful = True
    is_successful, message = controller_make_file(
        relative_path=None,
        action=None,
        controller_name=controller_name,
        route_name=None)
    click.echo(message)
    all_successful = all_successful and is_successful

    if crud:
        restful_actions = ['index', 'show', 'create', 'store', 'edit', 'update', 'destroy']
        relative_path = extract_relative_path_from(controller_name)
        for action in restful_actions:
            dotted_path_with_name = f"{relative_path.replace('/', '.')}.{action}"
            route_name = route_infer_name_from(dotted_path_with_name)


            is_successful, messages = wire_controller_route_view(
                dotted_path_with_name,
                relative_path,
                action,
                controller_name,
                route_name)
            all_successful = all_successful and is_successful

            for message in messages:
                click.echo(message)

    if not all_successful:
        click.secho("⚠️  Warning: One or more make controller steps failed.", fg="yellow", bold=True)

