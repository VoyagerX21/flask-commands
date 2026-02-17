import os
import click

from flask_commands.utils.controllers import (
    controller_make_file,
    controller_generate_relative_path_from_controller_name
)
from flask_commands.utils.files import file_is_project_root
from flask_commands.utils.models import (
    model_generate_hierarchy_from_controller_name,
    model_generate_model_name_from_controller_name,
    model_make_file
)
from flask_commands.utils.naming import camel_to_snake
from flask_commands.utils.routes import route_generate_route_name
from flask_commands.utils.wirings import wire_controller_route_view


@click.command(name="make:controller")
@click.argument("controller_name")
@click.option("--crud", is_flag=True,
              help="Optional CRUD flag to generate all seven RESTful actions routes and controller methods along with get views.")
@click.option("--model", "model_name", default=None,
              help="Optional model name (example Post which makes the database table 'posts').")
@click.option("-m", "--generate-model", is_flag=True,
              help="Optional model flag to generate an inferred model from the controller name.")
def make_controller(
    controller_name: str,
    crud: bool,
    model_name: str | None,
    generate_model: bool) -> None:
    if not file_is_project_root():
        return

    # Infer model name if not provided
    if generate_model and model_name is None:
        non_nested_model_name, nested_model_name = model_generate_model_name_from_controller_name(controller_name)
        if nested_model_name:
            _, parent_models, _ = \
                model_generate_hierarchy_from_controller_name(controller_name)

            click.echo(
                "Detected nested models:\n" +
                " -> ".join(parent_models)
            )
            click.echo(f"Y (nested generated model) = {nested_model_name}")
            click.echo(f"N (single resource model)  = {non_nested_model_name}")
            use_nested = click.confirm("Use nested pattern?", default=True)
            model_name = nested_model_name if use_nested else non_nested_model_name
        else:
            model_name = non_nested_model_name
        click.secho(f"💡 Info: Generated model {click.style(model_name, bold=True)}", fg="cyan")

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
        relative_path = controller_generate_relative_path_from_controller_name(controller_name)
        for action in restful_actions:
            dotted_path_with_action = f"{relative_path.replace('/', '.')}.{action}"
            route_name = route_generate_route_name(dotted_path_with_action)

            is_successful, messages = wire_controller_route_view(
                relative_path,
                action,
                controller_name,
                route_name)
            all_successful = all_successful and is_successful

            for message in messages:
                click.echo(message)

    # If a model_name was provided or inferred
    if model_name:
        model_init_path = os.path.join("app", "models", "__init__.py")
        model_file_path = os.path.join("app", "models", f"{model_name.lower()}.py")
        is_successful, message = model_make_file(
            model_name, model_init_path, model_file_path)
        click.echo(message)
        all_successful = all_successful and is_successful

    if not all_successful:
        click.secho("⚠️  Warning: One or more make controller steps produced a warning or failure.", fg="yellow", bold=True)
