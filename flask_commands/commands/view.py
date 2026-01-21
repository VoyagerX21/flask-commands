import os
import click

from flask_commands.utils.controllers import controller_infer_name_from
from flask_commands.utils.models import (
    model_infer_name_from,
    model_make_file
)
from flask_commands.utils.files import is_project_root
from flask_commands.utils.routes import route_infer_name_from
from flask_commands.utils.scaffold import split_dotted_path
from flask_commands.utils.wirings import wire_controller_route_view

@click.command(name="make:view")
@click.argument("dotted_path_with_name")
@click.option("--controller", "controller_name", default=None,
              help="Optional controller class name (example PostController).")
@click.option("-c", "--generate-controller", is_flag=True,
              help="Optional controller flag to generate an inferred controller from the dotted path name.")
@click.option("--route", "route_name", default=None,
              help="Optional route class name (example /posts).")
@click.option("-r", "--generate-route", is_flag=True,
              help="Optional route flag to generate an inferred route from the dotted path name.")
@click.option("--model", "model_name", default=None,
              help="Optional model name (example Post which makes the database table 'posts').")
@click.option("-m", "--generate-model", is_flag=True,
              help="Optional model flag to generate an inferred model from the dotted path name.")
def make_view(
    dotted_path_with_name: str,
    controller_name: str | None,
    generate_controller: bool,
    route_name: str | None,
    generate_route: bool,
    model_name: str | None,
    generate_model: bool) -> None:
    """
    \b
    Create a template view file under app/templates/<folder>/<name>.html.
    You can also optionally connect this view to a controller, route, and model.
    \b
    ─── Understanding DOTTED_PATH_WITH_NAME ───
    The dotted path defines the folder and file name:
        <folder>.<name> → app/templates/<folder>/<name>.html
        Example: posts.index → app/templates/posts/index.html
    \b
    You can also nest folders for relationships:
        admin.users.index → app/templates/admin/users/index.html
        posts.images.index → app/templates/posts/images/index.html
    \b
    ─── Simple Component Views ───
    For standalone components like a button:
        flask make:view button
    \b
    ─── CRUD Views ───
    For RESTful actions (index, show, create, store, edit, update, destroy/delete):
    Initial CRUD setup (controller, route, and model):
        flask make:view posts.index -crm
        flask make:view posts.index --controller PostController --route /posts --model Post
    \b
    Additional CRUD actions (e.g., show):
        flask make:view posts.show -cr
        flask make:view posts.show --controller PostController --route /posts/<int:post_id>
    \b
    ─── Flags ───
    Optional flags can be combined as seen above:
        -c / --generate-controller    generate inferred controller
        -r / --generate-route         generate inferred route
        -m / --generate-model         generate inferred model
    \b
    If you prefer explicit control:
        --controller CONTROLLER_NAME  set a specific controller
        --route ROUTE_NAME            set a specific route
        --model MODEL_NAME            set a specific model
    """
    if not is_project_root():
        return

    relative_path, action = split_dotted_path(dotted_path_with_name)

    # Infer controller name if not provided
    if generate_controller and controller_name is None:
        if relative_path != '':
            controller_name = controller_infer_name_from(relative_path)
            click.secho(f"💡 Info: Inferred controller name as {click.style(controller_name, bold=True)}", fg="cyan")
        else:
            controller_name = 'MainController'

    # Infer route name if not provided
    if generate_route and route_name is None:
        route_name = route_infer_name_from(dotted_path_with_name)
        click.secho("💡 Info: Inferred route name as "
                   f"{click.style(route_name, bold=True)}", fg="cyan")

    # Infer model name if not provided
    if generate_model and model_name is None:
        model_name = model_infer_name_from(relative_path, dotted_path_with_name)
        click.secho(f"💡 Info: Inferred model name as "
                   f"{click.style(model_name, bold=True)}", fg="cyan")

    click.echo("\n")

    all_successful = True
    is_successful, messages = wire_controller_route_view(
        dotted_path_with_name,
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
        click.secho("⚠️  Warning: One or more make view steps failed.", fg="yellow", bold=True)
