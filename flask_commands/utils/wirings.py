import os
import click

from flask_commands.utils.data_types import (
    ActionResult,
    ControllerResult,
    CrudResourceResult,
    RouteResult,
    ScaffoldStatus
)
from .controllers import controller_add_method, controller_make_file
from .naming import camel_to_snake
from .routes import (
    route_add_method,
    route_http_method_for_action,
    route_write_directory_and_register_blueprint
)
from .views import view_make_file


def wire_controller_route_view(
    relative_path: str,
    action: str,
    controller_name: str | None,
    route_name: str | None,
    is_view_directory_mains: bool = False,
) -> tuple[ActionResult, ControllerResult | None, RouteResult | None, list[str]]:
    """
    Wire together the view, controller, and route for a single action.

    For GET actions, this creates the view template first. The template is
    normally written under `app/templates/<relative_path>/`. When
    `is_view_directory_mains` is True, root view generation is grouped under
    `app/templates/mains/`, and any generated controller method will render
    that same template path.

    If `controller_name` is provided, this function ensures the controller
    method exists by adding it to an existing controller file or creating the
    controller file first.

    If `route_name` is provided, this function appends the route to an existing
    route package or creates and registers the route package when it does not
    yet exist. Root routes use the `mains` route package.

    Args:
        relative_path (str): Slash-delimited path before the action
            (examples: "", "posts", "posts/comments").
        action (str): Action name (examples: "index", "show", "store").
        controller_name (str | None): Controller class name to use, if any.
        route_name (str | None): URL rule to wire, if any.
        is_view_directory_mains (bool): When True, use the default `mains`
            template namespace for inferred root GET views.

    Returns:
        tuple[bool, list[str]]: Overall success flag and collected step messages.

    Examples:
        >>> is_successful, messages = wire_controller_route_view(
        ...     relative_path="posts",
        ...     action="index",
        ...     controller_name="PostController",
        ...     route_name="/posts",
        ... )
        >>> is_successful
        True
    """

    messages = []
    all_successful = True

    view_directory = "mains" if is_view_directory_mains else relative_path

    method = route_http_method_for_action(action)
    if method == "GET":
        relative_view_file_path = \
            os.path.join(view_directory, f"{action}.html")
        destination_file_path = \
            os.path.join("app", "templates", relative_view_file_path)

        is_successful, message = view_make_file(destination_file_path)
        all_successful = all_successful and is_successful
        messages.append(message)

    # If a controller_name was provided or generated
    if controller_name:
        controller_file_path = \
            os.path.join(
                "app",
                "controllers",
                f"{camel_to_snake(controller_name)}.py")

        # if controller exist just add the method
        if os.path.exists(controller_file_path):
            controller_result, message = controller_add_method(
                relative_path,
                action,
                controller_name,
                controller_file_path,
                route_name,
                view_directory)
        # else create the controller and the method
        else:
            controller_result, message = controller_make_file(
                relative_path,
                action,
                controller_name,
                controller_file_path,
                route_name,
                view_directory)
        all_successful = all_successful and (
            controller_result.status == ScaffoldStatus.ADDED)
        messages.append(message)

    # If a controller_name was provided or generated
    if route_name:
        route_directory_path = os.path.join(
            "app", "routes", relative_path if relative_path else 'mains')
        try:
            if os.path.exists(route_directory_path):
                is_successful, message = \
                    route_add_method(
                        relative_path,      # this is everything before the last part of dotted_path_with_action replacing . with /
                        action,             # in CRUD this is index, create, update, show... else this is just the last part of dotted_path_with_action
                        route_directory_path,  # this is app/routes/{relative_path} or app/routes/main if relative path is ''
                        route_name,         # this is the url path like /posts/<int:post_id> or /admin/posts/comments
                        controller_name)    # contoller_name is like PostController
            else:
                is_successful, message = \
                    route_write_directory_and_register_blueprint(
                        relative_path,      # this is everything before the last part of dotted_path_with_action replacing . with /
                        action,             # in CRUD this is index, create, update, show... else this is just the last part of dotted_path_with_action
                        route_directory_path,  # this is app/routes/{relative_path} or app/routes/main if relative path is ''
                        route_name,         # this is the url path like /posts/<int:post_id> or /admin/posts/comments
                        controller_name)    # contoller_name is like PostController
            all_successful = all_successful and is_successful
            messages.append(message)
        except Exception as exception:
            all_successful = False
            messages.append(click.style(f"💣 Error:\n {exception}", fg="red"))

    return all_successful, messages

def wire_crud_resource(
    relative_path: str,
    controller_name: str,
) -> tuple[CrudResourceResult, list[str]]:
    pass
