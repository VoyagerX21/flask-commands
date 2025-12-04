import os
import re
import click
from flask_commands.utils import controller_add_method, controller_make_file, \
    camel_to_snake, parse_dots, view_make_file


@click.command(name="make:view")
@click.argument("dotted_path_with_name")
@click.option("--controller", "controller_name", default=None,
              help="Optional controller class name to update (e.g. PostController)")
def make_view(dotted_path_with_name: str, controller_name: str | None) -> None:
    """
    Create a template view file under app/templates/<folder>/<name>.html

    Usage:
        flask make:view posts.index
        flask make:view posts.index --controller PostController
        flask make:view posts.index --controller PostController --route
    """
    relative_path, filename = parse_dots(dotted_path_with_name)
    relative_view_file_path = os.path.join(relative_path, f"{filename}.html")
    destination_file_path = \
        os.path.join("app", "templates", relative_view_file_path)
    try:
        view_make_file(destination_file_path, filename)
        click.echo(f"📄 File created at {click.style(destination_file_path, bold=True)}")
    except FileExistsError:
        click.echo(f"⚠️ Warning: A file already exist at {destination_file_path}.  Nothing happened.")
    except Exception as exception:
        click.echo(f"💣 Error: {exception}")

    # If a controller was provided, ensure it has a matching static method
    if controller_name:
        controller_file_path = os.path.join("app", "controllers", f"{camel_to_snake(controller_name)}.py")
        try:
            # if controller exist just add the method
            if os.path.exists(controller_file_path):
                completed, message = controller_add_method(
                    controller_name, filename, relative_view_file_path)
            # else create the controller and the method
            else:
                completed, message = controller_make_file(
                    controller_name, filename, relative_view_file_path)
            click.echo(message)
        except Exception as exception:
            click.echo(f"💣 Error: {exception}")
