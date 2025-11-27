import os
import sys
import subprocess
from typing import Optional, Iterable, Dict


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

def _read_template(file_path):
    """Read a template file and return its content as a string."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def _write_file(path: str, contents: str):
    # Split directory and filename
    directory = os.path.dirname(path)

    # Create the directory (and parents) if needed
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Check existence
    if os.path.exists(path):
        raise FileExistsError(f"{path} already exists")

    # Write text with UTF-8 encoding
    with open(path, "w", encoding="utf-8") as f:
        f.write(contents)

def _pip_install_in_venv(venv_dir: str, packages):
    # Use the venv's pip executable. On Windows it's under Scripts, else bin.
    pip_path = os.path.join(venv_dir, "bin", "pip")
    subprocess.check_call([pip_path, "install", *packages])

def _write_requirements_from_venv(venv_dir: str, project_path: str):
    """
    Run `pip freeze` inside the venv and write the output to
    `<project_path>/requirements.txt`.
    """
    pip_path = os.path.join(venv_dir, "bin", "pip")

    # Capture pip freeze output
    output = subprocess.check_output([pip_path, "freeze"], text=True)

    reqs_path = os.path.join(project_path, "requirements.txt")
    with open(reqs_path, "w", encoding="utf-8") as f:
        f.write(output)
