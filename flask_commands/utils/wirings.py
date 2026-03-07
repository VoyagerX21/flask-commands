import os
import click

from flask_commands.utils.data_types import (
    ActionResult,
    ControllerResult,
    CrudResourceResult,
    ModelResult,
    RouteResult,
    ScaffoldStatus
)
from flask_commands.utils.models import (
    model_get_registered_models,
    model_model_names_to_snake_case_names
)

from .controllers import controller_add_method, controller_make_file
from .naming import camel_to_snake
from .routes import (
    route_add_method,
    route_generate_route_and_blueprint_metadata,
    route_generate_route_name,
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
        tuple[ActionResult, ControllerResult | None, RouteResult | None, list[str]]:
            - ActionResult: structured result for the full action
            - ControllerResult | None: controller result when controller wiring ran
            - RouteResult | None: route directory result when route directory creation ran
            - list[str]: collected human-readable messages

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

    messages: list[str] = []
    all_successful = True

    view_directory = "mains" if is_view_directory_mains else relative_path

    view_file_path: str | None = None
    view_status = ScaffoldStatus.SKIPPED
    controller_result: ControllerResult | None = None
    route_result: RouteResult | None = None

    http_method = route_http_method_for_action(action)
    if http_method == "GET":
        relative_view_file_path = \
            os.path.join(view_directory, f"{action}.html")
        destination_file_path = \
            os.path.join("app", "templates", relative_view_file_path)

        view_status, message = view_make_file(destination_file_path)
        view_file_path = destination_file_path
        all_successful = all_successful and (
            view_status == ScaffoldStatus.ADDED)
        messages.append(message)

    # If a controller_name was provided or generated
    if controller_name:
        controller_file_path = os.path.join(
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
        all_successful = all_successful and controller_result.is_successful
        messages.append(message)

    route_status = ScaffoldStatus.SKIPPED
    url_for_example = ""

    # If a controller_name was provided or generated
    if route_name:
        route_directory_path = os.path.join(
            "app", "routes", relative_path if relative_path else 'mains')
        try:
            if os.path.exists(route_directory_path):
                action_result, message = \
                    route_add_method(
                        relative_path,      # this is everything before the last part of dotted_path_with_action replacing . with /
                        action,             # in CRUD this is index, create, update, show... else this is just the last part of dotted_path_with_action
                        route_directory_path,  # this is app/routes/{relative_path} or app/routes/main if relative path is ''
                        route_name,         # this is the url path like /posts/<int:post_id> or /admin/posts/comments
                        controller_name)    # contoller_name is like PostController

            else:
                route_result, action_result, message = \
                    route_write_directory_and_register_blueprint(
                        relative_path,      # this is everything before the last part of dotted_path_with_action replacing . with /
                        action,             # in CRUD this is index, create, update, show... else this is just the last part of dotted_path_with_action
                        route_directory_path,  # this is app/routes/{relative_path} or app/routes/main if relative path is ''
                        route_name,         # this is the url path like /posts/<int:post_id> or /admin/posts/comments
                        controller_name)    # contoller_name is like PostController
                all_successful = all_successful and route_result.is_successful
            all_successful = all_successful and action_result.is_successful
            route_status = action_result.route_status
            url_for_example = action_result.url_for_example
            messages.append(message)
        except Exception as exception:
            all_successful = False
            messages.append(click.style(f"💣 Error:\n {exception}", fg="red"))

    action_result = ActionResult(
        action=action,
        http_method=http_method,
        route_name=route_name if route_name else "",
        url_for_example=url_for_example,
        is_successful=all_successful,
        view_file_path=view_file_path,
        view_status=view_status,
        route_status=route_status
    )
    return action_result, controller_result, route_result, messages

def wiring_generate_crud_resource_resource_result(
        relative_path: str, controller_name: str
) -> tuple[CrudResourceResult, list[str]]:
    restful_actions = ["index", "show", "create", "store", "edit", "update", "destroy"]

