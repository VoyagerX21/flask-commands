import os
import ast
from venv import create
import click

from flask_commands.utils.data_types import (
    CreatedModel,
    ModelResult,
    ScaffoldStatus
)

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
    be generated.

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

def model_generate_hierarchy_from_model_name(model_name: str) -> tuple[list[str], list[str], str]:
    """
    Split a model class name into `namespace`, `parent_models`, and `child_model_name`.

    The function parses `model_name` with `split_pascal_case`, then resolves the
    segments against registered model class names from `app/models/__init__.py`
    via `_split_hierarchy_from_segments`.

    Resolution rules:
    1. Leading unmatched segments are collected as `namespace`.
    2. A contiguous run of matched model segments is collected as `parent_models`,
    choosing the longest joined model match at each position.
    3. Remaining segments are joined into `child_model_name` (PascalCase).

    Edge cases:
    - If `model_name` yields no PascalCase segments, returns `([], [], "")`.
    - If no model match is found, all segments become `namespace` and
    `child_model_name` is `""`.
    - If no models are registered, all parsed segments are treated as `namespace`.

    Args:
        model_name (str): Model class name, e.g. `"AdminUserProfileAvatar"`.

    Returns:
        tuple[list[str], list[str], str]:
            `(namespace, parent_models, child_model_name)`.

    Examples:
        >>> model_generate_hierarchy_from_model_name("")
        ([], [], '')

        # No registered models
        >>> model_generate_hierarchy_from_model_name("PostCommentImages")
        (['Post', 'Comment', 'Images'], [], '')

        # Registered models: User
        >>> model_generate_hierarchy_from_model_name("AdminUserAvatar")
        (['Admin'], ['User'], 'Avatar')

        # Registered models: User, Profile
        >>> model_generate_hierarchy_from_model_name("AdminUserProfile")
        (['Admin'], ['User', 'Profile'], '')

        # Registered models: User, UserProfile
        >>> model_generate_hierarchy_from_model_name("AdminUserProfileAvatar")
        (['Admin'], ['UserProfile'], 'Avatar')
    """
    model_segments = split_pascal_case(model_name)
    if not model_segments:
        return [], [], ""

    return _split_hierarchy_from_segments(model_segments)

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
    Generate a model class name from a dotted path that may include an action.

    The input is split into `(relative_path, action)` using
    `split_dotted_path_with_action_into_relative_path_and_action`, where `action`
    is always the last dot-separated segment.

    Rules:
    1. If `relative_path` is not empty, use the last slash-separated segment from
       `relative_path`.
    2. Otherwise, use `action`.
    3. Singularize the chosen segment, then convert snake_case to PascalCase.

    Args:
        dotted_path_with_action (str): Dotted path such as `"posts.index"`,
            `"admin.user_profiles.show"`, or `"posts"`.

    Returns:
        str: Generated model class name in PascalCase.

    Examples:
        >>> model_generate_model_name_from_dotted_path_with_action("posts.index")
        'Post'
        >>> model_generate_model_name_from_dotted_path_with_action("posts")
        'Post'
        >>> model_generate_model_name_from_dotted_path_with_action("admin.posts.show")
        'Post'
        >>> model_generate_model_name_from_dotted_path_with_action("user_profiles.index")
        'UserProfile'
        >>> model_generate_model_name_from_dotted_path_with_action("index")
        'Index'
    """


    relative_path, action = \
        split_dotted_path_with_action_into_relative_path_and_action(
            dotted_path_with_action)

    if relative_path != "":
        relative_path_last_segment = relative_path.split('/')[-1]
        signularized_segment = singularize(relative_path_last_segment).title()
    else:
        signularized_segment = singularize(action).title()

    return "".join([part.title() for part in signularized_segment.split("_") if part])

def model_generate_model_name_from_model_name(model_name: str) -> tuple[str, list[str]]:
    """
    Generate model name candidates from a model class name.

    This function returns two values:
    1. `non_nested_model_name`: a direct PascalCase model candidate.
    2. `nested_model_names`: hierarchy-derived nested candidate(s).

    `non_nested_model_name` is computed by:
    - splitting `model_name` with `split_pascal_case`,
    - singularizing only the final segment,
    - joining segments back into PascalCase.
    If no PascalCase segments are found, it returns `""`.

    `nested_model_names` is computed as follows:
    - Call `_generate_nested_model_names_from_model_name(model_name)`.
    - That helper first obtains `namespace`, `parent_models`, and `child_model_name`
      from `model_generate_hierarchy_from_model_name(model_name)`.
    - If `child_model_name == ""` and `parent_models == []`, return `namespace`.
    - If `child_model_name == ""` and `parent_models != []`, return `[]`.
    - Otherwise, return `[child_model_name]`.

    Args:
        model_name (str): Model class name to parse, e.g.
            `"Posts"` or `"AdminUserAvatar"`.

    Returns:
        tuple[str, list[str]]: `(non_nested_model_name, nested_model_names)`.

    Examples:
        # No registered models
        >>> model_generate_model_name_from_model_name("PostCommentImages")
        ('PostCommentImage', ['Post', 'Comment', 'Images'])
        >>> model_generate_model_name_from_model_name("Posts")
        ('Post', ['Posts'])
        >>> model_generate_model_name_from_model_name("")
        ('', [])

        # Registered models include: User
        >>> model_generate_model_name_from_model_name("AdminUserAvatar")
        ('AdminUserAvatar', ['Avatar'])

        # Registered models include: User, Profile
        >>> model_generate_model_name_from_model_name("AdminUserProfile")
        ('AdminUserProfile', [])
    """
    non_nested_model_name = \
        _generate_non_nested_model_name_from_model_name(model_name)
    nested_model_names = \
        _generate_nested_model_names_from_model_name(model_name)

    return non_nested_model_name, nested_model_names

def model_get_registered_models() -> list[str]:
    """
    Return registered model class names from `app/models/__init__.py`.

    This function parses `app/models/__init__.py` with `ast` and inspects only
    top-level `from ... import ...` statements (`ast.ImportFrom`).

    Accepted import sources:
    - Relative imports (for example, `from .post import Post`)
    - Absolute submodule imports under `app.models.` (for example,
    `from app.models.post import Post`)

    From accepted imports, only imported names that begin with an uppercase
    letter are treated as model classes. Names are deduplicated and returned
    sorted alphabetically.

    Returns:
        list[str]: Sorted model class names. Returns `[]` when
            `app/models/__init__.py` is missing or contains invalid Python syntax.

    Examples:
        # app/models/__init__.py:
        #   from .post import Post
        #   from .user_profile import UserProfile
        #   from app.models.comment import Comment
        #   from .helpers import format_slug
        #   from app.controllers.users import UsersController
        #
        # model_get_registered_models()
        # -> ['Comment', 'Post', 'UserProfile']
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

def model_make_file(model_name: str) -> tuple[CreatedModel, str]:
    """
    Create and register a SQLAlchemy model file for `model_name`.

    The function derives a snake_case slug from `model_name` using
    `camel_to_snake` and writes the model file to `app/models/<model_slug>.py`.
    In addtion the function generates a basic model class, and attempts to
    register it in `app/models/__init__.py` as
    `from .{model_slug} import {model_name}`

    The generated model:
    - imports `db`
    - defines `__tablename__ = pluralize(model_slug)`
    - includes `id`, `created_at`, and `updated_at`
    - includes `store_in_database()` and `delete_from_database()`

    Args:
        model_name (str): PascalCase model class name, such as `"Post"` or
            `"UserProfile"`.

    Returns:
        tuple[CreatedModel, str]:
            - `CreatedModel`: structured result for the created or attempted model
              - CreatedModel will have status ADDED with a success message
                when file creation and registration both succeed.
              - CreatedModel will have status WARNING with a warning message
                if the model file already exists.
              - CreatedModel will have status WARNING with a warning message
                if `app/models/__init__.py` is missing
                (model file may still be created).
              - CreatedModel will have status ERROR with an error message
                for unexpected write/append failures.
            - `str`: styled success, warning, or error message

    Examples:
        >>> created_model, message = model_make_file("Post")
        >>> created_model.model_name
        'Post'

    Notes:
    - Existing model files return status `EXISTS`.
    - If the model file is created but `app/models/__init__.py` is missing, the
      result status is `WARNING`.
    - Registration path is stored on `CreatedModel.registration_file_path`.
    """

    model_init_path = os.path.join("app", "models", "__init__.py")
    model_file_path = os.path.join("app", "models", f"{camel_to_snake(model_name)}.py")

    try:
        file_contents = [
            "from app import db",
            "from datetime import datetime, timezone",
            "",
            f"class {model_name}(db.Model):",
            f"    __tablename__ = '{pluralize(camel_to_snake(model_name))}'",
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
        return CreatedModel(
            model_name=model_name,
            model_file_path=model_file_path,
            registration_file_path=model_init_path,
            status=ScaffoldStatus.EXISTS,
            is_successful=False), message
    except Exception as exception:
        message = click.style(
            f"💣 Error: Failed to create model:\n{exception}", fg="red")
        return CreatedModel(
            model_name=model_name,
            model_file_path=model_file_path,
            registration_file_path=model_init_path,
            status=ScaffoldStatus.ERROR,
            is_successful=False), message

    try:
        init_contents = [f"from .{camel_to_snake(model_name)} import {model_name}"]
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
        return CreatedModel(
            model_name=model_name,
            model_file_path=model_file_path,
            registration_file_path=model_init_path,
            status=ScaffoldStatus.WARNING,
            is_successful=False), message
    except Exception as exception:
        message = click.style(
            f"💣 Error: Failed to update __init__.py:\n{exception}", fg="red")
        return CreatedModel(
            model_name=model_name,
            model_file_path=model_file_path,
            registration_file_path=model_init_path,
            status=ScaffoldStatus.ERROR,
            is_successful=False), message

    message = (
        click.style("✅ Success: Created New Model\n", fg="green", bold=True) +
        click.style(f"    - Created model {click.style(model_name, bold=True)}", fg="green") +
        click.style(f" at {click.style(model_file_path, bold=True)}\n", fg="green") +
        click.style(f"    - Registered {click.style(model_name, bold=True)}", fg="green") +
        click.style(f" model at {click.style(model_init_path, bold=True)}\n", fg="green")
    )
    return CreatedModel(
        model_name=model_name,
        model_file_path=model_file_path,
        registration_file_path=model_init_path,
        status=ScaffoldStatus.ADDED,
        is_successful=True), message

def model_model_names_to_snake_case_names(model_names:list[str]) -> list[str]:
    """
    Convert model class names to snake_case names.

    Each item is transformed with `camel_to_snake` and returned in the same order.

    Args:
        model_names (list[str]): Model class names (typically PascalCase), e.g.
            `["Post", "UserAPI"]`.

    Returns:
        list[str]: Snake_case names in the same order, e.g.
            `["post", "user_api"]`.

    Examples:
        >>> model_model_names_to_snake_case_names(["Post", "Comment"])
        ['post', 'comment']
        >>> model_model_names_to_snake_case_names(["RecipeCommentImage", "UserAPI"])
        ['recipe_comment_image', 'user_api']
        >>> model_model_names_to_snake_case_names([])
        []
    """
    return [camel_to_snake(model) for model in model_names]

def _finalize_child_model_name_for_routing(
        parent_models: list[str],
        remaining_segments: list[str],
        joiner: str) -> str:
    """
    Finalize `(parent_models, child_model)` for route-based hierarchy parsing.

    Rules:
    1. If `remaining_segments` exist, keep `parent_models` as-is and join the
       remaining segments into `child_model` using `joiner`.
    2. If `remaining_segments` are empty but `parent_models` is non-empty,
       promote the last parent model to `child_model` and return the rest as
       parents.
    3. If both are empty, return an empty child model.

    Args:
        parent_models (list[str]): Contiguous matched model segments.
        remaining_segments (list[str]): Unmatched tail segments.
        joiner (str): Separator used when combining tail segments (for example,
            `"_"` for route segments).

    Returns:
        tuple[list[str], str]: Finalized `(parent_models, child_model)`.

    Examples:
        >>> _finalize_child_model_name_for_routing(["posts"], ["shop", "images"], "_")
        (['posts'], 'shop_images')
        >>> _finalize_child_model_name_for_routing(["posts"], [], "_")
        ([], 'posts')
        >>> _finalize_child_model_name_for_routing([], [], "_")
        ([], '')
    """
    if remaining_segments:
        return parent_models, joiner.join(remaining_segments)
    if parent_models:
        return parent_models[:-1], parent_models[-1]
    return parent_models, ""

def _find_longest_running_model_segment_match_from_index(
        segments: list[str],
        registered_models: list[str],
        starting_index: int) -> tuple[str | None, int]:
    """
    Find the longest registered model name formed by concatenating segments
    starting at `starting_index`.

    The function incrementally joins `segments[starting_index:]` without a
    separator and tracks the longest value present in `registered_models`.

    Args:
        segments (list[str]): PascalCase-like segments to scan.
        registered_models (list[str]): Registered model class names.
        starting_index (int): Index at which matching begins.

    Returns:
        tuple[str | None, int]:
            - matched model name, or `None` when no match exists.
            - number of consumed segments for that match (0 when no match).

    Examples:
        >>> _find_longest_running_model_segment_match_from_index(
        ...     ["Admin", "User", "Profile", "Avatar"],
        ...     ["User", "UserProfile"],
        ...     1
        ... )
        ('UserProfile', 2)
        >>> _find_longest_running_model_segment_match_from_index(
        ...     ["Admin", "User"], ["Post"], 0
        ... )
        (None, 0)
    """
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
    """
    Generate nested model candidate names from a controller name hierarchy.

    Behavior is derived from `model_generate_hierarchy_from_controller_name`:
    - If `child_model_name` exists, return `[child_model_name]`.
    - If no child exists and no parent models were matched, return `namespace`.
    - If no child exists and parent models were matched, return `[]`.

    Args:
        controller_name (str): Controller class name.

    Returns:
        list[str]: Nested model name candidates.

    Examples:
        # Registered models: none
        >>> _generate_nested_model_names_from_controller_name("PostCommentImageController")
        ['Post', 'Comment', 'Image']

        # Registered models: User
        >>> _generate_nested_model_names_from_controller_name("AdminUserAvatarController")
        ['Avatar']

        # Registered models: User, Profile
        >>> _generate_nested_model_names_from_controller_name("AdminUserProfileController")
        []

        # Registered models: User
        >>> _generate_nested_model_names_from_controller_name("AdminUserProfileAvatarController")
        ['ProfileAvatar']
    """
    namespace, parent_models, child_model_name = \
        model_generate_hierarchy_from_controller_name(controller_name)
    if child_model_name == "":
        if parent_models == []:
            return namespace
        return []
    return [child_model_name]

def _generate_nested_model_names_from_model_name(model_name: str) -> list[str]:
    """
    Generate nested model candidate names from a model name hierarchy.

    Behavior is derived from `model_generate_hierarchy_from_model_name`:
    - If `child_model_name` exists, return `[child_model_name]`.
    - If no child exists and no parent models were matched, return `namespace`.
    - If no child exists and parent models were matched, return `[]`.

    Args:
        model_name (str): Model class name.

    Returns:
        list[str]: Nested model name candidates.

    Examples:
        # Registered models: none
        >>> _generate_nested_model_names_from_model_name("PostCommentImages")
        ['Post', 'Comment', 'Images']

        # Registered models: User
        >>> _generate_nested_model_names_from_model_name("AdminUserAvatar")
        ['Avatar']

        # Registered models: User, Profile
        >>> _generate_nested_model_names_from_model_name("AdminUserProfile")
        []

        # Registered models: User
        >>> _generate_nested_model_names_from_model_name("AdminUserProfileAvatar")
        ['ProfileAvatar']
    """
    namespace, parent_models, child_model_name = \
        model_generate_hierarchy_from_model_name(model_name)
    if child_model_name == "":
        if parent_models == []:
            return namespace
        return []
    return [child_model_name]

def _generate_non_nested_model_name_from_controller_name(controller_name: str) -> str:
    """
    Generate a single non-nested model candidate from a controller name.

    Steps:
    1. Remove a trailing `Controller` suffix when present.
    2. Split the remaining name with `split_pascal_case`.
    3. Singularize only the final segment.
    4. Join segments back into PascalCase.

    Args:
        controller_name (str): Controller class name.

    Returns:
        str: Non-nested model candidate, or `""` when no PascalCase segments
        can be parsed.

    Examples:
        >>> _generate_non_nested_model_name_from_controller_name("PostController")
        'Post'
        >>> _generate_non_nested_model_name_from_controller_name("PostsController")
        'Post'
        >>> _generate_non_nested_model_name_from_controller_name("AdminUserProfilesController")
        'AdminUserProfile'
         >>> _generate_non_nested_model_name_from_controller_name("Controller")
        ''
    """
    name_without_suffix = controller_name
    if controller_name.endswith("Controller"):
        name_without_suffix = controller_name[:-len("Controller")]
    model_segments = split_pascal_case(name_without_suffix)
    if not model_segments:
        return ""

    model_segments[-1] = singularize(model_segments[-1]).title()
    return "".join(model_segments)

def _generate_non_nested_model_name_from_model_name(model_name: str) ->str:
    """
    Generate a single non-nested model candidate from a model name.

    Steps:
    1. Split `model_name` with `split_pascal_case`.
    2. Singularize only the final segment.
    3. Join segments back into PascalCase.

    Args:
        model_name (str): Model class name.

    Returns:
        str: Non-nested model candidate, or `""` when no PascalCase segments
        can be parsed.

    Examples:
        >>> _generate_non_nested_model_name_from_model_name("Post")
        'Post'
        >>> _generate_non_nested_model_name_from_model_name("Posts")
        'Post'
        >>> _generate_non_nested_model_name_from_model_name("AdminUserProfiles")
        'AdminUserProfile'
        >>> _generate_non_nested_model_name_from_model_name("")
        ''
    """
    model_segments = split_pascal_case(model_name)
    if not model_segments:
        return ""

    model_segments[-1] = singularize(model_segments[-1]).title()
    return "".join(model_segments)

def _split_hierarchy_from_segments(segments: list[str]) -> tuple[list[str], list[str], str]:
    """
    Split PascalCase segments into `namespace`, `parent_models`, and `child_model_name`.

    Resolution uses registered models from `model_get_registered_models()` and
    longest-running segment matches:

    1. Consume leading non-matching segments as `namespace`.
    2. Consume the next contiguous run of model matches as `parent_models`,
       preferring the longest match at each step.
    3. Join the remaining segments into `child_model_name`.

    Args:
        segments (list[str]): Parsed PascalCase segments.

    Returns:
        tuple[list[str], list[str], str]:
            `(namespace, parent_models, child_model_name)`.

    Examples:
        # Registered models: none
        >>> _split_hierarchy_from_segments(["Post", "Comment", "Images"])
        (['Post', 'Comment', 'Images'], [], '')

        # Registered models: User
        >>> _split_hierarchy_from_segments(["Admin", "User", "Avatar"])
        (['Admin'], ['User'], 'Avatar')

        # Registered models: User, Profile
        >>> _split_hierarchy_from_segments(["Admin", "User", "Profile"])
        (['Admin'], ['User', 'Profile'], '')

        # Registered models: User, UserProfile
        >>> _split_hierarchy_from_segments(["Admin", "User", "Profile", "Avatar"])
        (['Admin'], ['UserProfile'], 'Avatar')
    """
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

    # 2) Detect contiguous chain of models from current index
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
