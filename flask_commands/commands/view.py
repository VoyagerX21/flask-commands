import os
import click
from flask_commands.utils import camel_to_snake, controller_add_method, \
    controller_make_file, generate_controller_name_from, \
    generate_route_file_path_and_blueprint_name, generate_route_name_from, \
    parse_dots, route_add_method, \
    route_make_directory_and_register_blueprint, view_make_file


@click.command(name="make:view")
@click.argument("dotted_path_with_name")
@click.option("--controller", "controller_name", default=None,
              help="Optional controller class name (example PostController).")
@click.option("-c", "--generate-controller", if_flag=True,
              help="Optional controller flag to generate an inferred controller from the dotted path name.")
@click.option("--route", "route_name", default=None,
              help="Optional route class name (example post).")
@click.option("-r", "--generate-route", is_flag=True,
              help="Optional route flag to generate an infered route from the dotted path name.")
@click.option("--model", "model_name", default=None,
              help="Optional model name (example Post which makes the database table 'posts').")
@click.option("-m", "--generate-model", is_flag=True,
              help="Optional model flag to generate an infered model from the dotted path name.")
def make_view(
    dotted_path_with_name: str,
    controller_name: str | None,
    generate_controller: bool,
    route_name: str | None,
    generate_route: bool,
    model_name: str | None,
    generate_model: bool) -> None:
    """
    Create a template view file under app/templates/<folder>/<name>.html

    Designed Usage for components views:
        flask make:view card

    Designed Usage for initial CRUD parts:
        flask make:view posts.index -crm
        flask make:view posts.index --controller PostController --route /posts --model Post

    Designed Usage for additional CRUD parts:
        flask make:view posts.show -cr
        flask make:view posts.show --controller PostController --route /posts/<int:post_id>

    Additional Usage:
        flask make:view posts.index -c
        flask make:view posts.index --controller PostController
        flask make:view posts.index -r
        flask make:view posts.index --route /posts
        flask make:view posts.index -m
        flask make:view posts.index --model Post
        flask make:view posts.index -cm
        flask make:view posts.index --controller PostController --model Post
        flask make:view posts.index -rm
        flask make:view posts.index --route /posts --model Post
    """
    relative_path, action = parse_dots(dotted_path_with_name)
    relative_view_file_path = os.path.join(relative_path, f"{action}.html")
    destination_file_path = \
        os.path.join("app", "templates", relative_view_file_path)
    try:
        view_make_file(destination_file_path, action)
        click.echo(f"📄 File created at ",
                   f"{click.style(destination_file_path, bold=True)}")
    except FileExistsError:
        click.echo(f"⚠️ Warning: A file already exist at
                   {destination_file_path}.  Nothing happened.")
    except Exception as exception:
        click.echo(f"💣 Error: {exception}")

    # Infer controller name if not provided
    if generate_controller and controller_name is None:
        if relative_path !== '':
            controller_name = generate_controller_name_from(relative_path)
            click.echo(f"Inferred the controller name as "
                       f"{click.style(controller_name, bold=True)}")
        else:
            click.echo(f"⚠️ Warning: Could not infer the controller name "
                       f"from {dotted_path_with_name}")

    # Infer route name if not provided
    if generate_route and route_name is None:
        route_name = generate_route_name_from(dotted_path_with_name)
        click.echo(f"Inferred the route name as "
                   f"{click.style(route_name, bold=True)}")


    # Infer model name if not provided
    if generate_model and model_name is None:
        message, model_name, table_name = \
            generate_model_name_from(relative_path, dotted_path_with_name)
        click.echo(message)

    # If a controller_name was provided or inferred
    if controller_name:
        controller_file_path = \
            os.path.join(
                "app",
                "controllers",
                f"{camel_to_snake(controller_name)}.py")
        try:
            # if controller exist just add the method
            if os.path.exists(controller_file_path):
                is_successful, message = controller_add_method(
                    controller_name, action, relative_view_file_path)
            # else create the controller and the method
            else:
                is_successful, message = controller_make_file(
                    controller_name, action, relative_view_file_path)
            click.echo(message)
        except Exception as exception:
            click.echo(f"💣 Error: {exception}")

    # If a controller_name was provided or inferred
    if route_name:
        route_file_path, blueprint_name = \
            generate_route_file_path_and_blueprint_name(
                dotted_path_with_name, relative_path)
        try:
            if os.path.exists(route_file_path):
                is_successful, message = \
                    route_add_method(
                        route_name, action, relative_path, controller_name)
            else:
                is_successful, message = \
                    route_make_directory_and_register_blueprint(
                        route_name,
                        action,
                        relative_path,
                        blueprint_name,
                        controller_name)
            click.echo(message)
        except Exception as exception:
            click.echo(f"💣 Error: {exception}")

    # If a model_name was provided or inferred
    if model_name:
        model_file_path = os.path.join("app", "models", f"{model_name.lower()}.py")
        model_init_path = os.path.join("app", "models", "__init__.py")
        try:
            init_contents = [f"from .{model_name.lower()} import {model_name}"]
            _file_append(model_init_path, init_contents)
            file_contents = [
                "from app import db",
                "from datetime import datetime, timezone",
                "",
                f"class {model_name}(db.Model):",
                f"    __tablename__ = '{generate_table_name_from_model_name(model_name)}'",
                "    # Columns",
                "    id = db.Column(db.Integer, primary_key=True)",
                "    created_at = db.Column(db.DateTime(timezone=True),",
                "                           index=True, ",
                "                           default=lambda: datetime.now(timezone.utc))",
                "    updated_at = db.Column(db.DateTime(timezone=True),",
                "                           default=lambda: datetime.now(timezone.utc), ",
                "                           onupdate=lambda: datetime.now(timezone.utc))",
                "",
                "    def store_in_database(self):",
                "        db.session.add(self)",
                "        db.session.commit()",
                "",
                "    def delete_from_database(self):",
                "        db.session.delete(self)",
                "        db.session.commit()",
                "",
                "    def __repr__(self):",
                '        """Model representation for Code Debugging"""',
                f"        return f'<{model_name} id:{{self.id}}>'",
            ]
            _file_write(model_file_path, file_contents)
        except Exception as exception:
            click.echo(f"💣 Error: {exception}")

