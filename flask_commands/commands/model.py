import os
import click

from flask_commands.utils.models import model_make_file
from flask_commands.utils.naming import pluralize
from flask_commands.utils.routes import route_infer_name_from
from flask_commands.utils.wirings import wire_controller_route_view


@click.command(name="make:model")
@click.argument("model_name")
@click.option("--crud", is_flag=True,
               help="Optional CRUD flag to generate all seven RESTful actions routes and controller methods along with get views.")
def make_model(model_name: str, crud:bool) -> None:
    all_successful = True

    if model_name:
        model_init_path = os.path.join("app", "models", "__init__.py")
        model_file_path = os.path.join("app", "models", f"{model_name.lower()}.py")
        is_successful, message = model_make_file(
            model_name, model_init_path, model_file_path)
        click.echo(message)
        all_successful = all_successful and is_successful

    if crud:
        restful_actions = ['index', 'show', 'create', 'store', 'edit', 'update', 'destroy']

        for action in restful_actions:
            controller_name = model_name + "Controller"
            relative_path = pluralize(model_name.lower())
            dotted_path_with_name = relative_path + '.' + action
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
        click.secho("⚠️  Warning: One or more make model steps failed.", fg="yellow", bold=True)
