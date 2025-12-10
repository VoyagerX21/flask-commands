import os
import re
import sys
import subprocess
from turtle import dot
import click
from typing import Dict, Iterable, Optional, Tuple

def camel_to_snake(name: str) -> str:
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

def create_venv(project_path: str, packages: Optional[Iterable[str]] = None, freeze_requirements: bool = False) -> str:
    """
    Create a virtual environment at <project_path>/venv using the current
    Python interpreter. If `packages` is provided, install them into the
    new venv using the venv's pip.
    """
    # Ensure the project directory exists
    os.makedirs(project_path, exist_ok=True)

    venv_dir = os.path.join(project_path, "venv")
    subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    if packages:
        _pip_install_in_venv(venv_dir, packages)

    if freeze_requirements:
        _write_requirements_from_venv(venv_dir, project_path)

    return venv_dir

def controller_add_method(controller_name: str, method_name: str, relative_view_file_path: str) -> Tuple[bool, str]:
    controller_file_path = os.path.join(
        "app", "controllers", f"{camel_to_snake(controller_name)}.py")
    # Read existing controller and check for method
    with open(controller_file_path, "r", encoding="utf-8") as f:
        source = f.read()

    method_pattern = rf"def\s+{re.escape(method_name)}\s*\(\)\s*(?:->\s*[^:]+)?\s*:"
    # If method already exists, do nothing and warn user
    if re.search(method_pattern, source):
        message = (
            click.style("⚠️ Warning: Method Already Exists\n", fg="yellow", bold=True) +
            click.style(f"Controller '{controller_name}' already has a method named '{method_name}'.\n", fg="yellow") +
            click.style("No changes were made.", fg="cyan")
        )
        return False, message

    # Try to find class definition to insert method into
    class_pattern = rf"^class\s+{re.escape(controller_name)}\b.*:\\s*$"
    lines = source.splitlines()
    insert_index = None
    # 1. Find the class
    for i, line in enumerate(lines):
        if re.match(class_pattern, line):
            # 2. find end of class (next top-level def/class or EOF)
            j = i + 1
            while j < len(lines):
                # skip blank lines inside the class
                if lines[j].strip() == "":
                    j += 1
                    continue
                # top-level (no indent)
                if len(lines[j]) - len(lines[j].lstrip()) == 0 and \
                        re.match(r"^(class|def)\b", lines[j]):
                    break
                j += 1
            insert_index = j
            break

    # 3. Build the new static method block
    method_block = [
         "",
         "    @staticmethod",
        f"    def {method_name}() -> str:",
        f"        return render_template('{relative_view_file_path}')"
    ]

    # 4. Insert new static method block
    if insert_index is not None:
        for line in reversed(method_block):
            lines.insert(insert_index, line)

        new_source = "\n".join(lines)
        with open(controller_file_path, "w", encoding="utf-8") as f:
            f.write(new_source)
        message = (
            click.style("✅ Method Added Successfully\n", fg="green", bold=True) +
            click.style(f"Added method '{method_name}' to controller '{controller_name}'.\n", fg="green") +
            click.style(f"View: {relative_view_file_path}", fg="cyan")
        )
        return True, message

    message = (
        click.style("⚠️ Warning: Controller Class Not Found\n", fg="yellow", bold=True) +
        click.style(f"Could not locate class '{controller_name}' inside:\n", fg="yellow") +
        click.style(f"  - {controller_file_path}\n", fg="cyan") +
        click.style("No method was added.", fg="yellow")
    )
    return False, message

def controller_make_file(controller_name: str, method_name: str, relative_view_file_path: str) -> Tuple[bool, str]:
    controller_file_path = os.path.join(
        "app", "controllers", f"{camel_to_snake(controller_name)}.py")
    contents = [
         "from flask import render_template",
         "",
        f"class {controller_name}(object):",
         "    @staticmethod",
        f"    def {method_name}() -> str:",
        f"        return render_template('{relative_view_file_path}')"
    ]
    _file_write(controller_file_path, contents)

    controller_init_path = os.path.join("app", "controllers", "__init__.py")
    with open(controller_init_path, "a", encoding="utf-8") as f:
        f.write(f"from .{camel_to_snake(controller_name)} import {controller_name}")

    message = (
        f"✅ Created controller {controller_name} with method "
        f"'{method_name}' at {click.style(controller_file_path, bold=True)}")

    return True, message

def copy_templates(project_path: str, replacements: Optional[Dict[str, str]] = None) -> None:
    """
    Copy everything under the package 'templates' directory into the target
    project_path, preserving directory structure. Optionally apply simple
    string replacements to file contents (e.g. {'project_name': name}).
    """
    templates_directory = os.path.join(os.path.dirname(__file__), "project")

    for root, directories, files in os.walk(templates_directory):
        for filename in files:
            source_path = os.path.join(root, filename)
            relative_path = os.path.relpath(source_path, templates_directory)
            destination_path = os.path.join(project_path, relative_path)

            content = _read_template(source_path)

            if replacements:
                for key, value in replacements.items():
                    content = content.replace(key, value)

            _file_write(destination_path, content)

def generate_controller_name_from(relative_path: str) -> str:
    return ''.join([_singularize(part).title()
                    for part in relative_path.split('/')]) + "Controller"

def generate_model_name_from(relative_path: str, dotted_path_with_name: str) -> Tuple[str, str]:
    if relative_path != "":
        model_name = _singularize(relative_path.split('/')[-1]).title()
    else:
        model_name = _singularize(dotted_path_with_name).title()
    message = (
        f"Infered the model name as ",
        f"{click.style(model_name, bold=True)}")
    return message, model_name

def generate_table_name_from_model_name(model_name: str) -> str:
    return _pluralize(model_name.lower())

def generate_route_file_path_and_blueprint_name(dotted_path_with_name: str, relative_path: str) -> Tuple[str, str]:
    if "." not in dotted_path_with_name:
        return os.path.join("app", "routes", "mains"), 'mains'
    return  os.path.join("app", "routes", relative_path), relative_path.replace("/", "_")

def generate_route_name_from(dotted_path_with_name: str) -> str:
    if "." not in dotted_path_with_name:
        return '/' + dotted_path_with_name
    resource, action = dotted_path_with_name.rsplit(".", 1)
    if action not in ['index', 'create', 'store', 'show', 'edit', 'update', 'destory', 'delete']:
        return '/' + dotted_path_with_name.replace('.', '/')
    if "." in resource:
        relations, object = resource.rsplit(".", 1)
        object = _singularize(object)
    else:
        object = _singularize(resource)
    resource = resource.replace('.', '/')
    return _crud_mapping_route(action, resource, object)

def model_make_file():
    pass

def parse_dots(dotted_path_with_name: str) -> Tuple[str, str]:
    parts = dotted_path_with_name.lower().split(".")
    relative_path = '' if len(parts) == 1 else '/'.join(parts[:-1])
    return relative_path, parts[-1]

def route_add_method(route_name: str, action: str, relative_path: str, controller_name: str | None) -> Tuple[bool, str]:
    # The route folder is already there so we just need to add to routes.py
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
    message = (
        click.style(f"✅ Added {method} route '{action}' to '{route_name}'.", fg="green") + "\n" +
        click.style(f"🔗 Use url_for('{route_name}.{action}') to reference it.", fg="yellow")
    )
    return True, message

def route_make_directory_and_register_blueprint(route_name: str,  action: str, relative_path: str, blueprint_name: str, controller_name: str | None) -> Tuple[bool, str]:
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
    #  4) update the __init__.py in app directory to include the new blueprint
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
    message = (
        click.style(f"📁 Created new route directory for '{blueprint_name}'.", fg="green") + "\n" +
        click.style(f"🧩 Registered the '{blueprint_name}' blueprint and added it to app.__init__.", fg="cyan") + "\n" +
        click.style(f"🛠️ Generated routes.py with the initial {method} action '{action}'.", fg="magenta") + "\n" +
        click.style(f"🔗 Reference using url_for('{route_name}.{action}').", fg="yellow")
    )
    return True, message

def view_make_file(destination_file_path: str, filename: str) -> None:
    content = []
    _file_write(destination_file_path, content)

def _crud_mapping_route(action: str, resource: str, object: str) -> str:
    mapping = {
        "index":    lambda resource, object: f"/{resource}",
        "create":   lambda resource, object: f"/{resource}/create",
        "store":    lambda resource, object: f"/{resource}",
        "show":     lambda resource, object: f"/{resource}/<int:{object}_id>",
        "edit":     lambda resource, object: f"/{resource}/<int:{object}_id>/edit",
        "update":   lambda resource, object: f"/{resource}/<int:{object}_id>",
        "destroy":  lambda resource, object: f"/{resource}/<int:{object}_id>/delete",
        "delete":   lambda resource, object: f"/{resource}/<int:{object}_id>/delete",
    }
    return mapping[action](resource, object)

def _file_append(file_path: str, contents: list[str]) -> None:
    """Appends a list of lines from contents to the file_path.  Rasises a File
    Not Found Error if the file does not exist.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No file exists at : {file_path}")

    normalized_content = [
        line if line.endswith("\n") else line + "\n"
        for line in contents
    ]

    with open(file_path, "a") as f:
        for line in normalized_content:
            f.write(line)

def _file_write(file_path: str, contents: list[str]) -> None:
    """Writes the contents to the file_path for a new file.  Raises a File
    Exists error if the file already exists at the given path directory."""
    # Split directory and filename
    directory = os.path.dirname(file_path)

    # Create the directory (and parents) if needed
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Check existence
    if os.path.exists(file_path):
        raise FileExistsError(f"{file_path} already exists")

    normalized_content = [
        line if line.endswith("\n") else line + "\n"
        for line in contents
    ]

    # Write text with UTF-8 encoding
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(normalized_content)

def _pluralize(name: str) -> str:
    name = name.lower()

    # category -> categories
    if name.endswith("y") and len(name) > 1 and name[-2] not in "aeiou":
        return name[:-1] + "ies"

    # class -> classes (handles most “s”, “x”, “z”, “ch”, “sh” endings)
    if name.endswith(("s", "x", "z", "ch", "sh")):
        return name + "es"

    # default: post -> posts
    return name + "s"

def _pip_install_in_venv(venv_dir: str, packages):
    print("Installing Python Dependencies")
    pip_path = os.path.join(venv_dir, "bin", "pip")
    subprocess.run([pip_path, "install", *packages], check=True, capture_output=True, text=True)

def _read_template(file_path):
    """Read a template file and return its content as a string."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def _singularize(name: str) -> str:
    name = name.lower()
    if name.endswith("ies"):
        return name[:-3] + "y"  # categories -> category
    if name.endswith("ses"):
        return name[:-2]        # classes -> class
    if name.endswith("s") and len(name) > 1:
        return name[:-1]        # posts -> post
    return name

def _write_requirements_from_venv(venv_dir: str, project_path: str):
    """
    Run `pip freeze` inside the venv and write the output to
    `<project_path>/requirements.txt`.
    """
    pip_path = os.path.join(venv_dir, "bin", "pip")

    # Capture pip freeze output
    requirements_content = \
        subprocess.check_output([pip_path, "freeze"], text=True)

    requirements_path = os.path.join(project_path, "requirements.txt")

    write_file(requirements_path, requirements_content)

