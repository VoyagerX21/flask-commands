import os
import pytest
from pathlib import Path
from flask_commands.utils.models import (
    model_generate_model_name_from_dotted_path_with_action,
    model_get_registered_models,
    model_generate_model_name_from_controller_name,
    model_make_file,
    model_model_names_to_snake_case_names,
    model_generate_hierarchy_from_dotted_path_with_action
)

@pytest.fixture
def model_project(tmp_path, monkeypatch):
    project_root = tmp_path
    model_dir = project_root / "app" / "models"
    model_dir.mkdir(parents=True)

    # __init__.py must exist for file_append_file
    init_file = model_dir / "__init__.py"
    init_file.write_text("\n", encoding="utf-8")

    monkeypatch.chdir(project_root)

    return project_root

def test_model_get_registered_models_parses_imports(tmp_path, monkeypatch):
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)

    init_file = models_dir / "__init__.py"
    init_file.write_text(
        "from .post import Post\n"
        "from app.models.comment import Comment\n"
        "from .helpers import format_slug\n"
        "from app.models.user import User, admin\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    assert model_get_registered_models() == ["Comment", "Post", "User"]

def test_model_get_registered_models_with_missing_init(tmp_path, monkeypatch):
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)

    monkeypatch.chdir(tmp_path)

    assert model_get_registered_models() == []

def test_model_get_registered_models_returns_empty_on_syntax_error(tmp_path, monkeypatch):
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)

    init_file = models_dir / "__init__.py"
    init_file.write_text("from .post import Post\nthis is not valid python(", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    assert model_get_registered_models() == []

def test_model_get_registered_models_ignores_non_importfrom_nodes(tmp_path, monkeypatch):
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)

    init_file = models_dir / "__init__.py"
    init_file.write_text(
        "import os\n"
        "x = 1\n"
        "from .post import Post\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    assert model_get_registered_models() == ["Post"]

def test_model_get_registered_models_ignores_non_models_absolute_imports(tmp_path, monkeypatch):
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)

    init_file = models_dir / "__init__.py"
    init_file.write_text(
        "from app.controllers.users import UsersController\n"
        "from app.models.post import Post\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    assert model_get_registered_models() == ["Post"]

def test_model_generate_model_name_from_dotted_path_with_action_with_dot():
    model_name = model_generate_model_name_from_dotted_path_with_action("posts.index")
    assert model_name == "Post"

def test_model_generate_model_name_from_dotted_path_with_action_without_dot():
    model_name = model_generate_model_name_from_dotted_path_with_action("posts")
    assert model_name == "Post"

def test_model_generate_model_name_from_controller_name():
    non_nested_model_name, nested_model_name = model_generate_model_name_from_controller_name("PostCommentImageController")
    assert non_nested_model_name, nested_model_name == ("PostCommentImage", "")

def test_model_make_file_success(model_project):
    is_successful, message = model_make_file(
        model_name="Post",
        model_init_path=os.path.join("app", "models", "__init__.py"),
        model_file_path=os.path.join("app", "models", "post.py"),
    )

    # --- Return value assertions ---
    assert is_successful is True
    assert "Created New Model" in message

    # --- File creation assertions ---
    model_file = model_project / "app" / "models" / "post.py"
    init_file = model_project / "app" / "models" / "__init__.py"

    assert model_file.exists()
    assert init_file.exists()

    # --- Content assertions (model file) ---
    model_contents = model_file.read_text(encoding="utf-8")

    assert "class Post(db.Model):" in model_contents
    assert "__tablename__" in model_contents
    assert "def store_in_database" in model_contents
    assert "def delete_from_database" in model_contents

    # --- Content assertions (__init__.py) ---
    init_contents = init_file.read_text(encoding="utf-8")
    assert "from .post import Post" in init_contents

def test_model_make_file_file_already_exists(model_project):
    model_file = model_project / "app" / "models" / "post.py"
    model_file.write_text("\n")

    is_successful, message = model_make_file(
        model_name="Post",
        model_init_path=os.path.join("app", "models", "__init__.py"),
        model_file_path=os.path.join("app", "models", "post.py"),
    )

    assert is_successful is False
    assert "Model Already Exists" in message

def test_model_make_file_file_write_file_exception(model_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("screen failure")

    # Patch file_write_file to fail
    monkeypatch.setattr(
        "flask_commands.utils.models.file_write_file",
        boom
    )

    is_successful, message = model_make_file(
        model_name="Post",
        model_init_path=os.path.join("app", "models", "__init__.py"),
        model_file_path=os.path.join("app", "models", "post.py"),
    )

    assert is_successful is False
    assert "Failed to create model" in message

def test_model_make_file_init_missing(tmp_path, monkeypatch):
    project_root = tmp_path
    model_dir = project_root / "app" / "models"
    model_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)

    is_successful, message = model_make_file(
        model_name="Post",
        model_init_path=os.path.join("app", "models", "__init__.py"),
        model_file_path=os.path.join("app", "models", "post.py"),
    )

    assert is_successful is False
    assert " Model __init__.py Missing" in message

def test_model_make_file_file_append_file_exception(model_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("screen failure")

    # Patch file_write_file to fail
    monkeypatch.setattr(
        "flask_commands.utils.models.file_append_file",
        boom
    )

    is_successful, message = model_make_file(
        model_name="Post",
        model_init_path=os.path.join("app", "models", "__init__.py"),
        model_file_path=os.path.join("app", "models", "post.py"),
    )

    assert is_successful is False
    assert "Failed to update __init__.py" in message

def test_model_model_names_to_snake_case_names_basic():
    assert model_model_names_to_snake_case_names(["Post"]) == ["post"]
    assert model_model_names_to_snake_case_names(["Post", "Comment"]) == ["post", "comment"]

def test_model_model_names_to_snake_case_names_compound():
    assert model_model_names_to_snake_case_names(["RecipeCommentImage"]) == ["recipe_comment_image"]
    assert model_model_names_to_snake_case_names(["UserAPI"]) == ["user_api"]

def test_model_model_names_to_snake_case_names_empty():
    assert model_model_names_to_snake_case_names([]) == []

def test_model_model_names_to_snake_case_names_preserves_order():
    assert model_model_names_to_snake_case_names(["Comment", "Post"]) == ["comment", "post"]

def test_model_generate_hierarchy_from_dotted_path_with_action_simple_resource(tmp_path, monkeypatch):
    dotted_path_with_action = "posts.index"
    init_content = (
        "from .post import Post\n"
    )
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)
    init_file = models_dir / "__init__.py"
    init_file.write_text(init_content, encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    namespace, parents, child = \
        model_generate_hierarchy_from_dotted_path_with_action(dotted_path_with_action)

    assert namespace == []
    assert parents == []
    assert child == "posts"

def test_model_generate_hierarchy_from_dotted_path_with_action_with_namespace(tmp_path, monkeypatch):
    dotted_path_with_action = "admin.posts.show"
    init_content = (
        "from .post import Post\n"
    )
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)
    init_file = models_dir / "__init__.py"
    init_file.write_text(init_content, encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    namespace, parents, child = \
        model_generate_hierarchy_from_dotted_path_with_action(dotted_path_with_action)

    assert namespace == ["admin"]
    assert parents == []
    assert child == "posts"

def test_model_generate_hierarchy_from_dotted_path_with_action_nested_models(tmp_path, monkeypatch):
    dotted_path_with_action = "admin.posts.comments.index"
    init_content = (
        "from .post import Post\n"
        "from .comment import Comment\n"
    )
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)
    init_file = models_dir / "__init__.py"
    init_file.write_text(init_content, encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    namespace, parents, child = \
        model_generate_hierarchy_from_dotted_path_with_action(dotted_path_with_action)

    assert namespace == ["admin"]
    assert parents == ["posts"]
    assert child == "comments"

def test_model_generate_hierarchy_from_dotted_path_with_action_no_dots(tmp_path, monkeypatch):
    dotted_path_with_action = "landinng"
    init_content = (
        "from .post import Post\n"
        "from .comment import Comment\n"
    )
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)
    init_file = models_dir / "__init__.py"
    init_file.write_text(init_content, encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    namespace, parents, child = \
        model_generate_hierarchy_from_dotted_path_with_action(dotted_path_with_action)

    assert namespace == []
    assert parents == []
    assert child == ""

def test_model_generate_hierarchy_from_dotted_path_with_action_remaining_segments(tmp_path, monkeypatch):
    dotted_path_with_action = "admin.posts.shop.images.show"
    init_content = (
        "from .post import Post\n"
    )
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)
    init_file = models_dir / "__init__.py"
    init_file.write_text(init_content, encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    namespace, parents, child = \
        model_generate_hierarchy_from_dotted_path_with_action(dotted_path_with_action)

    assert namespace == ["admin"]
    assert parents == ["posts"]
    assert child == "shop_images"

def test_model_generate_hierarchy_from_dotted_path_with_action_with_underscore(tmp_path, monkeypatch):
    dotted_path_with_action = "admin.users.user_profile.index"
    init_content = (
        "from .user import User\n"
        "from .post import Post\n"
        "from .user_profile import UserProfile\n"
    )
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)
    init_file = models_dir / "__init__.py"
    init_file.write_text(init_content, encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    namespace, parents, child = \
        model_generate_hierarchy_from_dotted_path_with_action(dotted_path_with_action)

    assert namespace == ["admin"]
    assert parents == ["users"]
    assert child == "user_profile"
