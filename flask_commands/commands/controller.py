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

    # Infer model name(s) if not provided
    model_names: list[str] = []

    if model_name:
        model_names = [model_name]
    # Infer model name if not provided
    elif generate_model:
        non_nested_model_name, nested_model_names = \
            model_generate_model_name_from_controller_name(controller_name)
        if nested_model_names:
            namespace, parent_models, child_model_names = \
                model_generate_hierarchy_from_controller_name(controller_name)
            if len(parent_models) > 1:
                click.echo(
                    "Detected nested models:\n" + " -> ".join(parent_models)
                )
                click.echo(f"1 (single resource model)  = {non_nested_model_name}")
                click.echo(f"2 (nested generated model) = {nested_model_names[0]}")
                choice = click.prompt(
                    "Enter choice:",
                    type=click.Choice(["1", "2", "single", "nested"], case_sensitive=False),
                    default=1,
                    show_choices=False)
                use_single = choice in ("1", "single").lower()
                chosen = non_nested_model_name if use_single else nested_model_names[0]
                model_names = [chosen]

            else:
                click.echo(
                    "Detected multiple child like segments:\n" +
                    ", ".join(child_model_names))
                click.echo(f"1 (single resource model)  = {non_nested_model_name}")
                click.echo(f"2 (generate the folowing models) = {', '.join(nested_model_names)}")
                choice = click.prompt(
                    "Enter choice:",
                    type=click.Choice(["1", "2", "single", "nested"], case_sensitive=False),
                    default=1,
                    show_choices=False).lower()
                use_single = choice in ("1", "single")
                model_names = [non_nested_model_name] if use_single else nested_model_names
        else:
            model_names = [non_nested_model_name]
        generated_models = click.style(', '.join(model_names), bold=True)
        click.secho(f"💡 Info: Generated model(s) {generated_models}", fg="cyan")

    # If a model_name was provided or inferred
    if model_names:
        for model_name in model_names:
            model_init_path = os.path.join("app", "models", "__init__.py")
            model_file_path = os.path.join("app", "models", f"{model_name.lower()}.py")
            is_successful, message = model_make_file(
                model_name, model_init_path, model_file_path)
            click.echo(message)
            all_successful = all_successful and is_successful

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

    if not all_successful:
        click.secho("⚠️  Warning: One or more make controller steps produced a warning or failure.", fg="yellow", bold=True)
