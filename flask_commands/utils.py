import os
import re
import sys
import subprocess
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
            f"⚠️ Warning: Controller {controller_name} already "
            "contains method '{method_name}'.")
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
        message = f"✅ Added method '{method_name}' to {controller_name}"
        return True, message

    message =  (
        f"⚠️ Warning: Could not find class {controller_name} "
        f"in file {controller_file_path}." )
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
    _write_file(controller_file_path, contents)

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

            _write_file(destination_path, content)

def view_make_file(destination_file_path: str, filename: str) -> None:
    content = ''
    _write_file(destination_file_path, content)

def parse_dots(dotted_path_with_name: str) -> Tuple[str, str]:
    parts = dotted_path_with_name.lower().split(".")
    relative_path = '' if len(parts) == 1 else '/'.join(parts[:-1])
    return relative_path, parts[-1]

def _pip_install_in_venv(venv_dir: str, packages):
    print("Installing Python Dependencies")
    pip_path = os.path.join(venv_dir, "bin", "pip")
    subprocess.run([pip_path, "install", *packages], check=True, capture_output=True, text=True)

def _read_template(file_path):
    """Read a template file and return its content as a string."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def _write_file(file_path: str, contents: list):
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

    # Write text with UTF-8 encoding
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(contents) + "\n")

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

