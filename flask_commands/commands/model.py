import os
import click

from flask_commands.utils.files import file_is_project_root
from flask_commands.utils.models import model_make_file
from flask_commands.utils.naming import camel_to_snake, pluralize
from flask_commands.utils.routes import route_generate_route_name
from flask_commands.utils.wirings import wire_controller_route_view


@click.command(name="make:model")
@click.argument("model_name")
@click.option("--crud", is_flag=True,
               help="Optional CRUD flag to generate all seven RESTful actions routes and controller methods along with get views.")
def make_model(model_name: str, crud:bool) -> None:
    if not file_is_project_root():
        return
    all_successful = True

    if model_name:
        is_successful, message = model_make_file(model_name)
        click.echo(message)
        all_successful = all_successful and is_successful

    if crud:
        restful_actions = ['index', 'show', 'create', 'store', 'edit', 'update', 'destroy']

        for action in restful_actions:
            controller_name = model_name + "Controller"
            relative_path = pluralize(model_name.lower())
            dotted_path_with_action = relative_path + '.' + action
            route_name = route_generate_route_name(dotted_path_with_action)

            is_successful, messages = wire_controller_route_view(
                relative_path,
                action,
                controller_name,
                route_name)
            all_successful = all_successful and is_successful

            for message in messages:
                click.echo(message)

    if not all_successful:
        click.secho("⚠️  Warning: One or more make model steps produced a warning or failure.", fg="yellow", bold=True)
