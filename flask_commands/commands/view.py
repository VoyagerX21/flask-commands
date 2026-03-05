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

@click.command(name="make:view", short_help="Create a view and optionally wire controller, route, and model.")
@click.argument("dotted_path_with_action")
@click.option("--controller", "controller_name", default=None,
              help="Use this controller class (for example: PostController).")
@click.option("-c", "--generate-controller", is_flag=True,
              help="Generate controller name from the dotted path (ignored if --controller is set)")
@click.option("--route", "route_name", default=None,
              help="Use this route path (for example: /posts or /posts/<int:post_id>).  Skips route inference and model prompt.")
@click.option("-r", "--generate-route", is_flag=True,
              help="Generate route from the dotted path (ignored if --route is set).  For RESTful actions, may prompt to generate a missing model when the last segment is not a registered model.")
@click.option("--model", "model_name", default=None,
              help="Use/create this model name (for example: Post which makes the database table 'posts').  Also avoids the missing-model prompt during route inference.")
@click.option("-m", "--generate-model", is_flag=True,
              help="Generate and create model from the dotted path (ignored if --model is set).  Also avoids the missing-model prompt during route inference.")
def make_view(
    dotted_path_with_action: str,
    controller_name: str | None,
    generate_controller: bool,
    route_name: str | None,
    generate_route: bool,
    model_name: str | None,
    generate_model: bool) -> None:
    """
    Create a view template and optionally wire a controller, route, and model.

    `dotted_path_with_action` determines the default template path
    `app/templates/<relative_path>/<action>.html`. For root actions like
    `landing`, the default template is `app/templates/landing.html`.

    When root controller and/or route wiring is auto-generated (for example
    `flask make:view landing -rc`), the generated root artifacts are organized
    under the default `mains` namespace:
    - view template at `app/templates/mains/<action>.html`
    - route wiring in `app/routes/mains`
    - controller wiring through `MainController`

    Explicit `--controller` and `--route` values are treated as user-directed
    wiring and do not trigger that implicit `mains` template placement.

    Use `-c/-r/-m` to generate controller/route/model, or provide
    `--controller`, `--route`, and `--model`. If `--generate-route` is used on
    RESTful paths with a missing model segment, you may be prompted before the
    route shape is generated. To avoid that prompt, provide `--route`,
    `--model`, or use `--generate-model`.
    """


    if not file_is_project_root():
        return

    is_successful, dotted_path_with_action = \
        normalize_dotted_path_with_action(dotted_path_with_action)
    if not is_successful:
        message = dotted_path_with_action
        click.echo(message)
        return

    all_successful: bool = True
    info_updates: list[str] = []
    message_updates: list[str] = []

    relative_path, action = \
        split_dotted_path_with_action_into_relative_path_and_action(
            dotted_path_with_action)

    is_view_directory_mains = (
        relative_path == ""
        and (
            (generate_controller and controller_name is None)
            or (generate_route and route_name is None)
        )
    )

    # 1) Generate controller name if not provided
    if generate_controller and controller_name is None:
        if relative_path != '':
            controller_name = controller_generate_controller_name_from_relative_path(relative_path)
            info_updates.append(f"Generated controller {controller_name}")
        else:
            controller_name = 'MainController'
            info_updates.append(f"Generated controller {controller_name}")

    # Generate model name if not provided
    if generate_model and model_name is None:
        model_name = \
            model_generate_model_name_from_dotted_path_with_action(dotted_path_with_action)
        info_updates.append(f"Generated model {model_name}")

    allow_model_prompt = not bool(model_name)

    # If a model_name was provided or generated
    if model_name:
        model_result, message = model_make_file(model_name)
        message_updates.append(message)
        all_successful = all_successful and model_result.is_successful

    # Generate route name if not provided
    if generate_route and route_name is None:
        route_name, new_model_name = \
            route_generate_route_name_with_model_prompt(
                dotted_path_with_action, allow_model_prompt)
        info_updates.append(f"Generated route {route_name}")
        if new_model_name:
            model_result, message = model_make_file(new_model_name)
            message_updates.append(message)
            all_successful = all_successful and model_result.is_successful

    is_successful, messages = wire_controller_route_view(
        relative_path,
        action,
        controller_name,
        route_name,
        is_view_directory_mains)
    message_updates.extend(messages)
    all_successful = all_successful and is_successful

    if info_updates:
        info_messages = (
            click.style("💡 Info: Generated From Flags\n", fg="cyan", bold=True) +
            "".join(click.style(f"    - {update}\n", fg="cyan")
                    for update in info_updates)
        )
        click.echo(info_messages)

    if message_updates:
        for update in message_updates:
            click.echo(update)

    if not all_successful:
        click.secho("⚠️  Warning: One or more make view steps produced a warning or failure.", fg="yellow", bold=True)
