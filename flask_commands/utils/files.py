import re
import os
import click
from typing import Dict, Optional

def file_append_file(file_path: str, contents: list[str]) -> None:
    """Appends a list of lines from contents to the file_path.  Insert a
    leading newline only if the file doesn't already end with one. Rasises
    a File Not Found Error if the file does not exist.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No file exists at : {file_path}")

    normalized_content = [
        line if line.endswith("\n") else line + "\n"
        for line in contents
    ]

    # if the file doesn't end with a new line character then add one
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if lines and not lines[-1].endswith("\n"):
        normalized_content.insert(0, '\n')

    with open(file_path, "a") as f:
        for line in normalized_content:
            f.write(line)

def file_copy_templates(project_path: str, include_db: bool, replacements: Optional[Dict[str, str]] = None) -> None:
    """
    Copy everything under the package 'templates' directory into the target
    project_path, preserving directory structure. Optionally apply simple
    string replacements to file contents (e.g. {'project_name': name}).
    """
    package_root = os.path.dirname(os.path.dirname(__file__))
    project_root_directory = os.path.join(package_root, "project")
    project_no_db_directory = os.path.join(package_root, "project_no_db")

    no_db_overrides = {
        ".env": os.path.join(project_no_db_directory, ".env"),
        ".env.example": os.path.join(project_no_db_directory, ".env.example"),
        os.path.join("app", "__init__.py"): os.path.join(project_no_db_directory, "app", "__init__.py"),
    }

    for root, directories, files in os.walk(project_root_directory):
        directories[:] = [d for d in directories if d != "__pycache__"]
        for filename in files:
            if filename == ".DS_Store" or filename.endswith(".pyc"):
                continue

            source_path = os.path.join(root, filename)
            relative_path = os.path.relpath(source_path, project_root_directory)

            # Skip over models folder when setup does not include a database
            if not include_db and relative_path.startswith(os.path.join("app", "models")):
                continue

            destination_path = os.path.join(project_path, relative_path)

            template_path = source_path
            if not include_db and relative_path in no_db_overrides:
                template_path = no_db_overrides[relative_path]
                
            content = _read_template(template_path)

            if replacements:
                for key, value in replacements.items():
                    content = content.replace(key, value)

            file_write_file(destination_path, content.splitlines())

def file_insert_flask_import_name_into_lines(
        lines: list[str],
        missing_method: str) -> list[str]:
    """
    Ensure `missing_method` exists in a `from flask import ...` line.

    If a Flask import line already exists, append the missing name to that line.
    Otherwise insert a new `from flask import <missing_method>` line using the
    normal import insertion logic.
    """
    flask_import_pattern = re.compile(r"^from\s+flask\s+import\s+(.+)$")

    for index, line in enumerate(lines):
        match = flask_import_pattern.match(line.strip())
        if not match:
            continue

        existing_names = [
            name.strip()
            for name in match.group(1).split(",")
            if name.strip()
        ]

        if missing_method not in existing_names:
            existing_names.append(missing_method)

        lines[index] = f"from flask import {', '.join(existing_names)}"
        return lines

    return file_insert_import_into_lines(
        lines,
        f"from flask import {missing_method}"
    )

def file_insert_import_into_lines(lines, import_statement) -> list:
    """
    Inserts an import or from statement into a list of lines.  Places the
    statement after any existing import/from block, and adds a blank line
    after the inserted statement if needed.

    Args:
        lines: List of source lines to modify.
        import_statement: Import/from line to insert.

    Returns:
        The modified list of lines.

    Examples:
        lines = ["import os", "", "print('hi')"]
        result = file_insert_import_into_lines(lines, "from sys import path")
        # result == ["import os", "from sys import path", "", "print('hi')"]
    """
    insert_at = 0
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_at = idx + 1
            continue
        if stripped == "":
            if insert_at == 0:
                continue
            break
        break
    lines.insert(insert_at, import_statement)
    if insert_at + 1 < len(lines) and lines[insert_at + 1].strip() != "":
        lines.insert(insert_at + 1, "")
    return lines

def file_is_project_root() -> bool:
    if os.path.isdir("app") and os.path.isfile("run.py"):
        return True

    click.secho("⚠️  Warning: You are not currently in a Flask project root directory.", fg="yellow", bold=True)
    click.secho("    - In order to run a flask make:... command please make sure you are in your flask application's main project directory", fg="yellow")
    click.echo(
        click.style(f"    - Change to your project root or run {click.style('`flask new`', bold=True)} ", fg="yellow") +
        click.style(f"to create a new flask project", fg="yellow")
    )
    click.secho("    - Flask-Commands expects to find app/ and run.py in the current directory", fg="yellow")
    click.secho("    - No files were created or changed", fg="yellow")
    return False

def file_write_file(file_path: str, contents: list[str]) -> None:
    """Writes the contents to the file_path for a new file.  Raises a File
    Exists error if the file already exists at the given path directory."""
    # Split directory and filename
    directory = os.path.dirname(file_path)

    # Create the directory (and parents) if needed
    # Not needed example: Only create directories when the path includes one; os.path.dirname("file.txt") is "".
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

def _read_template(file_path):
    """Read a template file and return its content as a string."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
