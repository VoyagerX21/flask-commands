import re
import os
import click

from flask_commands.utils.models import (
    model_get_registered_models,
    model_model_names_to_snake_case_names)
from flask_commands.utils.data_types import (
    ActionResult,
    RouteResult,
    RouteSpec,
    MissingModelPrompt,
    RouteStructurePrompt,
    PromptPlan,
    ScaffoldStatus
)

from .files import file_append_file, file_write_file
from .naming import pluralize, singularize
from .scaffold import (
    generate_restful_route,
    filter_falsy,
    split_dotted_path_with_action_into_relative_path_and_action)

def route_add_method(
        relative_path: str,
        action: str,
        route_directory_path: str,
        route_name: str,
        controller_name: str | None) -> tuple[ActionResult, str]:
    """
    Append a new route handler function to an existing `routes.py` file.

    This function builds a route function body for the given action (determining
    the HTTP method based on the action type where POST is used for store,
    update, destroy, delete and GET for all others), validates
    that the function name does not already exist in the target `routes.py`,
    appends the new handler , and returns a styled status message.


    Args:
        relative_path (str): Slash-delimited route path (examples: "posts", "posts/comments")
            the used dotted replace of the slashes is used in the `url_for`.
        action (str): Route action/function name (examples: "index", "show", "store").  Determines HTTP method of GET or POST.
        route_directory_path (str): Directory containing the target `routes.py`
            (example: "app/routes/posts").
        route_name (str): Flask URL rule for the route decorator
            (example: "/posts/<int:post_id>" or "/admin/posts/comments").
        controller_name (str | None): Controller class name used in the generated
            return call. Defaults to "MainController" when None.

    Returns:
        tuple[ActionResult, str]: A tuple containing:
            - ActionResult: Structured action result
                - WARNING and False when validation or append fails
                - ERROR and False when an acception rises
                - ADDED and True if the method was appended
            - str: Styled success/warning/error message describing what happened including and usage instructions.

    Examples:
        >>> is_successful, message = route_add_method(
        ...     relative_path="users",
        ...     action="index",
        ...     route_directory_path="app/routes/users",
        ...     route_name="/users",
        ...     controller_name="UserController"
        ... )
        >>> is_successful, message = route_add_method(
        ...     relative_path="recipes/comments",
        ...     action="show",
        ...     route_directory_path="app/routes/recipes/comments",
        ...     route_name="/recipes/<int:recipe_id>/comments/<int:comment_id>",
        ...     controller_name="RecipeCommentController"
        ... )
        >>> is_successful, message = route_add_method(
        ...     relative_path="",
        ...     action="about",
        ...     route_directory_path="app/routes/mains",
        ...     route_name="/about",
        ...     controller_name=None
        ... )
    """

    # The route folder is already there so we just need to add to routes.py
    # 1) _generate_route_method
    updates: list[str] = []
    _, route_file_path, _, _ = \
        route_generate_route_and_blueprint_metadata(
            relative_path, route_directory_path)
    try:
        route_content = _generate_route_method(action, route_name, controller_name)

        # 2) _validate_route_method_can_be_added
        is_successful, message = _apply_step_result(
            updates,
            _validate_route_method_can_be_added(action, route_file_path),
            "Could not prepare route file"
        )
        if not is_successful:
            return _generate_action_result(
                relative_path=relative_path,
                action=action,
                route_name=route_name,
                route_status=ScaffoldStatus.WARNING,
                is_successful=False
                ), message

        # 3) _append_route_method
        is_successful, message = _apply_step_result(
            updates,
            _append_route_method(action, route_file_path, route_content),
            "Could not add route method"
        )
        if not is_successful:
            return _generate_action_result(
                relative_path=relative_path,
                action=action,
                route_name=route_name,
                route_status=ScaffoldStatus.WARNING,
                is_successful=False
            ), message

    except Exception as exception:
        message = click.style(
            f"💣 Error: Failed to add method to route:\n{exception}", fg="red")
        return _generate_action_result(
                relative_path=relative_path,
                action=action,
                route_name=route_name,
                route_status=ScaffoldStatus.ERROR,
                is_successful=False
            ), message

    updates.extend([
        route_generate_route_visit_example(route_name),
        route_generate_route_url_for_reference_call(relative_path, action, route_name)
    ])

    update_messages = "".join(
        click.style(f"    - {update}\n", fg="green") for update in updates)

    message = (
        click.style("✅ Success: Added Route To Existing Directory \n", fg="green", bold=True) +
        click.style(update_messages, fg="green")
    )
    return _generate_action_result(
        relative_path=relative_path,
        action=action,
        route_name=route_name,
        route_status=ScaffoldStatus.ADDED,
        is_successful=True
    ), message

def route_generate_parameter_reference(parameters: list[str]) -> str:
    """
    Build a `url_for` argument suffix from parameter names.

    Args:
        parameters (list[str]): Parameter names in the order they should appear.

    Returns:
        str: "" when `parameters` is empty; otherwise a string starting with
        ", " followed by "name=name" pairs joined with ", ".

    Examples:
        >>> route_generate_parameter_reference([])
        ''
        >>> route_generate_parameter_reference(["post_id"])
        ', post_id=post_id'
        >>> route_generate_parameter_reference(["post_id", "comment_id"])
        ', post_id=post_id, comment_id=comment_id'
    """
    if not parameters:
        return ""
    return ", " + ", ".join(
        f"{parameter}={parameter}" for parameter in parameters)

def route_generate_parameter_reference_example(parameters: list[str]) -> str:
    if not parameters:
        return ""
    return ", " + ", ".join(
        f"{parameter}={i}" for i, parameter in enumerate(parameters, start=1)
    )

def route_generate_route_and_blueprint_metadata(
        relative_path: str,
        route_directory_path: str) -> tuple[str, str, str, str]:
    route_init_path=os.path.join(route_directory_path, "__init__.py")
    route_file_path=os.path.join(route_directory_path, "routes.py")
    if "/" in relative_path:
        blueprint_name = f"{relative_path.replace('/', '_')}_blueprint"
        blueprint_registration_file_path = os.path.join(
            os.path.dirname(route_directory_path), "__init__.py")
    else:
        blueprint_name = f"{relative_path if relative_path else 'mains'}_blueprint"
        blueprint_registration_file_path = os.path.join("app", "__init__.py")
    return (
        route_init_path,
        route_file_path,
        blueprint_name,
        blueprint_registration_file_path)

def route_generate_route_name(
    relative_path: str,
    action: str,
    is_restful: bool,
    relative_path_segments: list[str],
    relative_path_segment_models: list[str]
) -> str:
    """
    Build a nested Flask route path using model-aware IDs and RESTful rules.

    The action is hyphenated (`_` -> `-`). For each parent segment, the segment
    name is hyphenated and, if it is a known model, an `<int:..._id>` parameter
    is inserted. The last segment is handled differently for RESTful vs
    non-RESTful actions.

    Args:
        relative_path (str): Slash-delimited path without the action (e.g. "posts/comments").
        action (str): Action name such as "index", "show", "custom_action".
        is_restful (bool): True if action is a RESTful CRUD action.
        relative_path_segments (list[str]): `relative_path` split on "/" with empties removed.
        relative_path_segment_models (list[str]): Segments that map to known models.

    Returns:
        str: The nested route path starting with "/".

    Examples:
        >>> route_generate_route_name(
        ...     relative_path="posts/comments",
        ...     action="preview",
        ...     is_restful=False,
        ...     relative_path_segments=["posts", "comments"],
        ...     relative_path_segment_models=["posts", "comments"],
        ... )
        "/posts/<int:post_id>/comments/<int:comment_id>/preview"

        >>> route_generate_route_name(
        ...     relative_path="posts/comments",
        ...     action="show",
        ...     is_restful=True,
        ...     relative_path_segments=["posts", "comments"],
        ...     relative_path_segment_models=["posts", "comments"],
        ... )
        "/posts/<int:post_id>/comments/<int:comment_id>"
    """
    action_part = action.replace("_", "-")

    if relative_path == "":
        return f"/{action_part}"

    route_name_parts: list[str] = []
    for relative_path_segment in relative_path_segments[:-1]:
        route_name_parts.append(relative_path_segment.replace("_", "-"))
        if relative_path_segment in relative_path_segment_models:
            route_name_parts.append(
                f"<int:{singularize(relative_path_segment)}_id>")
    relative_path_last_segment = relative_path_segments[-1]
    # Non-RESTful: keep entered path, add ids for known model segments, then action
    if not is_restful:
        route_name_parts.append(relative_path_last_segment.replace("_", "-"))
        if relative_path_last_segment in relative_path_segment_models:
            route_name_parts.append(
                f"<int:{singularize(relative_path_last_segment)}_id>")
        route_name_parts.append(action_part)
        return "/" + "/".join(route_name_parts)
    # RESTful
    if relative_path_last_segment not in relative_path_segment_models:
        route_name_parts.extend(
            [relative_path_last_segment.replace("_", "-"), action_part])
        return "/" + "/".join(route_name_parts)
    parent_resources =  "/".join(route_name_parts)
    child_resource = relative_path_last_segment.replace("_", "-")
    return generate_restful_route(action, parent_resources, child_resource)

def route_generate_route_name_with_model_prompt(
        dotted_path_with_action: str,
        allow_model_prompt: bool) -> tuple[str, str | None]:
    """
    Generate a route name and optionally prompt to create a missing model.

    This function builds a RouteSpec from the dotted input, derives a prompt plan,
    and (when allowed) asks the user to confirm generating a missing model for a
    RESTful route whose last segment is not a registered model. If the prompt is
    declined or disabled, it returns the originally generated route name.

    Args:
        dotted_path_with_action (str): Normalized dotted input such as:
            - `posts.show`
            - `admin.posts.index`
            - `landing`
        allow_model_prompt (bool): If True, may prompt to generate a missing model.

    Returns:
        tuple[str, str | None]: A tuple containing:
            - The chosen route name (accepted or declined prompt route).
            - The model name to generate if the prompt was accepted; otherwise None.

    Examples:
        >>> route_name, model_name = route_generate_route_name_with_model_prompt("posts.show", False)
        >>> model_name is None
        True

    Note:
        Prompts are only considered for RESTful actions where the last path segment
        is not a registered model. Non-RESTful actions do not trigger prompts.
    """

    route_spec = _generate_route_spec(dotted_path_with_action)
    prompt_plan = _generate_prompt_plan(route_spec)

    if not allow_model_prompt \
            or not prompt_plan.missing_model\
            or not prompt_plan.route_structure:
        return route_spec.generated_route_name, None


    segment = prompt_plan.missing_model.segment
    model_name = prompt_plan.missing_model.model_name

    accepted_route = prompt_plan.route_structure.accepted_route
    declined_route = prompt_plan.route_structure.declined_route


    has_accepted = click.confirm(
        f"No registered model found for {click.style(segment, bold=True)}\n "
        f"   - Accept: {click.style(accepted_route, bold=True)}\n"
        f"    - Decline: {click.style(declined_route, bold=True)}\n"
        f"Generate the model {click.style(model_name, bold=True)}?\n",
        default=True
    )
    if not has_accepted:
        return prompt_plan.route_structure.declined_route, None
    return prompt_plan.route_structure.accepted_route, model_name

def route_generate_route_url_for_reference_call(relative_path: str, action: str, route_name: str) -> str:
    _, parameters = route_parse_route_name_for_params_and_types(route_name)
    parameter_reference = route_generate_parameter_reference_example(parameters)
    return (
        f"Reference this route with url_for(" +
        f"'{relative_path.replace('/', '.') if relative_path else 'mains'}"
        f".{action}'{parameter_reference})"
    )

def route_generate_route_visit_example(route_name: str) -> str:
    _, parameters = route_parse_route_name_for_params_and_types(route_name)
    relative_url = route_name
    for i, parameter in enumerate(parameters, start=1):
        relative_url = \
            re.sub(rf"<\w+:{parameter}>", str(i), relative_url, count=1)
    return f"Visit the new route at {relative_url}"

def route_http_method_for_action(action: str) -> str:
    """
    Return the HTTP method for a given route action.

    Actions that modify data ("store", "update", "destroy", "delete") map to "POST".
    All other actions map to "GET".

    Args:
        action (str): The action name (e.g., "index", "show", "store", "delete").

    Returns:
        str: "POST" for modifying actions; otherwise "GET".

    Examples:
        >>> route_http_method_for_action("index")
        'GET'
        >>> route_http_method_for_action("store")
        'POST'
    """
    return "POST" if action in ["store", "update", "destroy", "delete"] else "GET"

def route_parse_route_name_for_params_and_types(route_name: str) ->tuple[list[str], list[str]]:
    """
    Parse a Flask-style route and extract parameter names and typed parameter
    declarations.

    Only typed params like "<int:post_id>" are captured; untyped params like
    "<post_id>" are ignored.

    Args:
        route_name (str): Route string containing typed params, e.g.
            "/posts/<int:post_id>" or "/posts/<str:post_slug>".

    Returns:
        A tuple of (parameters_with_types, parameters) where:
        - parameters_with_types is a list like ["post_id: int"] or ["post_slug: str"].
        - parameters is a list like ["post_id"] or ["post_slug"].


    Examples:
        >>> route_parse_route_name_for_params_and_types(
        ...     "/recipes/<int:recipe_id>/comments/<int:comment_id>/images/<int:image_id>"
        ... )
        (['recipe_id: int', 'comment_id: int', 'image_id: int'],
         ['recipe_id', 'comment_id', 'image_id'])
    """
    matches = re.finditer(r"<(\w+):(\w+)>", route_name)
    parameters_with_types = []
    parameters = []

    for match in matches:
        type_of_param, param = match.groups()
        parameters_with_types.append(f"{param}: {type_of_param}")
        parameters.append(param)

    return parameters_with_types, parameters

def route_write_directory_and_register_blueprint(
    relative_path: str,
    action: str,
    route_directory_path: str,
    route_name: str,
    controller_name: str | None) -> tuple[RouteResult, ActionResult, str]:
    """
    Create a new Flask route package, write its initial route file, then register its blueprint.

    Workflow:
    1. Create any missing parent route directories for nested paths.
    2. Create the target route directory and write its `__init__.py`.
    3. Write `routes.py` with the initial action handler.
    4. Register the blueprint:
       - nested path: register in the parent route package
       - top-level path: register in `app/__init__.py`

    Args:
        relative_path (str): Route path without the action, slash-delimited
            (examples: "", "posts", "posts/comments").
        action (str): Route function/action name
            (examples: "index", "show", "custom_action").
        route_directory_path (str): Filesystem path for the new route package
            (example: "app/routes/posts/comments").
        route_name (str): Flask URL rule for the action
            (example: "/posts/<int:post_id>/comments").
        controller_name (str | None): Controller class used by the generated route;
            defaults to "MainController" when None.

    Returns:
        tuple[RouteResult, ActionResult, str]:
            - RouteResult: route directory / blueprint result
            - ActionResult: action-level route reference result
            - str: Styled summary of updates on success, or a warning/error reason on failure.

    Examples:
        >>> route_write_directory_and_register_blueprint(
        ...     relative_path="users",
        ...     action="index",
        ...     route_directory_path="app/routes/users",
        ...     route_name="/users",
        ...     controller_name="UserController",
        ... )
        >>> route_write_directory_and_register_blueprint(
        ...     relative_path="recipes/comments",
        ...     action="index",
        ...     route_directory_path="app/routes/recipes/comments",
        ...     route_name="/recipes/<int:recipe_id>/comments",
        ...     controller_name="RecipeCommentController",
        ... )
    """
    # The route folder is not there so we need to create everything:
    route_result = RouteResult(
        directory_status=ScaffoldStatus.WARNING,
        is_successful=False,
    )
    warning_action_result = _generate_action_result(
        relative_path=relative_path,
        action=action,
        route_name=route_name,
        route_status=ScaffoldStatus.WARNING,
        is_successful=False,
    )
    try:
        updates: list[str] = []

        #   1) Create routes folder and any missing parent directories for nested paths
        if "/" in relative_path:
            is_successful, updates = _write_parent_routes(relative_path)

            if not is_successful:
                messages = "".join(
                    click.style(f"    - {update}\n", fg="yellow")
                    for update in updates
                )
                return (
                    route_result,
                    warning_action_result,
                    click.style("⚠️  Warning: Could not prepare parent routes\n", fg="yellow", bold=True) + messages
                )

        os.makedirs(route_directory_path)

        #   2) Create the routes __init__.py file
        is_successful, reason, route_init_path = \
            _write_init_file(route_directory_path)
        if reason:
            updates.append(reason)
        route_result.route_init_path = route_init_path

        if not is_successful:
            message = (
                click.style(f"⚠️  Warning: Could not create route init file\n", fg="yellow", bold=True) +
                click.style(f"    - {reason}\n", fg="yellow")
            )
            return route_result, warning_action_result, message

        #   3) Create the routes routes.py file
        is_successful, reason, route_file_path = _write_routes_file(
                route_directory_path=route_directory_path,
                action=action,
                route_name=route_name,
                controller_name=controller_name)
        if reason:
            updates.append(reason)
        route_result.route_file_path = route_file_path
        if not is_successful:
            message = (
                click.style(f"⚠️  Warning: Could not create route file\n", fg="yellow", bold=True) +
                click.style(f"    - {reason}\n", fg="yellow")
            )
            return route_result, warning_action_result, message

        #   4) Register the blueprint in either the parent (nested path) or at the app level
        is_successful, reason, blueprint_name, blueprint_registration_file_path = _register_route(
            relative_path=relative_path,
            route_directory_path=route_directory_path,
        )
        if reason:
            updates.append(reason)
        route_result.blueprint_name = blueprint_name
        route_result.blueprint_registration_file_path = blueprint_registration_file_path

        if not is_successful:
            message = (
                click.style("⚠️  Warning: Could not register blueprint\n", fg="yellow", bold=True) +
                click.style(f"    - {reason}\n", fg="yellow")
            )
            return route_result, warning_action_result, message

    except Exception as exception:
        message = click.style(
            f"💣 Error: Failed to create route:\n{exception}", fg="red")
        route_result.directory_status = ScaffoldStatus.ERROR
        route_result.is_successful = False                                     # Not need but more readable
        error_action_result = _generate_action_result(
            relative_path=relative_path,
            action=action,
            route_name=route_name,
            route_status=ScaffoldStatus.ERROR,
            is_successful=False,
        )
        return route_result, error_action_result, message

    updates.extend([
        route_generate_route_visit_example(route_name),
        route_generate_route_url_for_reference_call(relative_path, action, route_name)
    ])

    update_messages = "".join(
        click.style(f"    - {update}\n", fg="green") for update in updates)
    message = (
        click.style("✅ Success: Created New Route Directory\n", fg="green", bold=True) +
        click.style(update_messages, fg="green")
    )
    route_result.directory_status = ScaffoldStatus.ADDED
    route_result.is_successful = True
    success_action_result = _generate_action_result(
        relative_path=relative_path,
        action=action,
        route_name=route_name,
        route_status=ScaffoldStatus.ADDED,
        is_successful=True,
    )
    return route_result, success_action_result, message

def _append_route_method(action: str, route_file_path: str, route_content: list[str]) -> tuple[bool, str]:
    try:
        file_append_file(route_file_path, route_content)
    except Exception as exception:
        return False, f"Failed to append {action} to {route_file_path}: {exception}"
    return True, f"Added route function {action} to {route_file_path}"

def _apply_step_result(
    updates: list[str],
    result: tuple[bool, str],
    failure_title: str,
) -> tuple[bool, str | None]:
    is_successful, reason = result

    if reason:
        updates.append(reason)

    if is_successful:
        return True, None

    message = (
        click.style(f"⚠️  Warning: {failure_title}\n", fg="yellow", bold=True) +
        click.style(f"    - {reason}\n", fg="yellow")
    )
    return False, message

def _generate_action_result(
        relative_path: str,
        action: str,
        route_name: str,
        route_status: ScaffoldStatus,
        is_successful: bool
) -> ActionResult:
    return ActionResult(
        action=action,
        http_method=route_http_method_for_action(action),
        route_name=route_name,
        url_for_example=route_generate_route_url_for_reference_call(
            relative_path, action, route_name),
        is_successful=is_successful,
        route_status=route_status
    )

def _generate_minimal_route_routes(route_directory_path: str) -> list[str]:
    return [f"from {route_directory_path.replace('/', '.')} import bp"]

def _generate_prompt_plan(route_spec: RouteSpec) -> PromptPlan:
    """
    Create a prompt plan for RESTful routes when a missing model segment is detected.

    If the route is RESTful and the last segment is not a recognized model, this
    builds prompts to suggest the missing model and an adjusted route structure.
    The route structure includes two optional names: one for the current route
    (without the missing model added) and one for the adjusted route (with the
    missing model added).

    Args:
        route_spec (RouteSpec): Parsed route metadata used to determine whether
            prompts are required and to generate suggested route names.

    Returns:
        PromptPlan: A plan containing optional `missing_model` and
        `route_structure` prompts, or an empty plan when no prompt is needed.
    """

    if not route_spec.relative_path_segments:
        return PromptPlan()

    relative_path_last_segment = route_spec.relative_path_segments[-1]
    is_last_segment_a_model = \
        relative_path_last_segment in route_spec.relative_path_segment_models

    # RESTful: Only prompt if last segment is not a model
    if (not route_spec.is_restful) or is_last_segment_a_model:
        return PromptPlan()

    model_name = singularize(relative_path_last_segment).title().replace("_", "")
    missing_model_prompt = MissingModelPrompt(
        segment=relative_path_last_segment,
        model_name=model_name
    )
    accepted_route = route_generate_route_name(
        relative_path=route_spec.relative_path,
        action=route_spec.action,
        is_restful=route_spec.is_restful,
        relative_path_segments=list(route_spec.relative_path_segments),
        relative_path_segment_models=list(route_spec.relative_path_segment_models + (relative_path_last_segment, ))
    )
    route_structure_prompt = RouteStructurePrompt(
        accepted_route=accepted_route,
        declined_route=route_spec.generated_route_name
    )
    return PromptPlan(
        missing_model=missing_model_prompt,
        route_structure=route_structure_prompt
    )

def _generate_route_init(route_directory_path: str) -> list[str]:
    blueprint_name = route_directory_path.split("/")[-1]
    return [
            "from flask import Blueprint",
            "",
            f"bp = Blueprint('{blueprint_name}', __name__)",
            "",
            f"from {route_directory_path.replace('/', '.')} import routes"
        ]

def _generate_route_method(
        action: str,
        route_name: str,
        controller_name: str | None) -> list[str]:
    controller_name = controller_name if controller_name else 'MainController'
    method = route_http_method_for_action(action)
    parameters_with_types, parameters = \
        route_parse_route_name_for_params_and_types(route_name)
    return  [
        "",
        f"@bp.route('{route_name}', methods=['{method}'])",
        f"def {action}({', '.join(parameters_with_types)}):",
        f"    return {controller_name}.{action}({', '.join(parameters)})"
    ]

def _generate_route_result(
        relative_path: str,
        route_directory_path: str,
        directory_status: ScaffoldStatus,
        is_successful: bool
) -> RouteResult:
    route_init_path, route_file_path, blueprint_name, blueprint_registration_file_path = \
        route_generate_route_and_blueprint_metadata(
            relative_path, route_directory_path)
    return RouteResult(
        directory_status=directory_status,
        is_successful=is_successful,
        route_init_path=route_init_path,
        route_file_path=route_file_path,
        blueprint_name=blueprint_name,
        blueprint_registration_file_path=blueprint_registration_file_path
    )

def _generate_route_spec(dotted_path_with_action: str) -> RouteSpec:
    """
    Analyze a dotted path with action to build a RouteSpec which includes a generated route name.

    This function does not prompt or choose alternate structures. It returns a
    RouteSpec snapshot used by downstream logic (for example, prompt planning).

    Workflow:
    1. Split `dotted_path_with_action` into `relative_path` and `action`.
    2. Detect whether `action` is RESTful.
    3. Load registered models from `app/models/__init__.py` via
       `model_get_registered_models()`.
    4. Convert registered model names to snake_case for per-segment matching.
    5. Mark which `relative_path` segments map to known models.
    6. Generate the route name with `route_generate_route_name()`.

    Args:
        dotted_path_with_action: Normalized dotted input in the form:
            - `resource.action` (example: `posts.show`)
            - `namespace.resource.action` (example: `admin.posts.index`)
            - `resource` (example: `landing`)

    Returns:
        RouteSpec: Immutable route analysis data containing:
            - original dotted input
            - `relative_path` and `action`
            - RESTful flag
            - split path segments
            - segments recognized as models
            - registered model names (PascalCase) and snake_case variants
            - `generated_route_name`

    Examples:
        >>> spec = _generate_route_spec("posts.show")
        >>> spec.relative_path
        'posts'
        >>> spec.action
        'show'
        >>> spec.is_restful
        True
        >>> spec.generated_route_name  # assuming "Post" is a registered model
        '/posts/<int:post_id>'

        >>> spec = _generate_route_spec("landing")
        >>> spec.relative_path
        ''
        >>> spec.action
        'landing'
        >>> spec.action
        'landing'
        >>> spec.generated_route_name
        '/landing'

    Note:
        Model matching is segment-by-segment using singularized segment names
        against registered snake_case model names.
    """
    relative_path, action = \
        split_dotted_path_with_action_into_relative_path_and_action(
            dotted_path_with_action)


    relative_path_segments = filter_falsy(relative_path.split("/"))
    is_restful = action in ["index", "create", "store", "show", "edit", "update", "destroy", "delete"]

    registered_models = model_get_registered_models()
    registered_snake_models = model_model_names_to_snake_case_names(
        registered_models)
    relative_path_segment_models = [
        relative_path_segment for relative_path_segment in relative_path_segments
        if singularize(relative_path_segment) in registered_snake_models]

    generated_route_name = route_generate_route_name(
        relative_path=relative_path,
        action=action,
        is_restful=is_restful,
        relative_path_segments=relative_path_segments,
        relative_path_segment_models=relative_path_segment_models
    )

    return RouteSpec(
        dotted_path_with_action=dotted_path_with_action,
        relative_path=relative_path,
        action=action,
        is_restful=is_restful,
        relative_path_segments=tuple(relative_path_segments),
        relative_path_segment_models=tuple(relative_path_segment_models),
        registered_models=tuple(registered_models),
        registered_snake_models=tuple(registered_snake_models),
        generated_route_name=generated_route_name
    )

def _register_blueprint_in_parent(
        relative_path: str,
        route_directory_path: str) -> tuple[bool, str, str | None, str | None]:
    _, _, blueprint_name, parent_init_path = route_generate_route_and_blueprint_metadata(
        relative_path, route_directory_path)
    try:
        with open(parent_init_path, "r", encoding="utf-8") as f:
            parent_source = f.read()
    except FileNotFoundError:
        return False, f"file __init__.py missing at {parent_init_path}", None, None

    import_line = f"from {route_directory_path.replace('/', '.')} import bp as {blueprint_name}"
    register_line = f"bp.register_blueprint({blueprint_name})"

    if import_line in parent_source and register_line in parent_source:
        return True, f"{blueprint_name} already registered", blueprint_name, parent_init_path
    new_blueprint_content = [
        "",
        import_line,
        register_line
    ]
    file_append_file(parent_init_path, new_blueprint_content)
    return True, f"Registered the new route as {blueprint_name} in {parent_init_path}", blueprint_name, parent_init_path

def _register_top_level_blueprint_in_app(
        relative_path: str,
        route_directory_path: str) -> tuple[bool, str, str | None, str | None]:
    _, _, blueprint_name, app_init_path = \
        route_generate_route_and_blueprint_metadata(
            relative_path, route_directory_path)

    try:
        with open(app_init_path, "r", encoding="utf-8") as file:
            source = file.read()
    except FileNotFoundError:
        return False, f"Failed to locate file `{app_init_path}`", None, None

    import_line = f"from {route_directory_path.replace('/', '.')} import bp as {blueprint_name}"
    register_line = f"app.register_blueprint({blueprint_name})"

    if import_line in source and register_line in source:
        return True, f"Route blueprint already registered in {app_init_path}", blueprint_name, app_init_path

    match = re.search(r"^\s*return app\b", source, flags=re.MULTILINE)
    if match is None:
        return False, f"Failed to locate `return app` in {app_init_path}", None, None

    insert_index = match.start()
    new_blueprint = (
        "\n"
        f"    {import_line}\n"
        f"    {register_line}\n"
    )
    new_content = source[:insert_index] + new_blueprint + source[insert_index:]

    with open(app_init_path, "w") as file:
        file.write(new_content)

    return True, f"Registered the new route directory as {blueprint_name} at {app_init_path}", blueprint_name, app_init_path

def _register_route(
        relative_path: str,
        route_directory_path: str) -> tuple[bool, str, str | None, str | None]:
    is_nested_blueprint = "/" in relative_path
    if is_nested_blueprint:
        return _register_blueprint_in_parent(relative_path, route_directory_path)
    return _register_top_level_blueprint_in_app(relative_path, route_directory_path)

def _validate_route_method_can_be_added(action: str, route_file_path: str, ) -> tuple[bool, str]:
    try:
        with open(route_file_path, "r", encoding="utf-8") as file:
            existing_file_content = file.read()
    except FileNotFoundError:
        return False, f"Could not find file at {route_file_path}"

    func_pattern = rf"^\s*def\s+{re.escape(action)}\s*\("
    if re.search(func_pattern, existing_file_content, re.MULTILINE):
        return False, f"Route function {action} already exists in {route_file_path}"

    return True, ""

def _write_init_file(route_directory_path: str) -> tuple[bool, str, str | None]:
    route_init_path = os.path.join(route_directory_path, "__init__.py")
    try:
        init_content = _generate_route_init(route_directory_path)
        file_write_file(route_init_path, init_content)
    except Exception as exception:
        return False, f"Failed to create __init__.py at {route_init_path}: {exception}", None
    return True, f"Created __init__.py at {route_init_path}", route_init_path

def _write_parent_route_directory(route_directory_path: str) -> list[str]:
    update_messages: list[str] = []
    if os.path.isdir(route_directory_path):
        return update_messages
    os.makedirs(route_directory_path)
    update_messages.append(
        f"Created routes directory at {route_directory_path}")
    route_init_path = os.path.join(route_directory_path, "__init__.py")
    file_write_file(
        route_init_path, _generate_route_init(route_directory_path))
    update_messages.append(
        f"Created __init__.py in {route_directory_path}")
    route_routes_path = os.path.join(route_directory_path, "routes.py")
    file_write_file(
        route_routes_path,
        _generate_minimal_route_routes(route_directory_path))
    update_messages.append(
        f"Created routes.py with blueprint import only in {route_directory_path}")
    return update_messages

def _write_parent_routes(relative_path: str) -> tuple[bool, list[str]]:
    update_messages: list[str] = []
    all_successful = True

    relative_path_segments = filter_falsy(relative_path.split("/"))             # ['recipes', 'comments', 'images']
    if len(relative_path_segments) <= 1:
        return True, update_messages

    app_base_route = os.path.join("app", "routes")                              # app/routes
    parent_segments = relative_path_segments[:-1]
    for index in range(len(parent_segments)):                                   # ['recipes', 'comments']
        parent_relative_path = "/".join(parent_segments[:index + 1])            # recipes or recipes/comments
        parent_route_directory_path = \
            os.path.join(app_base_route, parent_relative_path)                  # app/routes/recipes or app/routes/recipes/comments
        if not os.path.isdir(parent_route_directory_path):
            update_messages.extend(
                _write_parent_route_directory(parent_route_directory_path))

            if index == 0:
                is_successful, message, _, _ = \
                    _register_top_level_blueprint_in_app(
                        parent_relative_path,
                        parent_route_directory_path)
            else:
                is_successful, message, _, _ = \
                    _register_blueprint_in_parent(
                        parent_relative_path,
                        parent_route_directory_path)

            all_successful = all_successful and is_successful
            update_messages.append(message)

    return all_successful, update_messages

def _write_routes_file(
        route_directory_path: str,
        action: str,
        route_name: str,
        controller_name: str | None) -> tuple[bool, str, str | None]:
    route_file_path = os.path.join(route_directory_path, "routes.py")
    using_controller_name = controller_name if controller_name else 'MainController'
    method = route_http_method_for_action(action)
    parameters_with_types, parameters = route_parse_route_name_for_params_and_types(route_name)
    route_content = [
        f"from app.controllers import {using_controller_name}",
        f"from {route_directory_path.replace('/', '.')} import bp",
        "",
        f"@bp.route('{route_name}', methods=['{method}'])",
        f"def {action}({', '.join(parameters_with_types)}):",
        f"    return {using_controller_name}.{action}({', '.join(parameters)})"
    ]
    try:
        file_write_file(route_file_path, route_content)
    except Exception as exception:
        return False, f"Failed to create routes.py at {route_file_path}: {exception}", None
    return True, f"Created routes.py at {route_file_path}", route_file_path


