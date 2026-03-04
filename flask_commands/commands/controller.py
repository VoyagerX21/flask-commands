import os
import click

from flask_commands.utils.controllers import (
    controller_make_file,
    controller_generate_relative_path_from_controller_name
)
from flask_commands.utils.data_types import ScaffoldStatus
from flask_commands.utils.files import file_is_project_root
from flask_commands.utils.models import (
    model_generate_hierarchy_from_controller_name,
    model_generate_model_name_from_controller_name,
    model_generate_model_name_from_dotted_path_with_action,
    model_get_registered_models,
    model_make_file,
    model_model_names_to_snake_case_names
)
from flask_commands.utils.naming import camel_to_snake, singularize
from flask_commands.utils.routes import route_generate_route_name
from flask_commands.utils.wirings import wire_controller_route_view


@click.command(name="make:controller")
@click.argument("controller_name")
@click.option("--crud", is_flag=True,
              help="Scaffold RESTful routes and controller methods (index/show/create/store/edit/update/destroy), plus GET view templates.")
@click.option("--model", "model_name", default=None,
              help="Use/create this model name before wiring (for example: Post).")
@click.option("-m", "--generate-model", is_flag=True,
              help="Generate and create model name(s) from the controller name (ignored if --model is set).")
@click.option("--flat", "force_flat", is_flag=True,
              help="With --generate-model, force flatten model generation and skip nested-model prompt.")
@click.option("--nest", "force_nest", is_flag=True,
              help="With --generate-model, force nested model generation and skip nested-model prompt.")
def make_controller(
    controller_name: str,
    crud: bool,
    model_name: str | None,
    generate_model: bool,
    force_flat: bool,
    force_nest: bool,) -> None:
    """Create a controller and optionally scaffold models and CRUD wiring.

    Creates `app/controllers/<controller>.py`.
    Use `--crud` for RESTful scaffolding and `--model` or `--generate-model` for model generation.
    """

    if not file_is_project_root():
        return

    if force_flat and force_nest:
        raise click.UsageError("Use either --flat or --nest, not both.")

    if (force_flat or force_nest) and not generate_model:
        raise click.UsageError("--flat and --nest can only be used with --generate-model.")

    if (force_flat or force_nest) and model_name:
        raise click.UsageError("--flat and --nest cannot be used with --model.")

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
    all_successful: bool = True
    info_updates: list[str] = []
    message_updates: list[str] = []

    controller_result, message = controller_make_file(
        relative_path=None,
        action=None,
        controller_name=controller_name,
        controller_file_path=controller_file_path,
        route_name=None,
        view_directory=None)
    message_updates.append(message)
    all_successful = all_successful and (
        controller_result.status == ScaffoldStatus.ADDED)

    # Generate model name(s) if not provided
    model_names: list[str] = []

    if model_name:
        model_names = [model_name]
    # Generate model name if not provided
    elif generate_model:
        non_nested_model_name, nested_model_names = \
            model_generate_model_name_from_controller_name(controller_name)
        forced_choice = "flat" if force_flat else "nest" if force_nest else None
        if nested_model_names \
                and nested_model_names != [non_nested_model_name]:
            namespace, parent_models, child_model_name = \
                model_generate_hierarchy_from_controller_name(controller_name)
            if forced_choice:
                use_flatten = forced_choice == "flat"
            elif parent_models:
                click.echo(
                    "Detected nested models:\n" + " -> ".join(parent_models)
                )
                click.echo(f"  1) (flatten resource model) = {non_nested_model_name}")
                click.echo(f"  2) (nested generated model) = {nested_model_names[0]}")
                choice = click.prompt(
                    "Choose model structure (1/2, flat/nest):",
                    type=click.Choice(["1", "2", "flat", "nest"], case_sensitive=False),
                    default="1",
                    show_choices=False,
                    show_default=True).lower()
                use_flatten = choice in ["1", "flat"]
            # If parent_models are empty and nested_model_names is not then
            # then _generate_nested_model_names_from_controller_name
            # puts the namespace in nested_model_names
            else:
                click.echo(
                    "Detected multiple child like segments:\n" +
                    ", ".join(nested_model_names))
                click.echo(f"1 (flatten resource model)  = {non_nested_model_name}")
                click.echo(f"2 (generate the following models) = {', '.join(nested_model_names)}")
                choice = click.prompt(
                    "Choose model structure (1/2, flat/nest):",
                    type=click.Choice(["1", "2", "flat", "nest"], case_sensitive=False),
                    default=1,
                    show_choices=False).lower()
                use_flatten = choice in ("1", "flat")

            if parent_models:
                chosen = non_nested_model_name if use_flatten else nested_model_names[0]
                model_names = [chosen]
            else:
                model_names = [non_nested_model_name] if use_flatten else nested_model_names
        else:
            model_names = [non_nested_model_name]
        generated_models = ', '.join(model_names)
        if forced_choice == "flat":
            info_updates.append(
                f"Using --flat. Generated model(s): {generated_models}")
        elif forced_choice == "nest":
            info_updates.append(
                f"Using --nest. Generated model(s): {generated_models}")
        else:
            info_updates.append(f"Generated model(s): {generated_models}")

    # If a model_name was provided or generated
    if model_names:
        for model_name in model_names:
            is_successful, message = model_make_file(model_name)
            message_updates.append(message)
            all_successful = all_successful and is_successful

    if crud:
        restful_actions = ['index', 'show', 'create', 'store', 'edit', 'update', 'destroy']
        relative_path = controller_generate_relative_path_from_controller_name(controller_name)
        relative_path_segments = [
            segment for segment in relative_path.split("/") if segment]

        registered_models = model_get_registered_models()
        registered_snake_models = model_model_names_to_snake_case_names(
            registered_models)

        if relative_path_segments:
            relative_path_last_segment = relative_path_segments[-1]
            is_last_segment_a_model = \
                singularize(relative_path_last_segment) \
                    in registered_snake_models

            if not is_last_segment_a_model:
                new_model_name = model_generate_model_name_from_dotted_path_with_action(
                    f"{relative_path.replace('/', '.')}.index"
                )
                is_successful, message = model_make_file(new_model_name)
                message_updates.append(message)
                all_successful = all_successful and is_successful

                registered_models = model_get_registered_models()
                registered_snake_models = model_model_names_to_snake_case_names(
                    registered_models)

        relative_path_segment_models = [
            segment for segment in relative_path_segments
            if singularize(segment) in registered_snake_models]

        for action in restful_actions:
            route_name = route_generate_route_name(
                relative_path=relative_path,
                action=action,
                is_restful=True,
                relative_path_segments=relative_path_segments,
                relative_path_segment_models=relative_path_segment_models
            )

            is_successful, messages = wire_controller_route_view(
                relative_path,
                action,
                controller_name,
                route_name)
            all_successful = all_successful and is_successful

            message_updates.extend(messages)

    if info_updates:
        info_messages = (
            click.style("💡 Info: Generated From Flags\n", fg="cyan", bold=True) +
            "".join(
                click.style(f"    - {update}\n", fg="cyan")
                for update in info_updates
            )
        )
        click.echo(info_messages)

    if message_updates:
        for update in message_updates:
            click.echo(update)


    if not all_successful:
        click.secho("⚠️  Warning: One or more make controller steps produced a warning or failure.", fg="yellow", bold=True)
