import os
import click

from flask_commands.utils.data_types import (
    ActionResult,
    ControllerResult,
    CrudResult,
    ModelResult,
    RouteResult,
    ScaffoldStatus,
    WiringResult
)
from flask_commands.utils.controllers import (
    controller_add_method, 
    controller_make_file
)
from flask_commands.utils.models import (
    model_generate_model_name_from_dotted_path_with_action, 
    model_get_registered_models, 
    model_make_file, 
    model_model_names_to_snake_case_names
)
from flask_commands.utils.naming import camel_to_snake, singularize
from flask_commands.utils.routes import (
    route_add_method,
    route_generate_route_name,
    route_generate_route_visit_example,
    route_http_method_for_action,
    route_write_directory_and_register_blueprint
)
from flask_commands.utils.views import view_make_file

def wiring_generate_crud_result(
        relative_path: str,
        controller_name: str,
        controller_result: ControllerResult,
        model_result: ModelResult
) -> CrudResult:
    """
    Prepare and scaffold a full RESTful resource into one `CrudResult`.

    This function coordinates the canonical CRUD action set for a resource:

    - `index`
    - `show`
    - `create`
    - `store`
    - `edit`
    - `update`
    - `destroy`

    Workflow:
    1. Analyze `relative_path` and its segments.
    2. If the last segment is not a registered model, generate a fallback model
       and record its message in `CrudResult.message_updates`.
    3. Recompute registered model segments for route generation.
    4. Use `wiring_generate_wiring_result()` for each CRUD action.
    5. Aggregate:
       - controller method additions and existing methods
       - action-level results
       - route-directory creation result, when one occurred
       - warning/error messages
       - overall CRUD success

    Args:
        relative_path (str): Slash-delimited resource path, such as `"posts"` or
            `"posts/comments"`.
        controller_name (str): Controller class name for the resource.
        controller_result (ControllerResult): Existing or newly created
            controller result created earlier in the command flow.
        model_result (ModelResult): Aggregate model result assembled earlier in
            the command flow.

    Returns:
        CrudResult: Fully aggregated CRUD scaffold result, including command-level
        `message_updates`, `warning_updates`, and `is_successful`.

    Examples:
        >>> crud_result = wiring_generate_crud_result(
        ...     relative_path="posts",
        ...     controller_name="PostController",
        ...     controller_result=controller_result,
        ...     model_result=model_result,
        ... )
        >>> len(crud_result.action_results)
        7

    Notes:
    - `route_result` remains `None` when CRUD wiring only adds routes to an
      already existing route package.
    - Existing controller methods are accumulated on
      `controller_result.methods_existing`.
    - Success-path per-action messages are normalized into structured results
      and summary fields instead of being returned one-by-one.
    """

    restful_actions = ['index', 'show', 'create', 'store', 'edit', 'update', 'destroy']

    message_updates: list[str] = []
    is_successful: bool = True

    relative_path_segments = [
            segment for segment in relative_path.split("/") if segment]
    registered_models = model_get_registered_models()
    registered_snake_models = model_model_names_to_snake_case_names(
        registered_models)
    
    if relative_path_segments:
        relative_path_last_segment = relative_path_segments[-1]
        is_last_segment_a_model = \
            singularize(relative_path_last_segment) \
                in registered_snake_models

        if not is_last_segment_a_model:
            new_model_name = \
                model_generate_model_name_from_dotted_path_with_action(
                    f"{relative_path.replace('/', '.')}.index"
                )
            created_model, message = model_make_file(new_model_name)
            message_updates.append(message)
            is_successful = is_successful and created_model.is_successful
            model_result.is_successful = \
                model_result.is_successful and created_model.is_successful
            model_result.created_models.append(created_model)

            registered_models = model_get_registered_models()
            registered_snake_models = model_model_names_to_snake_case_names(
                registered_models)

    relative_path_segment_models = [
        segment for segment in relative_path_segments
        if singularize(segment) in registered_snake_models]

    crud_result = CrudResult(
        controller_result=controller_result,
        model_result=model_result,
        is_successful=is_successful,
        route_result=None,
        action_results=[],
        message_updates=message_updates,
        warning_updates=[]
    )

    for action in restful_actions:
        route_name = route_generate_route_name(
            relative_path=relative_path,
            action=action,
            is_restful=True,
            relative_path_segments=relative_path_segments,
            relative_path_segment_models=relative_path_segment_models
        )

        wiring_result = wiring_generate_wiring_result(
            relative_path,
            action,
            controller_name,
            route_name)

        crud_result.action_results.append(wiring_result.action_result)

        if wiring_result.controller_result is not None:
            if wiring_result.controller_result.status != ScaffoldStatus.EXISTS:
                crud_result.controller_result.is_successful = (
                    crud_result.controller_result.is_successful and
                    wiring_result.controller_result.is_successful
                )

            if wiring_result.controller_result.methods_added:
                crud_result.controller_result.methods_added.extend(
                    wiring_result.controller_result.methods_added
                )

            if wiring_result.controller_result.methods_existing:
                crud_result.controller_result.methods_existing.extend(
                    wiring_result.controller_result.methods_existing
                )

            if wiring_result.controller_result.status not in [ScaffoldStatus.ADDED, ScaffoldStatus.EXISTS]:
                crud_result.controller_result.status = \
                    wiring_result.controller_result.status

        if wiring_result.route_result is not None and crud_result.route_result is None:
            crud_result.route_result = wiring_result.route_result

        crud_result.warning_updates.extend(wiring_result.warning_messages)

    crud_result.is_successful = (
        crud_result.controller_result.is_successful
        and crud_result.model_result.is_successful
        and (
            crud_result.route_result.is_successful
            if crud_result.route_result is not None
            else True
        )
        and all(
            action_result.is_successful
            for action_result in crud_result.action_results
        )
    )

    return crud_result

def wiring_generate_wiring_result(
    relative_path: str,
    action: str,
    controller_name: str | None,
    route_name: str | None,
) -> WiringResult:
    """
    Wire one action's view, controller, and route artifacts and return a structured result.

    This function orchestrates the scaffolding for a single action and separates
    presentation concerns from execution concerns by returning a `WiringResult`
    object.

    Workflow:
    1. For GET actions, create the view template.
    2. Create the controller file or add the controller method.
    3. Add the route to an existing route package or create/register a new one.
    4. Split generated output into success messages and warning/error messages.

    View placement:
    - Uses `app/templates/<relative_path>/<action>.html`

    Route behavior:
    - Existing route package: delegates to `route_add_method`
    - Missing route package: delegates to
      `route_write_directory_and_register_blueprint`

    Args:
        relative_path (str): Slash-delimited path before the action, such as
            `"posts"` or `"posts/comments"`.
        action (str): Action name, such as `"index"`, `"show"`, or `"store"`.
        controller_name (str | None): Controller class to wire, if any.
        route_name (str | None): Route rule to wire, if any.

    Returns:
        WiringResult:
            - `action_result`: overall action-level result
            - `controller_result`: controller-level result when controller wiring ran
            - `route_result`: route-directory result when route directory creation ran
            - `success_messages`: human-readable success messages for this action
            - `warning_messages`: warning and error messages for this action

    Examples:
        >>> result = wiring_generate_wiring_result(
        ...     relative_path="posts",
        ...     action="index",
        ...     controller_name="PostController",
        ...     route_name="/posts",
        ... )
        >>> result.action_result.action
        'index'
        >>> result.action_result.http_method
        'GET'

    Notes:
    - `route_result` is only populated when route package creation/registration
      occurred during this action.
    - Warning ownership lives here so callers do not have to infer message
      ordering from internal step order.
    """

    success_messages: list[str] = []
    warning_messages: list[str] = []
    all_successful = True

    view_directory = relative_path

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
        if view_status == ScaffoldStatus.ADDED:
            success_messages.append(message)
        else:
            warning_messages.append(message)

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
        if controller_result.is_successful:
            success_messages.append(message)
        else:
            warning_messages.append(message)

    route_status = ScaffoldStatus.SKIPPED
    url_for_example = ""

    # If a controller_name was provided or generated
    if route_name:
        route_directory_path = os.path.join(
            "app", "routes", relative_path if relative_path else 'mains')
        try:
            if os.path.exists(route_directory_path):
                route_action_result, message = \
                    route_add_method(
                        relative_path,      # this is everything before the last part of dotted_path_with_action replacing . with /
                        action,             # in CRUD this is index, create, update, show... else this is just the last part of dotted_path_with_action
                        route_directory_path,  # this is app/routes/{relative_path} or app/routes/main if relative path is ''
                        route_name,         # this is the url path like /posts/<int:post_id> or /admin/posts/comments
                        controller_name)    # contoller_name is like PostController

            else:
                route_result, route_action_result, message = \
                    route_write_directory_and_register_blueprint(
                        relative_path,      # this is everything before the last part of dotted_path_with_action replacing . with /
                        action,             # in CRUD this is index, create, update, show... else this is just the last part of dotted_path_with_action
                        route_directory_path,  # this is app/routes/{relative_path} or app/routes/main if relative path is ''
                        route_name,         # this is the url path like /posts/<int:post_id> or /admin/posts/comments
                        controller_name)    # contoller_name is like PostController
                all_successful = all_successful and route_result.is_successful
            all_successful = all_successful and route_action_result.is_successful
            route_status = route_action_result.route_status
            url_for_example = route_action_result.url_for_example
            if route_action_result.is_successful and (
                route_result is None or route_result.is_successful
            ):
                success_messages.append(message)
            else:
                warning_messages.append(message)
        except Exception as exception:
            all_successful = False
            warning_messages.append(click.style(f"💣 Error:\n {exception}", fg="red"))

    action_result = ActionResult(
        action=action,
        http_method=http_method,
        route_name=route_name if route_name else "",
        url_for_example=url_for_example,
        is_successful=all_successful,
        visit_example=(
            route_generate_route_visit_example(route_name)
            if route_name and http_method == "GET" else None
        ),
        view_file_path=view_file_path,
        view_status=view_status,
        route_status=route_status
    )

    return WiringResult(
        action_result=action_result,
        controller_result=controller_result,
        route_result=route_result,
        success_messages=success_messages,
        warning_messages=warning_messages)
