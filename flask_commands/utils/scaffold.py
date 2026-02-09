import re
import os
from .naming import singularize

# TODO: THIS NEEDS TO GO AND BE REPLACED WITH LOGIC FROM model_get_registered_models
def check_dotted_path_with_action_for_models(dotted_path_with_action: str) -> list[str]:
    """
    Return path segments that map to registered models.

    Scans a dotted path (e.g. "posts.comments.show") and checks each segment
    against the names listed in `app/models/__init__.py`, returning only those
    segments that correspond to registered models.

    Examples:
        "posts.comments.show" -> ["posts", "comments"]
        "admin.users.index" -> ["users"]
    """
    models = []
    model_init_path = os.path.join("app", "models", "__init__.py")
    try:
        with open(model_init_path, "r", encoding="utf-8") as f:
            model_init_content = f.read()
    except FileNotFoundError:
        return models
    for part_name in dotted_path_with_action.lower().split("."):
        if singularize(part_name) in model_init_content:
            models.append(part_name)
    return models



def crud_mapping_route(action: str, resource: str, child_object: str) -> str:
    """
    Map a CRUD action to a URL pattern for a given resource with child_object name.
    - `action`: one of 'index','create','store','show','edit','update','destroy','delete'
    - `resource`: path-like resource (e.g. 'posts' or 'admin/posts' or 'admin/posts/comments')
    - `child_object`: singular child_object name used in resource variable ideally at the end (e.g. 'post', 'comment')
    """
    mapping = {
        "index":    lambda resource, child_object: f"/{resource}",
        "create":   lambda resource, child_object: f"/{resource}/create",
        "store":    lambda resource, child_object: f"/{resource}",
        "show":     lambda resource, child_object: f"/{resource}/<int:{child_object}_id>",
        "edit":     lambda resource, child_object: f"/{resource}/<int:{child_object}_id>/edit",
        "update":   lambda resource, child_object: f"/{resource}/<int:{child_object}_id>",
        "destroy":  lambda resource, child_object: f"/{resource}/<int:{child_object}_id>/delete",
        "delete":   lambda resource, child_object: f"/{resource}/<int:{child_object}_id>/delete",
    }
    return mapping[action](resource, child_object)

def generate_crud_route(action: str, parent_resources: str, child_resource: str) -> str:
    """
    Map a CRUD action to a URL pattern for a given resource with child_object name.
    - `action`: one of 'index','create','store','show','edit','update','destroy','delete'
    - `resource`: path-like resource (e.g. 'posts' or 'admin/posts' or 'admin/posts/comments')
    - `child_object`: singular child_object name used in resource variable ideally at the end (e.g. 'post', 'comment')
    """

    base = f"/{parent_resources}/{child_resource}" \
        if parent_resources != "" else f"/{child_resource}"
    child_parameter = f"<int:{singularize(child_resource.replace('-', '_'))}_id>"


    mapping = {
        "index":    lambda base, child_parameter: f"{base}",
        "create":   lambda base, child_parameter: f"{base}/create",
        "store":    lambda base, child_parameter: f"{base}",
        "show":     lambda base, child_parameter: f"{base}/{child_parameter}",
        "edit":     lambda base, child_parameter: f"{base}/{child_parameter}/edit",
        "update":   lambda base, child_parameter: f"{base}/{child_parameter}",
        "destroy":  lambda base, child_parameter: f"{base}/{child_parameter}/delete",
        "delete":   lambda base, child_parameter: f"{base}/{child_parameter}/delete",
    }
    return mapping[action](base, child_parameter)

def filter_falsy(items: list[str]) -> list[str]:
    return [item for item in items if item]

def normalize_dotted_path_with_action(dotted_path_with_action: str) -> tuple[bool, str]:
    """
    Normalize a dotted path with action by replacing '-' with '_', collapsing duplicate
    '.' and '_', removing dot-separated segments that are only underscores, and stripping
    leading/trailing '.', '_' or spaces.

    Normalization steps:
    1. Lowercase all characters.
    2. Replace hyphens with underscores.
    3. Collapse repeated dots and underscores to a single character.
    4. Remove dot-separated segments that are only underscores.
    5. Strip leading/trailing dots, underscores, or spaces.

    Raises:
        ValueError: If the input becomes empty after normalization.

    Examples:
        "Admin.Posts-Index" -> "admin.posts_index"
        "  admin..posts__show  " -> "admin.posts_show"
        "___Posts..." -> "posts"
        ".-Admin-.-" -> "admin"
        "  ..__  " -> ValueError
    """
    value = dotted_path_with_action.lower()
    value = value.replace("-", "_")
    value = re.sub(r"\.+", ".", value)
    value = re.sub(r"\_+", "_", value)
    value = re.sub(r"\.\_\.", ".", value)
    value = value.strip("._ ")
    if value == "":
        return False, "💣 Error: Invalid dotted path (empty after normalization)."
    return True, value

def split_dotted_path_with_action_into_relative_path_and_action(
        dotted_path_with_action: str) -> tuple[str, str]:
    """
    Split a dotted path like 'posts.index' -> (relative_path, action).
    Examples:
      'posts.index' -> ('posts', 'index')
      'admin.posts.show' -> ('admin/posts', 'show')
      'index' -> ('', 'index')
      'admin.posts.comments' -> ('admin/posts', 'comments')
    The action is always the last segment; the rest form a relative path.
    """
    parts = dotted_path_with_action.split(".")
    action = parts[-1]
    relative_path = '' if len(parts) == 1 else '/'.join(parts[:-1])
    return relative_path, action
