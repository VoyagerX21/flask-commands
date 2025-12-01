import os
import re
import click
from flask_commands.utils import controller_add_method, controller_make_file, \
    camel_to_snake, parse_dots, view_make_file


@click.command(name="make:view")
@click.argument("dotted_name")
@click.option("--controller", "controller_name", default=None,
              help="Optional controller class name to update (e.g. PostController)")
def make_view(dotted_path_with_name: str) -> None:
    """
    Create a template view file under app/templates/<folder>/<name>.html

    Usage:
        flask make:view posts.index
    """
    relative_path, filename = parse_dots(dotted_path_with_name)
    destination_path = os.path.join("app", "templates", relative_path)
    try:
        view_make_file(destination_path, filename)
        click.echo(f"📄 File created at {click.style(destination_path, bold=True)}")
    except FileExistsError:
        click.echo(f"⚠️ Warning: A file already exist at {destination_path}.  Nothing happened.")
    except Exception as exc:
        click.echo(f"💣 Error: {exc}")

    # If a controller was provided, ensure it has a matching static method
    if controller_name:
        controller_file_path = os.path.join("app", "controllers", f"{camel_to_snake(controller_name)}.py")
        try:
            # if controller exist just add the method
            if os.path.exists(controller_file_path):
                controller_add_method(controller_name, method_name = filename)
            # else create the controller and the method
            else:
                controller_make_file(controller_name, method_name = filename)
        except Exception as exception:
            click.echo(f"💣 Error: {exc}")
