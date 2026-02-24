import os
import click

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
    route_name: str | None
) -> tuple[bool, list[str]]:
    """
    Wire together view, controller, and route for a given action.

    Creates a view file for GET actions, ensures a controller method exists
    (creating the controller if needed), and adds or creates the route and
    blueprint for the given dotted path. Collects success/error messages for
    each step and returns overall status.

    Args:
        dotted_path_with_action (str): Dotted path like "posts.comments.show".
        relative_path (str): Slash-delimited path like "posts/comments".
        action (str): Action name (e.g., "index", "show", "store").
        controller_name (str | None): Controller class name or None.
        route_name (str | None): URL path like "/posts/<int:post_id>".

    Returns:
        tuple[bool, list[str]]: Overall success flag and list of messages.

    Examples:
        >>> is_successful, messages = wire_controller_route_view(
        ...     relative_path="posts",
        ...     action="index",
        ...     controller_name="PostController",
        ...     route_name="/posts"
        ... )
        >>> is_successful
        True
    """
    messages = []
    all_successful = True

    method = route_http_method_for_action(action)
    if method == "GET":
        relative_view_file_path = os.path.join(relative_path, f"{action}.html")
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
            is_successful, message = controller_add_method(
                relative_path,
                action,
                controller_name,
                route_name)
        # else create the controller and the method
        else:
            is_successful, message = controller_make_file(
                relative_path,
                action,
                controller_name,
                route_name)
        all_successful = all_successful and is_successful
        messages.append(message)

    # If a controller_name was provided or generated
    if route_name:
        route_directory_path = os.path.join("app", "routes", relative_path)
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

