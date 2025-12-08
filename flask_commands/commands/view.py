import os
import click
from flask_commands.utils import camel_to_snake, controller_add_method, \
    controller_make_file, generate_controller_name_from, \
    generate_route_name_from, parse_dots, singularize, \
    view_make_file, _file_write


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
        click.echo(f"📄 File created at {click.style(destination_file_path, bold=True)}")
    except FileExistsError:
        click.echo(f"⚠️ Warning: A file already exist at {destination_file_path}.  Nothing happened.")
    except Exception as exception:
        click.echo(f"💣 Error: {exception}")

    # Infer controller name if not provided
    if generate_controller and controller_name is None:
        if relative_path !== '':
            controller_name = generate_controller_name_from(relative_path)
            click.echo(f"Inferred the controller name as {click.style(controller_name, bold=True)}")
        else:
            click.echo(f"⚠️ Warning: Could not infer the controller name from {dotted_path_with_name}")

    if generate_route and route_name is None:
        route_name = generate_route_name_from(dotted_path_with_name)
        click.echo(f"Inferred the route name as {click.style(route_name, bold=True)}")

    # If a controller was provided, ensure it has a matching static method
    if controller_name:
        controller_file_path = os.path.join("app", "controllers", f"{camel_to_snake(controller_name)}.py")
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

    # If a route was provided, ensure it has a matching url
    if route_name:
        # TODO: HERE IS HOW THIS SHOULD LOOK AND THE CODE IS BELOW YOU JUST HAVE TO ADD THE CODE TO utils.py AND WIRE EVERYTHING TOGETHER
        route_file_path, blueprint_name = generate_route_file_path_and_blueprint_name(dotted_path_with_name)
        try:
            if os.path.exists(route_file_path):
                is_successful, message = route_add_method()
            else:
                is_successful, message = route_make_directory_and_register_blueprint()
            click.echo(message)
        except Exception as exception:
            click.echo(f"💣 Error: {exception}")

        #TODO: THIS IS THE CODE FOR ABOVE JUST MOVE IT TO utils.py
        if "." not in dotted_path_with_name:
            route_file_path = os.path.join("app", "routes", "mains")
            blueprint_name = 'mains'
        else:
            route_file_path = os.path.join("app", "routes", relative_path)
            blueprint_name = relative_path.replace("/", "_")

        if os.path.exists(route_file_path):
            # The route folder is already there so we
            # just need to add to the routes.py file
            route_file_path = os.path.join(route_file_path, "routes.py")
            using_controller_name = controller_name if controller_name else 'MainController'
            method = "POST" if action in ["store", "update", "destroy", "delete"] else "GET"
            route_content = [
                ""
                f"@bp.route('{route_name.replace(relative_path, '')}', methods=['{method}'])"
                f"def {action}():"
                f"    return {using_controller_name}.{action}()"
            ]
            _file_append(route_file_path, route_content)
        else:
            # The route folder is not there so we need to create everything:
            #   1) create routes folder - check
            os.makedirs(route_file_path)
            #   2) __init__.py file - check
            route_init_path = os.path.join(route_file_path, "__init__.py")
            route_init_content = [
                 "from flask import Blueprint",
                 "",
                f"bp = Blueprint('{blueprint_name}', __name__)",
                 "",
                f"from app.routes.{blueprint_name.replace("_", ".")} import routes"
            ]
            _file_write(route_init_path, route_init_content)
            #   3) routes.py file - check
            route_file_path = os.path.join(route_file_path, "routes.py")
            using_controller_name = controller_name if controller_name else 'MainController'
            method = "POST" if action in ["store", "update", "destroy", "delete"] else "GET"
            route_content = [
                f"from app.controllers import {using_controller_name}",
                "",
                f"from app.routes.{blueprint_name.replace("_", ".")} import bp"
                "",
                f"@bp.route('{route_name.replace(relative_path, '')}', methods=['{method}'])"
                f"def {action}():"
                f"    return {using_controller_name}.{action}()"
            ]
            _file_write(route_file_path, route_content)
           #   4) update the __init__.py in app directory to include the new blueprint
            app_init_path = os.path.join("app", "__init__.py")
            with open(app_init_path, "r", encoding="utf-8") as f:
                source = f.read()

            match = re.search(r"^\s*return app\b", source, flags=re.MULTILINE)
            insert_index = match.start()
            new_blueprint = [
                f"    from {route_file_path.replace('/', '.')} import bp as {blueprint_name}_blueprint"
                f"    app.register_blueprint({blueprint_name}_blueprint)"
            ]
            new_blueprint = "\n".join(new_blueprint)
            new_content = source[:insert_index] + new_blueprint + "\n" + source[insert_index:]
            with open(app_init_path, "w") as f:
                f.write(new_content)


