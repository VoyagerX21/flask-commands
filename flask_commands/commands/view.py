import os
import click

from flask_commands.utils.controllers import controller_generate_controller_name_from_relative_path
from flask_commands.utils.models import (
    model_generate_model_name_from_dotted_path_with_action,
    model_make_file
)
from flask_commands.utils.files import file_is_project_root
from flask_commands.utils.naming import camel_to_snake
from flask_commands.utils.routes import route_generate_route_name_with_model_prompt
from flask_commands.utils.scaffold import (
    normalize_dotted_path_with_action,
    split_dotted_path_with_action_into_relative_path_and_action
)
from flask_commands.utils.wirings import wire_controller_route_view

@click.command(name="make:view")
@click.argument("dotted_path_with_action")
@click.option("--controller", "controller_name", default=None,
              help="Use this controller class (for example: PostController).")
@click.option("-c", "--generate-controller", is_flag=True,
              help="Generate controller name from the dotted path (ignored if --controller is set)")
@click.option("--route", "route_name", default=None,
              help="Use this route path (for example: /posts or /posts/<int:post_id>)..")
@click.option("-r", "--generate-route", is_flag=True,
              help="Generate route from the dotted path (ignored if --route is set). May prompt to create a missing model.")
@click.option("--model", "model_name", default=None,
              help="Use/create this model name (for example: Post which makes the database table 'posts').")
@click.option("-m", "--generate-model", is_flag=True,
              help="Generate and create model from the dotted path (ignored if --model is set).")
def make_view(
    dotted_path_with_action: str,
    controller_name: str | None,
    generate_controller: bool,
    route_name: str | None,
    generate_route: bool,
    model_name: str | None,
    generate_model: bool) -> None:
    """
    Create a view template and optionally wire controller, route, and model.

    `dotted_path_with_action` maps to `app/templates/...` (for example, `posts.index`).
    Use `-c/-r/-m` to generate controller/route/model, or provide `--controller`, `--route`, and `--model`.
    """
    if not file_is_project_root():
        return

    is_successful, dotted_path_with_action = \
        normalize_dotted_path_with_action(dotted_path_with_action)
    if not is_successful:
        message = dotted_path_with_action
        click.echo(message)
        return

    all_successful = True
    relative_path, action = \
        split_dotted_path_with_action_into_relative_path_and_action(
            dotted_path_with_action)

    # 1) Generate controller name if not provided
    if generate_controller and controller_name is None:
        if relative_path != '':
            controller_name = controller_generate_controller_name_from_relative_path(relative_path)
            click.secho(f"💡 Info: Generated controller {click.style(controller_name, bold=True)}\n", fg="cyan")
        else:
            controller_name = 'MainController'

    # Generate model name if not provided
    if generate_model and model_name is None:
        model_name = \
            model_generate_model_name_from_dotted_path_with_action(dotted_path_with_action)
        click.secho(f"💡 Info: Generated model {click.style(model_name, bold=True)}\n", fg="cyan")

    allow_model_prompt = not bool(model_name)

    # If a model_name was provided or generated
    if model_name:
        is_successful, message = model_make_file(model_name)
        click.echo(message)
        all_successful = all_successful and is_successful

    # Generate route name if not provided
    if generate_route and route_name is None:
        route_name, new_model_name = \
            route_generate_route_name_with_model_prompt(
                dotted_path_with_action, allow_model_prompt)
        click.secho(f"💡 Info: Generated route {click.style(route_name, bold=True)}\n", fg="cyan")
        if new_model_name:
            is_successful, message = model_make_file(new_model_name)
            click.echo(message)
            all_successful = all_successful and is_successful

    is_successful, messages = wire_controller_route_view(
        relative_path,
        action,
        controller_name,
        route_name)

    all_successful = all_successful and is_successful

    for message in messages:
        click.echo(message)

    if not all_successful:
        click.secho("⚠️  Warning: One or more make view steps produced a warning or failure.", fg="yellow", bold=True)
