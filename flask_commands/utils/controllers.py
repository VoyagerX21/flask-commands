import os
import re
import click

from flask_commands.utils.data_types import ActionResult, ControllerResult, RouteResult, ScaffoldStatus
from flask_commands.utils.models import model_generate_hierarchy_from_controller_name
from flask_commands.utils.scaffold import filter_falsy

from .files import (
    file_append_file,
    file_write_file,
    file_insert_flask_import_name_into_lines,
    file_insert_import_into_lines )
from .naming import camel_to_snake, pluralize, singularize
from .routes import(
    route_parse_route_name_for_params_and_types,
    route_http_method_for_action,
    route_generate_parameter_reference
)

def controller_add_method(
        relative_path: str,
        action: str,
        controller_name: str,
        controller_file_path: str,
        route_name: str | None = None,
        view_directory: str | None = None) -> tuple[ControllerResult, str]:
    """
    Add a static method to an existing controller class.

    This function reads the target controller file, verifies that the requested
    method does not already exist, ensures the required Flask imports are
    present, locates the controller class, and inserts a new `@staticmethod`
    action method.

    Method body generation:
    - GET actions return `render_template(...)`
    - POST actions return `redirect(url_for(...))` to the `.index` route for
      the current relative path

    Template resolution:
    - `view_directory` overrides the template namespace when provided
    - otherwise `relative_path` is used
    - In normal usage, `view_directory` is usually the same as
      `relative_path`, but inferred root wiring may pass `'mains'` so root view
      templates render from the default namespace.

    Route parameter handling:
    - when `route_name` is provided, typed route parameters are parsed and
      included in the generated method signature. If the method already exists
      or the controller class cannot be found, no file changes are made.

    Args:
        relative_path (str): Slash-delimited path used for route references and
            as the default template directory.
        action (str): Method name to add to the controller.
        controller_name (str): Target controller class name.
        controller_file_path (str): Filesystem path to the controller file.
        route_name (str | None): Optional route rule used to derive typed
            method parameters.
        view_directory (str | None): Optional template directory override for
            generated GET methods. This is typically `relative_path`, but may
            be `'mains'` for inferred root view wiring.

    Returns:
        tuple[ControllerResult, str]:
            - `ControllerResult`: structured controller result describing status
              and any methods added
            - `str`: styled success, warning, or error message

    Examples:
        >>> result, message = controller_add_method(
        ...     relative_path="posts",
        ...     action="index",
        ...     controller_name="PostController",
        ...     controller_file_path="app/controllers/post_controller.py",
        ...     route_name="/posts",
        ... )
        >>> result.methods_added
        ['index']

    Notes:
    - If the method already exists, no file changes are made and the result
      status is `EXISTS`.
    - If the controller class cannot be found in the file, no changes are made
      and the result status is `WARNING`.
    """
    try:
        # Read existing controller and check for method
        with open(controller_file_path, "r", encoding="utf-8") as file:
            source = file.read()

        # If method already exists, do nothing and warn user
        method_pattern = rf"def\s+{re.escape(action)}\s*\([^)]*\)\s*(?:->\s*[^:]+)?\s*:"
        if re.search(method_pattern, source):
            message = (
                click.style("⚠️  Warning: Method Already Exists\n", fg="yellow", bold=True) +
                click.style(f"    - Controller {click.style(controller_name, bold=True)}", fg="yellow") +  click.style(f" already has a method named {click.style(action, bold=True)}.\n", fg="yellow") +
                click.style("    - No changes were made to controller's method\n", fg="yellow")
            )
            return _generate_controller_result(
                controller_name,
                controller_file_path,
                status=ScaffoldStatus.EXISTS,
                methods_existing=[action]), message

        # Try to find class definition to insert method into
        class_pattern = rf"^class\s+{re.escape(controller_name)}\b.*:\s*$"
        lines = source.splitlines()

        is_redirect = route_http_method_for_action(action) == "POST"

        if is_redirect:
            import_redirect_pattern = r"from\s+flask\s+import\s+.*\bredirect\b"
            import_url_for_pattern = r"from\s+flask\s+import\s+.*\burl_for\b"
            import_response_return_value_pattern = (
                r"from\s+flask\.typing\s+import\s+.*\bResponseReturnValue\b"
            )
            if not re.search(import_redirect_pattern, source):
                lines = file_insert_flask_import_name_into_lines(
                    lines, "redirect")
            if not re.search(import_url_for_pattern, source):
                lines = file_insert_flask_import_name_into_lines(
                    lines, "url_for")
            if not re.search(import_response_return_value_pattern, source):
                lines = file_insert_import_into_lines(
                    lines, "from flask.typing import ResponseReturnValue")

        else:
            import_render_template_pattern = r"from\s+flask\s+import\s+.*\brender_template\b"
            if not re.search(import_render_template_pattern, source):
                lines = file_insert_flask_import_name_into_lines(
                    lines, "render_template")


        insert_index = None
        # 1. Find the class
        for start_index, line in enumerate(lines):
            if re.match(class_pattern, line):
                # 2. find end of class (next top-level def/class or EOF)
                end_index = start_index + 1
                while end_index < len(lines):
                    # skip blank lines inside the class
                    if lines[end_index].strip() == "":
                        end_index += 1
                        continue
                    # top-level (no indent)
                    if len(lines[end_index]) - len(lines[end_index].lstrip()) == 0 and \
                            re.match(r"^(class|def)\b", lines[end_index]):
                        break
                    end_index += 1
                insert_index = end_index
                break
        # If the controller class isn’t found do nothing and warn user
        if insert_index is None:
            message = (
                click.style("⚠️  Warning: Controller Class Not Found\n", fg="yellow", bold=True) +
                click.style(f"    - Could not locate class '{controller_name}' inside {controller_file_path}\n", fg="yellow") +
                click.style("    - No method was added.", fg="cyan")
            )
            return _generate_controller_result(
                controller_name,
                controller_file_path,
                status=ScaffoldStatus.WARNING), message

        # 3. Build the new static method block
        method_parameters = ""
        parameters = []
        if route_name:
            parameters_with_types, parameters = \
                route_parse_route_name_for_params_and_types(route_name)
            method_parameters = ", ".join(parameters_with_types)
        if is_redirect:
            if action != "store":
                parameters = parameters[:-1]
            parameter_reference = route_generate_parameter_reference(parameters)
            redirect_route_reference = relative_path.replace("/", ".")
            return_line = " "*8 +\
                f"return redirect(url_for('{redirect_route_reference}" + \
                f".index'{parameter_reference}))"
        else:
            template_directory = \
                relative_path if view_directory is None else view_directory
            relative_view_file_path = \
                os.path.join(template_directory, f"{action}.html")
            return_line = \
                f"        return render_template('{relative_view_file_path}')"

        return_type = "ResponseReturnValue" if is_redirect else "str"

        method_block = [
            "",
            "    @staticmethod",
            f"    def {action}({method_parameters}) -> {return_type}:",
            return_line
        ]

        # check for just the class with only a pass and remove the pass
        class_body = lines[start_index + 1:insert_index]
        non_blank = [line for line in class_body if line.strip() != ""]
        if non_blank and all(line.strip() == "pass" for line in non_blank):
            lines = lines[:start_index + 1] + lines[insert_index:]
            insert_index = start_index + 1

        # 4. Insert new static method block
        for line in reversed(method_block):
            lines.insert(insert_index, line)

        new_source = "\n".join(lines)
        with open(controller_file_path, "w", encoding="utf-8") as f:
            f.write(new_source)
    except Exception as exception:
        message = click.style(f"💣 Error: Failed to add Controller Method\n {exception}", fg="red")
        return _generate_controller_result(
            controller_name,
            controller_file_path,
            status=ScaffoldStatus.ERROR,
        ), message
    message = (
        click.style("✅ Success: Method Added To Controller\n", fg="green", bold=True) +
        click.style(f"    - Added method {action} to controller {controller_name}\n", fg="green") +
        click.style(f"    - Controller located at {controller_file_path}\n", fg="green")
    )
    return _generate_controller_result(
        controller_name,
        controller_file_path,
        status=ScaffoldStatus.ADDED,
        methods_added=[action]
    ), message

def controller_generate_controller_name_from_relative_path(relative_path: str) -> str:
    """
    Build a controller class name from a slash-delimited relative path.

    Each path segment is singularized, converted to TitleCase, and stripped of
    underscores, then all segments are concatenated with a trailing
    ``"Controller"``.

    Args:
        relative_path (str): Slash-delimited path (for example,
            ``"posts/comments"`` or ``"admin/users/user_profiles"``).

    Returns:
        str: Generated controller class name.

    Examples:
        >>> controller_generate_controller_name_from_relative_path("posts/comments/images")
        'PostCommentImageController'
        >>> controller_generate_controller_name_from_relative_path("user_profiles")
        'UserProfileController'
        >>> controller_generate_controller_name_from_relative_path("admin/users/user_profiles")
        'AdminUserUserProfileController'
        >>> controller_generate_controller_name_from_relative_path("")
        'Controller'
    """
    return ''.join([singularize(part).title().replace('_', '')
                    for part in relative_path.split('/')]) + "Controller"

def controller_generate_relative_path_from_controller_name(controller_name: str) -> str:
    """
    Generate a slash-delimited relative path from a controller class name.

    This function derives hierarchy segments using
    ``model_generate_hierarchy_from_controller_name``. If no registered model
    anchor is found, all parsed segments are treated as resource segments and
    pluralized. If a registered model anchor is found, leading unmatched
    segments are treated as namespaces, kept singular, and combined into one
    hyphenated URL segment. Model/resource segments are converted to snake_case,
    pluralized, and joined with ``/``.

    Args:
        controller_name (str): Controller class name (for example,
            ``"PostCommentController"`` or ``"AdminUserProfileController"``).

    Returns:
        str: Relative path (for example, ``"posts/comments"``). Returns ``""``
        when no segments can be derived.

    Examples:
        # No registered models
        >>> controller_generate_relative_path_from_controller_name("CommentController")
        'comments'

        # Registered models: Post
        >>> controller_generate_relative_path_from_controller_name("PostController")
        'posts'

         # Registered models: Post
        >>> controller_generate_relative_path_from_controller_name("PostCommentController")
        'posts/comments'

        # Registered models: Post, Comment
        >>> controller_generate_relative_path_from_controller_name("PostCommentController")
        'posts/comments'

        # Registered models: User, UserProfile   (multi-word model)
        >>> controller_generate_relative_path_from_controller_name("AdminUserProfileAvatarController")
        'admin/user_profiles/avatars'

        # Registered models: Order
        >>> controller_generate_relative_path_from_controller_name("FrontDeskOrderController")
        'front-desk/orders'

    Note:
        Output depends on registered models in ``app/models/__init__.py``
        because hierarchy detection is model-aware.
    """
    
    namespaces, parent_models, child_model_name = \
        model_generate_hierarchy_from_controller_name(controller_name)
    
    if not parent_models and not child_model_name:
        return "/".join(
            pluralize(camel_to_snake(segment))
            for segment in filter_falsy(namespaces)
        )
    namespace_segment = "_".join(
        camel_to_snake(segment) for segment in filter_falsy(namespaces))
    
    resource_segments = [
        pluralize(camel_to_snake(segment)) 
        for segment in filter_falsy(parent_models + [child_model_name])]
    
    return '/'.join(filter_falsy([namespace_segment]) + resource_segments)

def controller_make_file(
        relative_path: str | None,
        action: str | None, # When you generate a controller calls and register it without any methods
        controller_name: str,
        controller_file_path: str,
        route_name: str | None = None,
        view_directory: str | None = None) -> tuple[ControllerResult, str]:
    """
    Create a new controller file and optionally scaffold one initial action method.

    This function writes `app/controllers/<controller>.py` and attempts to
    register the controller in `app/controllers/__init__.py`.

    When `action` is provided, `relative_path` must also be provided (and vice
    versa). With no `action`, the generated class body is `pass`.

    When `action` is provided, the generated controller includes:
    - a static action method
    - the required Flask imports
      - `render_template` for GET actions
      - `redirect, url_for` for POST actions

    - the static method returns `render_template(...)` for GET actions or
      `redirect(url_for(...))` for POST actions

    Validation:
    - `action` requires `relative_path`
    - `relative_path` requires `action`

    Route parameter handling:
    - when `route_name` is provided, typed route parameters are parsed and
      included in the generated method signature

    Args:
        relative_path (str | None): Slash-delimited path used for route
            references and as the default template directory when `action`
            is present.
        action (str | None): Optional action method to scaffold.
        controller_name (str): Controller class name to create.
        controller_file_path (str): Filesystem path for the new controller file.
        route_name (str | None): Optional route rule used to derive typed
            method parameters.
        view_directory (str | None): Optional template directory override for
            generated GET methods.

    Returns:
        tuple[ControllerResult, str]:
            - `ControllerResult`: structured controller result describing status,
              registration path, and any methods added
            - `str`: styled success, warning, or error message

    Examples:
        >>> result, message = controller_make_file(
        ...     relative_path=None,
        ...     action=None,
        ...     controller_name='PostController',
        ...     controller_file_path='app/controllers/post_controller.py',
        ... )
        >>> result.controller_name
        'PostController'

        >>> result, message = controller_make_file(
        ...     relative_path="posts",
        ...     action="index",
        ...     controller_name="PostController",
        ...     controller_file_path="app/controllers/post_controller.py",
        ...     route_name="/posts",
        ... )
        >>> result.methods_added
        ['index']

    Notes:
    - The controller file may be created even when registration in
      `app/controllers/__init__.py` fails, in which case the result status is
      `WARNING`.
    - Existing controller files return status `EXISTS` and are not overwritten.
    """
    if action and relative_path is None:
        message = click.style(
            "💣 Error: relative_path required when action present", fg="red")
        return _generate_controller_result(
            controller_name,
            controller_file_path,
            status=ScaffoldStatus.ERROR), message

    if relative_path and action is None:
        message = click.style(
            "💣 Error: action required when relative_path present", fg="red")
        return _generate_controller_result(
            controller_name,
            controller_file_path,
            status=ScaffoldStatus.ERROR), message

    parameters_with_types_joined = ""
    parameters = []
    if route_name:
        parameters_with_types, parameters = \
            route_parse_route_name_for_params_and_types(route_name)
        parameters_with_types_joined = ", ".join(parameters_with_types)


    is_redirect = route_http_method_for_action(action) == "POST"
    contents = []
    if action:
        if is_redirect:
            contents.extend([
                "from flask import redirect, url_for",
                "from flask.typing import ResponseReturnValue",
                ""])
        else:
            contents.extend(["from flask import render_template", ""])
    contents.append(f"class {controller_name}:")
    if action:
        return_type = "ResponseReturnValue" if is_redirect else "str"
        contents.extend([
            f"    @staticmethod",
            f"    def {action}({parameters_with_types_joined}) -> {return_type}:",
        ])
        if is_redirect:
            parameter_reference = route_generate_parameter_reference(parameters)
            redirect_route_reference = relative_path.replace("/", ".")
            contents.append(
                f"        return redirect(url_for('{redirect_route_reference}"
                f".index'{parameter_reference}))")
        else:
            template_directory = \
                relative_path if view_directory is None else view_directory
            relative_view_file_path = \
                os.path.join(template_directory, f"{action}.html")
            contents.append(f"        return render_template('"
                            f"{relative_view_file_path}')")
    else:
        contents.append("    pass")
    try:
        file_write_file(controller_file_path, contents)
    except FileExistsError:
        message = (
            click.style("⚠️ Warning: Controller Already Exists\n", fg="yellow", bold=True) +
            click.style(f"    - Controller {controller_name} already exists.\n", fg="yellow") +
            click.style(f"    - No changes were made to existing controller\n", fg="yellow")
        )
        return _generate_controller_result(
            controller_name,
            controller_file_path,
            status=ScaffoldStatus.EXISTS
        ), message
    except Exception as exception:
        message = click.style(
            f"💣 Error: Failed to create controller:\n{exception}", fg="red")
        return _generate_controller_result(
            controller_name,
            controller_file_path,
            status=ScaffoldStatus.ERROR
        ), message

    try:
        controller_init_path = os.path.join("app", "controllers", "__init__.py")
        init_contents = [f"from .{camel_to_snake(controller_name)} import {controller_name}"]
        file_append_file(controller_init_path, init_contents)
    except FileNotFoundError:
        message = (
            click.style("⚠️  Warning: Controller __init__.py Missing\n", fg="yellow", bold=True) +
            click.style(f"    - Controller {controller_name} was created, but __init__.py does not exist.\n", fg="yellow") +
            click.style(f"    - You may need to register the controller manually.", fg="yellow")
        )
        return _generate_controller_result(
            controller_name,
            controller_file_path,
            status=ScaffoldStatus.WARNING,
            registration_file_path=controller_init_path,
            methods_added=[action] if action else []
        ), message
    except Exception as exception:
        message = click.style(
            f"💣 Error: Failed to update __init__.py:\n{exception}", fg="red")
        return _generate_controller_result(
            controller_name,
            controller_file_path,
            status=ScaffoldStatus.ERROR,
            registration_file_path=controller_init_path,
            methods_added=[action] if action else []
        ), message

    if action:
        message = (
            click.style(f"✅ Success: Created Controller Class With Method\n", fg="green", bold=True) +
            click.style(f"    - Created a new controller called {controller_name}\n", fg="green") +
            click.style(f"    - Added method {action} to controller\n", fg="green") +
            click.style(f"    - Registered {controller_name} at {controller_init_path}\n", fg="green") +
            click.style(f"    - New controller located at {controller_file_path}\n", fg="green")
        )
    else:
        message = (
            click.style(f"✅ Success: Created Controller Class\n", fg="green", bold=True) +
            click.style(f"    - Created a new controller called {controller_name}\n", fg="green") +
            click.style(f"    - Registered {controller_name} at {controller_init_path}\n", fg="green") +
            click.style(f"    - New controller located at {controller_file_path}\n", fg="green")
        )

    return _generate_controller_result(
        controller_name,
        controller_file_path,
        status=ScaffoldStatus.ADDED,
        registration_file_path=controller_init_path,
        methods_added=[action] if action else []
    ), message

def _generate_controller_result(
        controller_name: str,
        controller_file_path: str,
        status: ScaffoldStatus,
        registration_file_path: str | None = None,
        methods_added: list[str] | None = None,
        methods_existing: list[str] | None = None
) -> ControllerResult:
    """
    Build a normalized `ControllerResult` from controller scaffold metadata.

    This helper centralizes how controller scaffold outcomes are translated into
    structured results so callers do not manually reconstruct:
    - success state
    - registration path
    - methods added

    Args:
        controller_name (str): Controller class name.
        controller_file_path (str): Filesystem path to the controller file.
        status (ScaffoldStatus): Scaffold outcome status.
        registration_file_path (str | None): Registration target path when known.
        methods_added (list[str] | None): Methods added during the operation.

    Returns:
        ControllerResult: Structured controller result.

    Examples:
        >>> result = _generate_controller_result(
        ...     controller_name="PostController",
        ...     controller_file_path="app/controllers/post_controller.py",
        ...     status=ScaffoldStatus.ADDED,
        ...     methods_added=["index"],
        ... )
        >>> result.is_successful
        True
    """
    return ControllerResult(
        controller_name=controller_name,
        controller_file_path=controller_file_path,
        status=status,
        is_successful=status == ScaffoldStatus.ADDED,
        registration_file_path=registration_file_path,
        methods_added=[] if methods_added is None else methods_added,
        methods_existing=[] if methods_existing is None else methods_existing
    )


