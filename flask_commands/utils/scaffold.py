import re
import os
from .naming import singularize


def filter_falsy(items: list[str]) -> list[str]:
    return [item for item in items if item]

def generate_restful_route(action: str, parent_resources: str, child_resource: str) -> str:
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

    # UX layer: allow slash input and map it to dotted form.
    # UX layer: allow - or _ for multi word objects map them to _
    value = value.replace("/", ".")
    value = value.replace("-", "_")

    # Canonicalize separators and underscores.
    value = re.sub(r"\.+", ".", value)
    value = re.sub(r"\_+", "_", value)
    value = re.sub(r"\.\_\.", ".", value)
    value = value.strip("._ ")
    if value == "":
        return False, "💣 Error: Invalid dotted path (empty after normalization)."

    # Internal segments should only contain [a-z0-9_].
    segments = value.split(".")
    if any(not re.fullmatch(r"[a-z0-9_]+", segment) for segment in segments):
        return False, "💣 Error: Invalid dotted path (allowed: letters, numbers, underscore)."
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

def split_pascal_case(name: str) -> list[str]:
    """
    Split a PascalCase or CamelCase string into its component words.

    This function is designed for names like:
        "AdminUserProfileImage" -> ["Admin", "User", "Profile", "Image"]
        "HTTPResponse"          -> ["HTTP", "Response"]
        "XCoordinate"           -> ["X", "Coordinate"]

    Regex explanation (in plain English):

    We look for "word-like" chunks that follow PascalCase rules:

    1) Each chunk must start with a capital letter:
           [A-Z]

    2) After the first capital letter, the chunk continues in one of two ways
       this is the (?:`option1`|`option2`) notation:

       a) Normal word:
           [a-z]+
           - one or more lowercase letters
           - e.g. "Admin", "User", "Profile"

       b) Acronym or capital run:
           [A-Z]*
           - zero or more additional capital letters
           - allows acronyms like "HTTP" and single-letter words like "X"

           (?=[A-Z]|$)
           - a lookahead that ensures we stop the acronym when the next character
             is either:
               • another capital letter (start of a new word), or
               • the end of the string

    Together, the regex:
        r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))'

    means:
        "Match a capital letter, followed by either lowercase letters
         or a run of capital letters that ends cleanly before the next word."

    Returns:
        A list of PascalCase components in their original capitalization.
    """
    return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', name)
