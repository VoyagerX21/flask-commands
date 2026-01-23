from calendar import c
import os
import re
import click
from typing import Tuple
from .files import append_file, write_file, insert_import_into_lines
from .naming import camel_to_snake, pluralize, singularize
from .routes import(
    parse_route_name_for_params_and_types,
    route_http_method_for_action,
    route_build_parameter_reference
)


def controller_add_method(
        relative_path: str,
        action: str,
        controller_name: str,
        route_name: str | None = None) -> Tuple[bool, str]:
    try:
        controller_file_path = os.path.join(
            "app", "controllers", f"{camel_to_snake(controller_name)}.py")
        # Read existing controller and check for method
        with open(controller_file_path, "r", encoding="utf-8") as f:
            source = f.read()

        # If method already exists, do nothing and warn user
        method_pattern = rf"def\s+{re.escape(action)}\s*\([^)]*\)\s*(?:->\s*[^:]+)?\s*:"
        if re.search(method_pattern, source):
            message = (
                click.style("⚠️  Warning: Method Already Exists\n", fg="yellow", bold=True) +
                click.style(f"    - Controller {click.style(controller_name, bold=True)}", fg="yellow") +  click.style(f" already has a method named {click.style(action, bold=True)}.\n", fg="yellow") +
                click.style("    - No changes were made to controller's method\n", fg="yellow")
            )
            return False, message

        # Try to find class definition to insert method into
        class_pattern = rf"^class\s+{re.escape(controller_name)}\b.*:\s*$"
        lines = source.splitlines()

        is_redirect = route_http_method_for_action(action) == "POST"

        if is_redirect:
            import_redirect_pattern = r"from\s+flask\s+import\s+.*\bredirect\b"
            import_url_for_pattern = r"from\s+flask\s+import\s+.*\burl_for\b"
            if not re.search(import_redirect_pattern, source) or \
                    not re.search(import_url_for_pattern, source):
                lines =insert_import_into_lines(
                    lines, "from flask import redirect, url_for")

        else:
            import_render_template_pattern = r"from\s+flask\s+import\s+.*\brender_template\b"
            if not re.search(import_render_template_pattern, source):
                lines =insert_import_into_lines(
                    lines, "from flask import render_template")


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
            return False, message

        # 3. Build the new static method block
        method_parameters = ""
        parameters = []
        if route_name:
            parameters_with_types, parameters = \
                parse_route_name_for_params_and_types(route_name)
            method_parameters = ", ".join(parameters_with_types)
        if is_redirect:
            if action != "store":
                parameters = parameters[:-1]
            parameter_reference = route_build_parameter_reference(parameters)
            redirect_route_reference = relative_path.replace("/", ".")
            return_line = " "*8 +\
                f"return redirect(url_for('{redirect_route_reference}" + \
                f".index'{parameter_reference}))"
        else:
            relative_view_file_path = \
                os.path.join(relative_path, f"{action}.html")
            return_line = \
                f"        return render_template('{relative_view_file_path}')"

        method_block = [
            "",
            "    @staticmethod",
            f"    def {action}({method_parameters}) -> str:",
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
        return False, message
    message = (
        click.style("✅ Success: Method Added To Controller\n", fg="green", bold=True) +
        click.style(f"    - Added method {click.style(action, bold=True)}", fg="green") + click.style(f" to controller {click.style(controller_name, bold=True)}\n", fg="green") +
        click.style(f"    - Controller located at {click.style(controller_file_path, bold=True)}\n", fg="green")
    )
    return True, message

def controller_infer_name_from(relative_path: str) -> str:
    return ''.join([singularize(part).title()
                    for part in relative_path.split('/')]) + "Controller"

def extract_relative_path_from(controller_name: str) -> str:
    """Return pluralized path from a controller class name.

    Example:
        PostCommentImageController -> posts/comments/images
    """
    parts = camel_to_snake(controller_name).split('_')[:-1]
    return '/'.join(list(map(lambda part: pluralize(part), parts)))

def controller_make_file(
        relative_path: str | None,
        action: str | None, # method_name
        controller_name: str,
        route_name: str | None = None) -> Tuple[bool, str]:
    if action and relative_path is None:
        return False, click.style("💣 Error: relative_path required when action present", fg="red")
    if relative_path and action is None:
        return False, click.style("💣 Error: action required when relative_path present", fg="red")

    parameters_with_types_joined = ""
    parameters = []
    if route_name:
        parameters_with_types, parameters = \
            parse_route_name_for_params_and_types(route_name)
        parameters_with_types_joined = ", ".join(parameters_with_types)


    is_redirect = route_http_method_for_action(action) == "POST"
    contents = []
    if action:
        if is_redirect:
            contents.extend(["from flask import redirect, url_for", ""])
        else:
            contents.extend(["from flask import render_template", ""])
    contents.append(f"class {controller_name}:")
    if action:
        contents.extend([
            "    @staticmethod",
            f"    def {action}({parameters_with_types_joined}) -> str:",
        ])
        if is_redirect:
            parameter_reference = route_build_parameter_reference(parameters)
            redirect_route_reference = relative_path.replace("/", ".")
            contents.append(
                f"        return redirect(url_for('{redirect_route_reference}"
                f".index'{parameter_reference}))")
        else:
            relative_view_file_path = \
                os.path.join(relative_path, f"{action}.html")
            contents.append(f"        return render_template('"
                            f"{relative_view_file_path}')")
    else:
        contents.append("    pass")
    try:
        controller_file_path = os.path.join(
            "app", "controllers", f"{camel_to_snake(controller_name)}.py")
        write_file(controller_file_path, contents)
    except FileExistsError:
        message = (
            click.style("⚠️ Warning: Controller Already Exists\n", fg="yellow", bold=True) +
            click.style(f"    - Controller {click.style(controller_name, bold=True)}", fg="yellow") + click.style(" already exists.\n", fg="yellow" ) +
            click.style("    - No changes were made to existing controller\n", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(
            f"💣 Error: Failed to create controller:\n{exception}", fg="red")

    try:
        controller_init_path = os.path.join("app", "controllers", "__init__.py")
        init_contents = [f"from .{camel_to_snake(controller_name)} import {controller_name}"]

        append_file(controller_init_path, init_contents)
    except FileNotFoundError:
        message = (
            click.style("⚠️  Warning: Controller __init__.py Missing\n", fg="yellow", bold=True) +
            click.style(f"    - Controller {click.style(controller_name, bold=True)}", fg="yellow") + click.style(" was created, but __init__.py does not exist.\n", fg="yellow") +
            click.style("    - You may need to register the controller manually.", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(
            f"💣 Error: Failed to update __init__.py:\n{exception}", fg="red")

    if action:
        message = (
            click.style(f"✅ Success: Created Controller Class With Method\n", fg="green", bold=True) +
            click.style(f"    - Created a new controller called {click.style(controller_name, bold=True)}\n", fg="green") +
            click.style(f"    - Added method {click.style(action, bold=True)}", fg="green") + click.style(" to controller\n", fg="green") +
            click.style(f"    - Registered {click.style(controller_name, bold=True)}", fg="green") + click.style(f" at {click.style('app/controllers/__init__.py', bold=True, fg='green')}\n", fg="green") +
            click.style(f"    - New controller located at {click.style(controller_file_path, bold=True)}\n", fg="green")
        )
    else:
        message = (
            click.style(f"✅ Success: Created Controller Class\n", fg="green", bold=True) +
            click.style(f"    - Created a new controller called {click.style(controller_name, bold=True)}\n", fg="green") +
            click.style(f"    - Registered {click.style(controller_name, bold=True)}", fg="green") + click.style(f" at {click.style('app/controllers/__init__.py', bold=True, fg='green')}\n", fg="green") +
            click.style(f"    - New controller located at {click.style(controller_file_path, bold=True)}\n", fg="green")
        )

    return True, message
