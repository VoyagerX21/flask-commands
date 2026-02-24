import click

from flask_commands.utils.controllers import (
    controller_generate_controller_name_from_relative_path,
    controller_generate_relative_path_from_controller_name
)
from flask_commands.utils.files import file_is_project_root
from flask_commands.utils.models import (
    model_generate_model_name_from_model_name,
    model_get_registered_models,
    model_make_file,
    model_model_names_to_snake_case_names
)
from flask_commands.utils.naming import camel_to_snake, pluralize, singularize
from flask_commands.utils.routes import route_generate_route_name
from flask_commands.utils.wirings import wire_controller_route_view


@click.command(name="make:model")
@click.argument("model_name")
@click.option("--crud", is_flag=True,
               help="After creating model file(s), scaffold RESTful controller, routes, and views.")
@click.option("--flat", "force_flat", is_flag=True,
              help="Use flatten model structure and skip the nested-model prompt (requires --crud).")
@click.option("--nest", "force_nest", is_flag=True,
              help="Use nested model structure and skip the nested-model prompt (requires --crud).")
def make_model(model_name: str, crud: bool, force_flat: bool, force_nest: bool) -> None:
    """Create a model and optionally scaffold full CRUD wiring.

    Generates model file(s) and updates model registration.
    Use `--crud` to also generate controller, RESTful routes, and view templates.
    """
    if not file_is_project_root():
        return

    # near top of make_model (after project root check)
    if force_flat and force_nest:
        raise click.UsageError("Use either --flat or --nest, not both.")

    if (force_flat or force_nest) and not crud:
        raise click.UsageError("--flat and --nest can only be used with --crud.")

    all_successful = True

    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_model_name(model_name)

    if not non_nested_model_name:
        click.secho("💣 Error: Could not generate model name from input.", fg="red", bold=True)
        return

    models_to_create = [non_nested_model_name]
    use_nested = False

    if crud \
            and nested_model_names \
            and nested_model_names != [non_nested_model_name]:
        if force_flat:
            use_nested = False
            models_to_create = [non_nested_model_name]
            click.secho(f"💡 Info: Using --flat. Generated model(s): "
                        f"{non_nested_model_name}", fg="cyan")
        elif force_nest:
            use_nested = True
            models_to_create = nested_model_names
            click.secho(f"💡 Info: Using --nest. Generated model(s): "
                        f"{', '.join(nested_model_names)}", fg="cyan")
        else:
            click.echo("Detected nested model structure:")
            click.echo(f"  1) (flatten model) = {non_nested_model_name}")
            if len(nested_model_names) == 1:
                click.echo(f"  2) (nested leaf model) = {nested_model_names[0]}")
            else:
                click.echo(f"  2) (nested model chain) = {' -> '.join(nested_model_names)}")

            choice = click.prompt(
                "Choose model structure (1/2, flatten/nested)",
                type=click.Choice(["1", "2", "flatten", "nested"], case_sensitive=False),
                default="1",
                show_choices=False,
                show_default=True).lower()
            if choice in ["2", "nested"]:
                use_nested = True
                models_to_create = nested_model_names


    # 1) Generate model files (and register them) first
    for new_model_name in models_to_create:
        is_successful, message = model_make_file(new_model_name)
        click.echo(message)
        all_successful = all_successful and is_successful

    # 2) CRUD wiring (controller + routes + views)
    if crud:
        restful_actions = ['index', 'show', 'create', 'store', 'edit', 'update', 'destroy']

        if use_nested:
            relative_path = \
                controller_generate_relative_path_from_controller_name(
                    f"{non_nested_model_name}Controller")
        else:
            relative_path = pluralize(camel_to_snake(non_nested_model_name))

        controller_name = \
            controller_generate_controller_name_from_relative_path(
                relative_path)

        relative_path_segments = [
            segment for segment in relative_path.split("/") if segment]
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
                route_name
            )
            all_successful = all_successful and is_successful

            for message in messages:
                click.echo(message)

    if not all_successful:
        click.secho("⚠️  Warning: One or more make model steps produced a warning or failure.", fg="yellow", bold=True)
