import os
import ast
import click

from .files import file_append_file, file_write_file
from .naming import camel_to_snake, pluralize, singularize
from .scaffold import (
    filter_falsy,
    split_dotted_path_with_action_into_relative_path_and_action,
    split_pascal_case,
)

def model_generate_hierarchy_from_controller_name(controller_name: str) -> tuple[list[str], list[str], str]:
    """
    Split a controller class name into `namespace`, `parent_models`, and `child_model_name`.

    This function removes a trailing `Controller` suffix (if present), splits the
    remaining PascalCase name into segments, then resolves those segments against
    registered model class names from `app/models/__init__.py`.

    Resolution rules:
    1. Leading unmatched segments are collected as `namespace`.
    2. A contiguous run of matched model segments is collected as `parent_models`.
    At each position, the longest joined model match is chosen.
    3. Remaining unmatched segments are joined into `child_model_name` (PascalCase).

    Edge cases:
    - If the name is empty after removing `Controller`, returns `([], [], "")`.
    - If no model match is found, all segments become `namespace` and
    `child_model_name` is `""`.
    If no model is registered, all parsed segments are treated as `namespace`.

    Args:
        controller_name (str): Controller class name, e.g.
            `"AdminUserProfileAvatarController"`.

    Returns:
        tuple[list[str], list[str], str]:
            `(namespace, parent_models, child_model_name)`.

    Examples:
        >>> model_generate_hierarchy_from_controller_name("Controller")
        ([], [], '')

        # No registered models
        >>> model_generate_hierarchy_from_controller_name("PostCommentImagesController")
        (['Post', 'Comment', 'Images'], [], '')

        # Registered models: User
        >>> model_generate_hierarchy_from_controller_name("AdminUserAvatarController")
        (['Admin'], ['User'], 'Avatar')

        # Registered models: User, Profile
        >>> model_generate_hierarchy_from_controller_name("AdminUserProfileController")
        (['Admin'], ['User', 'Profile'], '')

        # Registered models: User, UserProfile
        >>> model_generate_hierarchy_from_controller_name("AdminUserProfileAvatarController")
        (['Admin'], ['UserProfile'], 'Avatar')
    """

    name_without_suffix = controller_name
    if controller_name.endswith("Controller"):
        name_without_suffix = controller_name[:-len("Controller")]

    model_segments = split_pascal_case(name_without_suffix)
    if not model_segments:
        return [], [], ""

    return _split_hierarchy_from_segments(model_segments)

def model_generate_hierarchy_from_dotted_path_with_action(dotted_path_with_action: str) -> tuple[list[str], list[str], str]:
    """
    Split a dotted route-like path into namespace, parent model chain, and child model.

    The function first separates `dotted_path_with_action` into a relative path and
    an action segment, then analyzes only the relative path segments from left to right.

    Resolution rules:
    1. Leading segments that are *not* registered models are collected as `namespace`.
    2. The next contiguous run of registered model segments is collected as `parent_models`.
    3. Remaining segments are folded into a single `child_model` joined with `_`.
    If no remainder exists, the child model may be promoted from the parent chain
    by `_finalize_child_model_name_for_routing`, or end up empty when nothing can
    be inferred.

    Model matching is done in snake_case against registered models from
    `app/models/__init__.py`, with each path segment singularized before comparison.

    Args:
        dotted_path_with_action (str): Dotted path that may include a trailing action,
            e.g. "admin.posts.comments.index" or "posts.index".

    Returns:
        tuple[list[str], list[str], str]:
            - namespace: unmatched leading path segments
            - parent_models: contiguous matched model segments
            - child_model: final child segment (possibly compound with `_`), or ""

    Examples:
        >>> model_generate_hierarchy_from_dotted_path_with_action("posts.index")
        ([], [], 'posts')

        >>> model_generate_hierarchy_from_dotted_path_with_action("admin.posts.show")
        (['admin'], [], 'posts')

        >>> model_generate_hierarchy_from_dotted_path_with_action("admin.posts.comments.index")
        (['admin'], ['posts'], 'comments')

        >>> model_generate_hierarchy_from_dotted_path_with_action("admin.posts.shop.images.show")
        (['admin'], ['posts'], 'shop_images')

        >>> model_generate_hierarchy_from_dotted_path_with_action("admin.users.user_profile.index")
        (['admin'], ['users'], 'user_profile')

        >>> model_generate_hierarchy_from_dotted_path_with_action("landinng")
        ([], [], '')
    """

    registered_models = model_get_registered_models()
    registered_snake_case_models = \
        model_model_names_to_snake_case_names(registered_models)
    relative_path, _ = \
        split_dotted_path_with_action_into_relative_path_and_action(
            dotted_path_with_action)

    segments = relative_path.split("/")
    segments = filter_falsy(segments)
    namespace: list[str] = []
    parent_models: list[str] = []
    index = 0

    # 1) Namespace prefix
    while index < len(segments) and singularize(segments[index]) not in registered_snake_case_models:
        namespace.append(segments[index])
        index += 1

    # 2) Contiguous chain of models
    while index < len(segments) and singularize(segments[index]) in registered_snake_case_models:
        parent_models.append(segments[index])
        index += 1

    # 3) Remainder becomes child segment
    parent_models, child_model = _finalize_child_model_name_for_routing(
        parent_models, segments[index:], "_")

    return namespace, parent_models, child_model

# TODO: Stopped here (the doc string is good need to make better test for this function there is currently only one test)
def model_generate_model_name_from_controller_name(controller_name: str) -> tuple[str, list[str]]:
    """
    Generate model name candidates from a controller class name.

    This function returns two values:
    1. `non_nested_model_name`: a direct PascalCase model candidate.
    2. `nested_model_names`: hierarchy-derived nested candidate(s).

    `non_nested_model_name` is computed by:
    - removing a trailing `Controller` suffix when present,
    - splitting the remaining value with `split_pascal_case`,
    - singularizing only the final segment,
    - joining segments back into PascalCase.
    If no PascalCase segments are found, it returns `""`.

    `nested_model_names` is computed as follows:
    - Call `_generate_nested_model_names_from_controller_name(controller_name)`.
    - That helper first obtains `namespace`, `parent_models`, and `child_model_name`
    from `model_generate_hierarchy_from_controller_name(controller_name)`.
    - If `child_model_name == ""` and `parent_models == []`, return `namespace`.
    - If `child_model_name == ""` and `parent_models != []`, return `[]`.
    - Otherwise, return `[child_model_name]`.

    Args:
        controller_name (str): Controller class name to parse, e.g.
            `"PostsController"` or `"AdminUserAvatarController"`.

    Returns:
        tuple[str, list[str]]: `(non_nested_model_name, nested_model_names)`.

    Examples:
        # No registered models
        >>> model_generate_model_name_from_controller_name("PostCommentImageController")
        ('PostCommentImage', ['Post', 'Comment', 'Image'])
        >>> model_generate_model_name_from_controller_name("PostsController")
        ('Post', ['Posts'])
        >>> model_generate_model_name_from_controller_name("Controller")
        ('', [])

        # Registered models include: User
        >>> model_generate_model_name_from_controller_name("AdminUserAvatarController")
        ('AdminUserAvatar', ['Avatar'])

        # Registered models include: User, Profile
        >>> model_generate_model_name_from_controller_name("AdminUserProfileController")
        ('AdminUserProfile', [])
    """

    non_nested_model_name = \
        _generate_non_nested_model_name_from_controller_name(controller_name)
    nested_model_names = \
        _generate_nested_model_names_from_controller_name(controller_name)

    return non_nested_model_name, nested_model_names,

def model_generate_model_name_from_dotted_path_with_action(dotted_path_with_action: str) -> str:
    """
    Infer a model name from a dotted view path.

    Uses split_dotted_path_with_action_into_relative_path_and_action to
    derive the relative path, then singularizes the final segment
    and converts it to title case.

    Args:
        dotted_path_with_action (str): The dotted module path or name.

    Returns:
        str: The inferred model name in title case.

    Example:
        >>> name = model_generate_model_name_from_dotted_path_with_action("posts.index")
        >>> name
        'Post'
        >>> name = model_generate_model_name_from_dotted_path_with_action("posts")
        >>> name
        'Post'
    """
    relative_path, action = \
        split_dotted_path_with_action_into_relative_path_and_action(
            dotted_path_with_action)
    if relative_path != "":
        relative_path_last_segment = relative_path.split('/')[-1]
        model_name = singularize(relative_path_last_segment).title()
    else:
        model_name = singularize(action).title()
    return model_name

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

def model_make_file(model_name: str, model_init_path: str, model_file_path: str) -> tuple[bool, str]:
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
        tuple[bool, str]: A tuple containing:
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
        file_write_file(model_file_path, file_contents)
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
        file_append_file(model_init_path, init_contents)
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

def model_model_names_to_snake_case_names(model_names:list[str]) -> list[str]:
    """
    Convert a list of PascalCase model class names to snake_case slugs.

    Args:
        model_names: Model class names in PascalCase, e.g. ["Post", "UserAPI"].

    Returns:
        A list of snake_case names in the same order, e.g. ["post", "user_api"].

    Examples:
        >>> model_model_names_to_snake_case_names(["Post", "Comment"])
        ['post', 'comment']
        >>> model_model_names_to_snake_case_names(["RecipeCommentImage"])
        ['recipe_comment_image']
    """
    return [camel_to_snake(model) for model in model_names]

def _finalize_child_model_name_for_routing(
        parent_models: list[str],
        remaining_segments: list[str],
        joiner: str) -> str:
    if remaining_segments:
        return parent_models, joiner.join(remaining_segments)
    if parent_models:
        return parent_models[:-1], parent_models[-1]
    return parent_models, ""

def _find_longest_running_model_segment_match_from_index(
        segments: list[str],
        registered_models: list[str],
        starting_index: int) -> tuple[str | None, int]:
    if starting_index < 0 or starting_index >= len(segments):
        return None, 0

    longest_running_model_segment: str | None = None
    longest_running_match_length: int = 0
    running_segment: str = ""
    running_length: int = 0

    for index in range(starting_index, len(segments)):
        running_segment += segments[index]
        running_length = (index - starting_index) + 1
        if running_segment in registered_models:
            longest_running_model_segment = running_segment
            longest_running_match_length = running_length

    return longest_running_model_segment, longest_running_match_length

def _generate_nested_model_names_from_controller_name(controller_name: str) -> list[str]:
    namespace, parent_models, child_model_name = \
        model_generate_hierarchy_from_controller_name(controller_name)
    if child_model_name == "":
        if parent_models == []:
            return namespace
        return []
    return [child_model_name]

def _generate_non_nested_model_name_from_controller_name(controller_name: str) -> str:
    name_without_suffix = controller_name
    if controller_name.endswith("Controller"):
        name_without_suffix = controller_name[:-len("Controller")]
    model_segments = split_pascal_case(name_without_suffix)
    if not model_segments:
        return ""

    model_segments[-1] = singularize(model_segments[-1]).title()
    return "".join(model_segments)

def _split_hierarchy_from_segments(segments: list[str]) -> tuple[list[str], list[str], str]:
    namespace: list[str] = []
    parent_models: list[str] = []
    child_model_name = ""

    registered_models = model_get_registered_models()

    index = 0
    # 1) Detect namespace prefix
    while index < len(segments):
        match, _ = \
            _find_longest_running_model_segment_match_from_index(
                segments, registered_models, index)
        if match is None:
            namespace.append(segments[index])
            index += 1
        else:
            break

    # 2) Detect contiguous cahin of models from current index
    while index < len(segments):
        match, match_length = \
            _find_longest_running_model_segment_match_from_index(
                segments, registered_models, index)
        if match is None:
            break
        parent_models.append(match)
        index += match_length

    # 3) Remaing segments become child_model_name
    child_model_name = "".join(segments[index:])

    return namespace, parent_models, child_model_name
