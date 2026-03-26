import os
import click

from flask_commands.utils.controllers import (
    controller_generate_controller_name_from_relative_path,
    controller_generate_relative_path_from_controller_name,
    controller_make_file
)
from flask_commands.utils.data_types import (
    ControllerResult,
    CrudResult,
    ModelResult,
    ScaffoldStatus,
)
from flask_commands.utils.files import file_is_project_root
from flask_commands.utils.models import (
    model_generate_model_name_from_model_name,
    model_make_file
)
from flask_commands.utils.naming import camel_to_snake, pluralize
from flask_commands.utils.presents import present_output_blocks
from flask_commands.utils.wirings import wiring_generate_crud_result


@click.command(name="make:model")
@click.argument("model_name")
@click.option("--crud", is_flag=True,
               help="After creating model file(s), scaffold RESTful controller, routes, and GET view templates.")
@click.option("--flat", "force_flat", is_flag=True,
              help="With --crud this skips nested-model prompt by forcing flattened model generation. (requires --crud).")
@click.option("--nest", "force_nest", is_flag=True,
              help="With --crud this skips nested-model prompt by forcing nested model generation. (requires --crud).")
def make_model(model_name: str, crud: bool, force_flat: bool, force_nest: bool) -> None:
    """Create model file(s) and optionally scaffold CRUD wiring.

    Generates model file(s) and updates model registration.
    Use `--crud` to also generate controller, RESTful routes, and GET view templates.
    """
    if not file_is_project_root():
        return

    # near top of make_model (after project root check)
    if force_flat and force_nest:
        raise click.UsageError("Use either --flat or --nest, not both.")

    if (force_flat or force_nest) and not crud:
        raise click.UsageError("--flat and --nest can only be used with --crud.")

    all_successful: bool = True
    info_updates: list[str] = []
    message_updates: list[str] = []
    crud_result: CrudResult | None = None
    crud_warning_updates: list[str] = []
    model_result = ModelResult(is_successful=True)


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
            info_updates.append(
                f"Using --flat. Generated model(s): {non_nested_model_name}")
        elif force_nest:
            use_nested = True
            models_to_create = nested_model_names
            info_updates.append(
                f"Using --nest. Generated model(s): {', '.join(nested_model_names)}"
            )   
        else:
            click.echo("Detected nested model structure:")
            click.echo(f"  1) (flatten model) = {non_nested_model_name}")
            if len(nested_model_names) == 1:
                click.echo(f"  2) (nested leaf model) = {nested_model_names[0]}")
            else:
                click.echo(f"  2) (nested model chain) = {' -> '.join(nested_model_names)}")

            choice = click.prompt(
                "Choose model structure (1/2, flat/nest)",
                type=click.Choice(["1", "2", "flat", "nest"], case_sensitive=False),
                default="1",
                show_choices=False,
                show_default=True).lower()
            if choice in ["2", "nest"]:
                use_nested = True
                models_to_create = nested_model_names


    # 1) Generate model files (and register them) first
    for new_model_name in models_to_create:
        created_model, message = model_make_file(new_model_name)
        message_updates.append(message) 
        all_successful = all_successful and created_model.is_successful
        model_result.created_models.append(created_model)
        model_result.is_successful = (
            model_result.is_successful and created_model.is_successful
        )

    # 2) CRUD wiring (controller + routes + views)
    if crud:
        if use_nested:
            relative_path = \
                controller_generate_relative_path_from_controller_name(
                    f"{non_nested_model_name}Controller")
        else:
            relative_path = pluralize(camel_to_snake(non_nested_model_name))

        controller_name = \
            controller_generate_controller_name_from_relative_path(
                relative_path)
        controller_file_path = os.path.join(
            "app",
            "controllers",
            f"{camel_to_snake(controller_name)}.py",
        )
        if os.path.exists(controller_file_path):
            controller_result = ControllerResult(
                controller_name=controller_name,
                controller_file_path=controller_file_path,
                status=ScaffoldStatus.EXISTS,
                is_successful=True,
                registration_file_path=None,
                methods_added=[],
                methods_existing=[],
            )
        else:
            controller_result, message = controller_make_file(
                relative_path=None,
                action=None,
                controller_name=controller_name,
                controller_file_path=controller_file_path,
                route_name=None,
                view_directory=None)
            all_successful = all_successful and controller_result.is_successful

        crud_result = wiring_generate_crud_result(
            relative_path=relative_path,
            controller_name=controller_name,
            controller_result=controller_result,
            model_result=model_result
        )

        all_successful = all_successful and crud_result.is_successful
        
    present_blocks = present_output_blocks(
        info_updates=info_updates, 
        message_updates=message_updates, 
        crud_result=crud_result)
    for block in present_blocks:
        click.echo(block)
       
    if not all_successful:
        click.secho("⚠️  Warning: One or more make model steps produced a warning or failure.", fg="yellow", bold=True)
