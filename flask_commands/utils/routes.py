import re
import os
import click
from dataclasses import dataclass
from enum import StrEnum
from flask_commands.utils.models import (
    model_get_registered_models,
    model_model_names_to_snake_case_names)
from .files import append_file, write_file
from .naming import pluralize, singularize
from .scaffold import (
    generate_restful_route,
    filter_falsy,
    split_dotted_path_with_action_into_relative_path_and_action)

RESTFUL_ACTIONS = {"index", "create", "store", "show", "edit", "update", "destroy", "delete"}
MEMBER_ACTIONS = {"show", "edit", "update", "destroy", "delete"}

@dataclass(frozen=True)
class RouteSpec:
    dotted_path_with_action: str
    relative_path: str
    action: str
    is_restful: bool
    relative_path_segments: tuple[str]
    relative_path_segment_models: tuple[str]
    registered_models: tuple[str]
    registered_snake_models: tuple[str]
    generated_route_name: str

@dataclass(frozen=True)
class MissingModelPrompt:
    segment: str
    model_name: str

@dataclass(frozen=True)
class RouteStructurePrompt:
    accepted_route: str
    declined_route: str

@dataclass(frozen=True)
class PromptPlan:
    missing_model: MissingModelPrompt | None = None
    route_structure: RouteStructurePrompt | None = None

def route_add_method(relative_path: str,  action: str, route_folder_path: str, blueprint_name: str,  route_name: str, controller_name: str | None) -> tuple[bool, str]:
    """
    Add a new route to the routes.py file in the specified route folder.
    Determines the HTTP method based on the action type (POST for store,
    update, destroy, delete; GET for others) and appends a new route
    definition with the corresponding controller method call.

    Args:
        relative_path (str): The relative path to strip from route_name for the decorator.
        action (str): The action name (e.g., 'store', 'update', 'show', 'destroy'). Determines HTTP method.
        route_folder_path (str): The absolute path to the routes folder containing routes.py.
        blueprint_name (str): The top level of the relative_path (e.g., posts or mains)
        route_name (str): this is the url path like /posts/<int:post_id> or /admin/posts/comments
        controller_name (str | None): The name of the controller class. Defaults to 'MainController' if None.

    Returns:
        tuple[bool, str]: A tuple containing:
            - bool: True indicating the route was successfully added.
            - str: A formatted message with success notification and usage instructions.

    Example:
        >>> is_successful, message = route_add_method(
        ...     relative_path='users',
        ...     action='index',
        ...     route_folder_path='app/routes/users',
        ...     blueprint_name='users',
        ...     route_name='/users',
        ...     controller_name='UserController'
        ... )
        >>> is_successful, message = route_add_method(
        ...     relative_path='recipes/comments/images',
        ...     action='show',
        ...     route_folder_path='app/routes/recipes/comments/images',
        ...     blueprint_name='recipes',
        ...     route_name='/recipes/<int:recipe_id>/comments/<int:comment_id>/images/<int:image_id>',
        ...     controller_name='RecipeCommentImageController'
        ... )
        >>> is_successful, message = route_add_method(
        ...     relative_path='',
        ...     action='about',
        ...     route_folder_path='app/routes/mains',
        ...     blueprint_name='mains',
        ...     route_name='/about',
        ...     controller_name=None
        ... )
    """

    # The route folder is already there so we just need to add to routes.py

    try:
        route_file_path = os.path.join(route_folder_path, "routes.py")
        using_controller_name = controller_name if controller_name else 'MainController'
        method = route_http_method_for_action(action)
        parameters_with_types, parameters = \
            route_parse_route_name_for_params_and_types(route_name)
        route_content = [
            "",
            f"@bp.route('{route_name}', methods=['{method}'])",
            f"def {action}({', '.join(parameters_with_types)}):",
            f"    return {using_controller_name}.{action}({', '.join(parameters)})"
        ]
        with open(route_file_path, "r", encoding="utf-8") as file:
            existing_file_content = file.read()

        func_pattern = rf"^\s*def\s+{re.escape(action)}\s*\("
        if re.search(func_pattern, existing_file_content, re.MULTILINE):
            message = (
                click.style(f"⚠️ Warning: Route Function Exists\n", fg="yellow", bold=True) +
                click.style(f"    - Route function {click.style(action, bold=True)}", fg="yellow") +
                    click.style(f" already exists at {click.style(route_folder_path, bold=True)}", fg="yellow") +
                    click.style(f"/routes.py\n", bold=True, fg="yellow") +
                click.style("    - No changes were made existing route function\n", fg="yellow")
            )
            return False, message
        append_file(route_file_path, route_content)
    except FileNotFoundError:
        message = (
            click.style("⚠️ Warning: Route Directory Missing\n", fg="yellow", bold=True) +
            click.style(f"    - Could not find routes.py file in folder {click.style(route_folder_path, bold=True)}\n", fg="yellow") +
            click.style("    - No changes were made\n", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(f"💣 Error: Failed to add method to route:\n{exception}", fg="red")

    parameter_reference = _generate_parameter_reference_example(parameters)

    message = (
        click.style(f"✅ Success: Added Route To Existing Directory \n", fg="green", bold=True) +
        click.style(f"    - Updated routes directory at {click.style(route_folder_path, bold=True)}\n", fg="green") +
        click.style(f"    - Added {click.style(method, bold=True)} ", fg="green") + click.style(f"route with url {click.style(route_name, bold=True)}\n", fg="green") +
        click.style(f"    - Reference route with ", fg="green") + click.style(f"url_for('{relative_path.replace('/', '.')}.{action}'{parameter_reference})\n", fg="green", bold=True)
    )
    return True, message

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
    route_spec = route_generate_route_spec(dotted_path_with_action)
    prompt_plan = route_generate_prompt_plan(route_spec)

    if not allow_model_prompt \
            or not prompt_plan.missing_model\
            or not prompt_plan.route_structure:
        return route_spec.generated_route_name, None


    segment = prompt_plan.missing_model.segment
    model_name = prompt_plan.missing_model.model_name
    has_accepted = click.confirm(
        "No registered model found for "
        f"{click.style(segment, bold=True)}. "
        f"Generate {click.style(model_name, bold=True)}?",
        default=True
    )
    if not has_accepted:
        return prompt_plan.route_structure.declined_route, None
    return prompt_plan.route_structure.accepted_route, model_name

def route_generate_parameter_reference(parameters: list[str]) -> str:
    if not parameters:
        return ""
    return ", " + ", ".join(
        f"{parameter}={parameter}" for parameter in parameters)

def route_generate_prompt_plan(route_spec: RouteSpec) -> PromptPlan:
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

def route_generate_route_folder_path_and_blueprint_name(dotted_path_with_action: str, relative_path: str) -> tuple[str, str]:
    """
    Generate a file path and blueprint name for a Flask route module.

    Args:
        dotted_path_with_action (str): A dotted path notation string that may contain
            a dot separator and a name component (e.g., 'auth.login' or 'dashboard').
        relative_path (str): A relative path string representing the route directory
            structure (e.g., 'auth/login' or 'users/profile').

    Returns:
        tuple[str, str]: A tuple containing:
            - str: The file path for the route module relative to the project root.
            - str: The blueprint name derived from the relative path, with forward slashes
                replaced by underscores.

    Example:
        >>> route_generate_route_folder_path_and_blueprint_name('posts.index', 'posts')
        ('app/routes/posts', 'posts')

        >>> route_generate_route_folder_path_and_blueprint_name('posts.comments.index', 'posts/comments')
        ('app/routes/posts/comments', 'posts')

        >>> route_generate_route_folder_path_and_blueprint_name('dashboard', '')
        ('app/routes/mains', 'mains')

        >>> route_generate_route_folder_path_and_blueprint_name('recipe.comments.images.index', 'recipe/comments/images')
        ('app/routes/recipe/comments/images', 'mains')
    """
    if "." not in dotted_path_with_action:
        return os.path.join("app", "routes", "mains"), 'mains'
    top_level = relative_path.split("/", 1)[0]
    return os.path.join("app", "routes", relative_path), top_level

def route_generate_route_spec(dotted_path_with_action: str) -> RouteSpec:
    """
    Analyze a dotted path and produce a complete route-generation specification.

    This function does not decide prompts or final route selection. It builds a
    `RouteSpec` snapshot used by downstream logic to decide between flat and
    nested routes (and prompt behavior, if needed).

    Workflow:
    1. Split `dotted_path_with_action` into `relative_path` and `action`.
    2. Detect whether `action` is RESTful (`RESTFUL_ACTIONS`).
    3. Load registered models from `app/models/__init__.py` via
       `model_get_registered_models()`.
    4. Convert registered model names to snake_case for per-segment matching.
    5. Mark which `relative_path` segments map to known models.
    6. Build both candidate routes:
       - `flat_route` (single hyphenated path segment)
       - `nested_route` (model-aware path with optional `<int:..._id>` params)

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
            - `flat_route` and `nested_route` candidates

    Examples:
        >>> spec = route_generate_route_spec("posts.show")
        >>> spec.relative_path
        'posts'
        >>> spec.action
        'show'
        >>> spec.is_restful
        True
        >>> spec.flat_route
        '/posts-show'
        >>> spec.nested_route
        '/posts/<int:post_id>'

        >>> spec = route_generate_route_spec("landing")
        >>> spec.relative_path
        ''
        >>> spec.action
        'landing'
        >>> spec.flat_route
        '/landing'
        >>> spec.nested_route
        '/landing'

    Note:
        Model matching is segment-by-segment using singularized segment names
        against registered snake_case model names.
    """
    relative_path, action = \
        split_dotted_path_with_action_into_relative_path_and_action(
            dotted_path_with_action)


    relative_path_segments = filter_falsy(relative_path.split("/"))
    is_restful = action in RESTFUL_ACTIONS

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
        relative_path_segments=relative_path_segments,
        relative_path_segment_models=tuple(relative_path_segment_models),
        registered_models=tuple(registered_models),
        registered_snake_models=registered_snake_models,
        generated_route_name=generated_route_name
    )

def route_http_method_for_action(action: str) -> str:
    return "POST" if action in ["store", "update", "destroy", "delete"] else "GET"

def route_make_directory_and_register_blueprint(relative_path: str, action: str, route_folder_path: str, blueprint_name: str, route_name: str, controller_name: str | None) -> tuple[bool, str]:
    """
    Creates a new Flask route directory structure and registers a blueprint in the Flask app.

    This function automates the setup of a new route module by:
    1. Creating the route folder directory
    2. Creating a __init__.py file in the route directory
    3. Creating a routes.py file with the initial route action
    4. Registering the blueprint in the app's __init__.py

    Args:
        action (str): The action/method name (e.g., 'index', 'store', 'update', 'destroy').
                     Determines HTTP method: POST for store/update/destroy/delete, GET otherwise.
        route_folder_path (str): The file system path where the route folder will be created.
        blueprint_name (str): The name of the Flask blueprint to create (e.g., 'users').
        route_name (str): The full name/path of the route (e.g., 'users.index').
        controller_name (str | None): The name of the controller class to use. Defaults to 'MainController' if None.

    Returns:
        tuple[bool, str]: A tuple containing:
            - bool: True if the operation was successful.
            - str: A formatted success message with styled output describing the created resources,
                   blueprint registration, generated route action, and url_for reference.

    Example:
        >>> is_successful, message = route_make_directory_and_register_blueprint(
        ...     relative_path='users',
        ...     action='index',
        ...     route_folder_path='app/routes/users',
        ...     blueprint_name='users',
        ...     route_name='/users',
        ...     controller_name='UserController'
        ...
        >>> is_successful, message = route_make_directory_and_register_blueprint(
        ...     relative_path='recipes/comments/images',
        ...     action='index',
        ...     route_folder_path='app/routes/recipes/comments/images',
        ...     blueprint_name='recipes',
        ...     route_name='/recipes/<int:recipe_id>/comments/<int:comment_id>/images',
        ...     controller_name='RecipeCommentImageController')
    """
    # The route folder is not there so we need to create everything:
    #   1) create routes folder - check
    try:
        os.makedirs(route_folder_path)
    #   2) Create and possibly update __init__.py files
    #   2a) Create the nested __init__.py file
        route_init_path = os.path.join(route_folder_path, "__init__.py")
        registered_blueprint = route_folder_path.split("/")[-1]
        route_init_content = [
            "from flask import Blueprint",
            "",
            f"bp = Blueprint('{registered_blueprint}', __name__)",
            "",
            f"from {route_folder_path.replace('/', '.')} import routes"
        ]
        write_file(route_init_path, route_init_content)
    #   2b) Check to see if you need to update the top level __init__.py to
    #       include the new blueprint
        top_level_path = os.path.join("app", "routes", blueprint_name)
        top_level_init_path = os.path.join(top_level_path, "__init__.py")
        parent_init_path = os.path.join(os.path.dirname(route_folder_path), "__init__.py")
        is_nested_blueprint = route_init_path != top_level_init_path
        if is_nested_blueprint:
            new_blueprint_content = [
                "",
                f"from {route_folder_path.replace('/', '.')} import bp as {relative_path.replace('/', '_')}_blueprint",
                f"bp.register_blueprint({relative_path.replace('/', '_')}_blueprint)"
            ]
            append_file(parent_init_path, new_blueprint_content)

    #   3) routes.py file - check
        route_file_path = os.path.join(route_folder_path, "routes.py")
        using_controller_name = controller_name if controller_name else 'MainController'
        method = route_http_method_for_action(action)
        parameters_with_types, parameters = route_parse_route_name_for_params_and_types(route_name)
        route_content = [
            f"from app.controllers import {using_controller_name}",
            f"from {route_folder_path.replace('/', '.')} import bp",
            "",
            f"@bp.route('{route_name}', methods=['{method}'])",
            f"def {action}({', '.join(parameters_with_types)}):",
            f"    return {using_controller_name}.{action}({', '.join(parameters)})"
        ]
        write_file(route_file_path, route_content)
    except FileExistsError:
        message = (
            click.style("⚠️  Warning: Route Already Exists\n", fg="yellow", bold=True) +
            click.style(f"    - Route Directory for {click.style(blueprint_name, bold=True)}", fg="yellow") + click.style(" already exists\n", fg="yellow") +
            click.style("    - No changes were made\n", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(f"💣 Error: Failed to create route:\n{exception}", fg="red")

    #  4) update the __init__.py in app directory to include the new blueprint
    # if it is not a nested blueprint
    if not is_nested_blueprint:
        app_init_path = os.path.join("app", "__init__.py")
        with open(app_init_path, "r", encoding="utf-8") as f:
            source = f.read()

        match = re.search(r"^\s*return app\b", source, flags=re.MULTILINE)
        if match is None:
            message = (
                click.style("⚠️  Warning: Could not register blueprint\n", fg="yellow", bold=True) +
                click.style(
                    "    - Failed to locate `return app` in app/__init__.py.\n",
                    fg="yellow"
                ) +
                click.style(
                    f"    - Please register '{blueprint_name}' manually.",
                    fg="yellow"
                )
            )
            return False, message
        insert_index = match.start()
        new_blueprint = [
            "",
            f"    from {route_folder_path.replace('/', '.')} import bp as {blueprint_name}_blueprint",
            f"    app.register_blueprint({blueprint_name}_blueprint)"
        ]
        new_blueprint = "\n".join(new_blueprint)
        new_content = source[:insert_index] + new_blueprint + "\n" + source[insert_index:]
        with open(app_init_path, "w") as f:
            f.write(new_content)

    registered_location = "app/__init__.py"
    if is_nested_blueprint:
        registered_location = parent_init_path
    route_reference = relative_path.replace("/", ".")
    parameter_reference = _generate_parameter_reference_example(parameters)


    message = (
        click.style(f"✅ Success: Created New Route Directory\n", fg="green", bold=True) +
        click.style(f"    - Registered the new route directory as {click.style(registered_blueprint, bold=True)}", fg="green") + click.style(f" at {click.style(registered_location, bold=True)}\n", fg="green") +
        click.style(f"    - Created routes directory at {click.style(route_folder_path, bold=True)}\n", fg="green") +
        click.style(f"    - Initialized {click.style(method, bold=True)} ", fg="green") + click.style(f"route with url {click.style(route_name, bold=True)}\n", fg="green") +
        click.style(f"    - Route function {click.style(action, bold=True)} ", fg="green") + click.style(f"is using controller {click.style(using_controller_name, bold=True)}\n", fg="green") +
        click.style(f"    - Reference route with ", fg="green") + click.style(f"url_for('{route_reference}.{action}'{parameter_reference})\n", fg="green", bold=True)
    )
    return True, message

def route_parse_route_name_for_params_and_types(route_name: str) ->tuple[list[str], list[str]]:
    """
    Parse a Flask-style route and extract parameter names and typed parameter
    declarations.

    Args:
        route_name: Route string containing typed params, e.g. "/posts/<int:post_id>"
        route_name: Route string containing typed params, e.g. "/posts/<str:post_slug>".

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

def _generate_parameter_reference_example(parameters: list[str]) -> str:
    if not parameters:
        return ""
    return ", " + ", ".join(
        f"{parameter}={i}" for i, parameter in enumerate(parameters, start=1)
    )

