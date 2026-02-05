import os
import ast
import click
from typing import Tuple
from .files import append_file, write_file
from .naming import camel_to_snake, pluralize, singularize
from .scaffold import split_dotted_path_with_action_into_relative_path_and_action

def _model_finalize_child_model(parent_models: list[str], remaining_relative_path_segments: list[str], joiner: str) -> str:
    if remaining_relative_path_segments:
        return parent_models, joiner.join(remaining_relative_path_segments)
    if parent_models:
        return parent_models[:-1], parent_models[-1]
    return parent_models, ""

def model_split_hierarchy_from_dotted_path_with_action(dotted_path_with_action: str) -> Tuple[list[str], list[str], str]:
    registered_models = model_get_registered_models()
    relative_path, action = split_dotted_path_with_action_into_relative_path_and_action(dotted_path_with_action)

    relative_path_segments = relative_path.split("/")
    namespace: list[str] = []
    parent_models: list[str] = []
    index = 0

    # 1) Namespace prefix
    while index < len(relative_path_segments) and singularize(relative_path_segments[index]) not in model_slugs:
        namespace.append(relative_path_segments[index])
        index += 1

    # 2) Contiguous chain of models
    while index < len(relative_path_segments) and singularize(relative_path_segments[index]) in model_slugs:
        parent_models.append(relative_path_segments[index])
        index += 1

    # 3) Remainder becomes child segment
    parent_models, child_model = _model_finalize_child_model(
        parent_models, relative_path_segments[index:], "/")

    return namespace, parent_models, child_model


def model_infer_name_from_dotted_view_path(dotted_path_with_action: str) -> str:
    """
    Infer a model name from a dotted view path.

    Uses split_dotted_path_with_action_into_relative_path_and_action to derive the relative path, then
    singularizes the final segment and converts it to title case.

    Args:
        dotted_path_with_action (str): The dotted module path or name.

    Returns:
        str: The inferred model name in title case.

    Example:
        >>> name = model_infer_name_from_dotted_view_path("posts.index")
        >>> name
        'Post'
        >>> name = model_infer_name_from_dotted_view_path("posts")
        >>> name
        'Post'
    """
    relative_path, _ = split_dotted_path_with_action_into_relative_path_and_action(dotted_path_with_action)
    if relative_path != "":
        model_name = singularize(relative_path.split('/')[-1]).title()
    else:
        model_name = singularize(dotted_path_with_action).title()
    return model_name

def model_infer_name_from_controller(controller_name: str) -> str:
    """
    Infer a model name from a controller class name.

    Examples:
        PostController -> Post
        PostCommentImageController -> Image
        AdminUserController -> User
    """
    name_without_suffix = controller_name
    if controller_name.endswith("Controller"):
        name_without_suffix = controller_name[:-len("Controller")]
    snake = camel_to_snake(name_without_suffix)
    last_segment = snake.split("_")[-1] if snake else ""
    return singularize(last_segment).title()

def model_get_registered_models() -> list[str]:
    """
    Return the list of registered model class names from `app/models/__init__.py`.

    The function parses the file’s import statements (relative imports or
    `app.models.*` absolute imports) and collects any imported names that start
    with an uppercase letter, treating them as model classes.

    Returns:
        list[str]: Sorted model class names. Returns an empty list if the file
            is missing or contains invalid Python syntax.

    Examples:
        # app/models/__init__.py:
        #   from .post import Post
        #   from app.models.comment import Comment
        #   from .helpers import format_slug
        #
        # model_get_registered_models()
        # -> ['Comment', 'Post']
    """
    models_init_file_path = os.path.join("app", "models", "__init__.py")
    try:
        with open(models_init_file_path, "r", encoding="utf-8") as file:
            init_content = file.read()
    except FileNotFoundError:
        return []
    try:
        tree = ast.parse(init_content, filename=models_init_file_path)
    except SyntaxError:
        return []
    models: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
           continue
        # allow relative imports OR absolute app.models import
        if node.level == 0 and not (node.module and node.module.startswith("app.models.")):
            continue
        for alias in node.names:
            if alias.name and alias.name[0].isupper():
                models.add(alias.name)
    return sorted(models)

def model_make_file(model_name: str, model_init_path: str, model_file_path: str) -> Tuple[bool, str]:
    """
    Create a new SQLAlchemy model file with standard boilerplate code.

    This function generates a model class file with common attributes (id, created_at, updated_at)
    and database operations (store_in_database, delete_from_database). It also registers the model
    in the __init__.py file by adding an import statement.

    Args:
        model_name (str): The name of the model class to create (example, 'User', 'Post').
        model_init_path (str): The file path to the models __init__.py file where the import
                               statement will be appended.
        model_file_path (str): The file path where the new model file will be created.

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if the model was created successfully.
            - str: A formatted success message with file paths and status indicators.
    """
    try:
        file_contents = [
            "from app import db",
            "from datetime import datetime, timezone",
            "",
            f"class {model_name}(db.Model):",
            f"    __tablename__ = '{pluralize(model_name.lower())}'",
            "    # Columns",
            "    id = db.Column(db.Integer, primary_key=True)",
            "    created_at = db.Column(db.DateTime(timezone=True),",
            "                           index=True, ",
            "                           default=lambda: datetime.now(timezone.utc))",
            "    updated_at = db.Column(db.DateTime(timezone=True),",
            "                           default=lambda: datetime.now(timezone.utc), ",
            "                           onupdate=lambda: datetime.now(timezone.utc))",
            "",
            "    def store_in_database(self):",
            "        db.session.add(self)",
            "        db.session.commit()",
            "",
            "    def delete_from_database(self):",
            "        db.session.delete(self)",
            "        db.session.commit()",
            "",
            "    def __repr__(self):",
            '        """Model representation for Code Debugging"""',
            f"        return f'<{model_name} id:{{self.id}}>'",
        ]
        write_file(model_file_path, file_contents)
    except FileExistsError:
        message = (
            click.style("⚠️  Warning: Model Already Exists\n", fg="yellow", bold=True) +
            click.style(f"    - Model {click.style(model_name, bold=True)} ", fg="yellow") + click.style("already exists\n", fg="yellow" ) +
            click.style("    - No changes were made to the existing model\n", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(
            f"💣 Error: Failed to create model:\n{exception}", fg="red")

    try:
        init_contents = [f"from .{model_name.lower()} import {model_name}"]
        append_file(model_init_path, init_contents)
    except FileNotFoundError:
        message = (
            click.style("⚠️  Warning: Model __init__.py Missing\n", fg="yellow", bold=True) +
            click.style(
                f"    - Model '{model_name}' was created, "
                f"but __init__.py does not exist.\n",
                fg="yellow"
            ) +
            click.style("    - You may need to register it manually.", fg="yellow")
        )
        return False, message
    except Exception as exception:
        return False, click.style(
            f"💣 Error: Failed to update __init__.py:\n{exception}", fg="red")


    message = (
        click.style("✅ Success: Created New Model\n", fg="green", bold=True) +
        click.style(f"    - Created model {click.style(model_name, bold=True)}", fg="green") + click.style(f" at {click.style(model_file_path, bold=True)}\n", fg="green") +
        click.style(f"    - Registered {click.style(model_name, bold=True)}", fg="green") + click.style(f" model at {click.style(model_init_path, bold=True)}\n", fg="green")
    )
    return True, message
