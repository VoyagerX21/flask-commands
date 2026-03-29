import os
import pytest
from pathlib import Path
from flask_commands.utils.data_types import ScaffoldStatus
from flask_commands.utils.models import (
    model_generate_hierarchy_from_controller_name,
    model_generate_hierarchy_from_model_name,
    model_generate_model_name_from_dotted_path_with_action,
    model_generate_model_name_from_model_name,
    model_get_registered_models,
    model_generate_model_name_from_controller_name,
    model_make_file,
    model_model_names_to_snake_case_names,
    model_generate_hierarchy_from_dotted_path_with_action,
    _find_longest_running_model_segment_match_from_index
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

def test_model_generate_hierarchy_from_controller_name_suffix_only_returns_empty(model_project):
    namespace, parents, child = model_generate_hierarchy_from_controller_name("Controller")

    assert namespace == []
    assert parents == []
    assert child == ""

def test_model_generate_hierarchy_from_controller_name_no_registered_models(model_project):
    namespace, parents, child = model_generate_hierarchy_from_controller_name("PostCommentImagesController")

    assert namespace == ["Post", "Comment", "Images"]
    assert parents == []
    assert child == ""

def test_model_generate_hierarchy_from_controller_name_namespace_parent_child(model_project):
    (model_project / "app" / "models" / "__init__.py")\
        .write_text("from .user import User\n")

    namespace, parents, child = model_generate_hierarchy_from_controller_name("AdminUserAvatarController")

    assert namespace == ["Admin"]
    assert parents == ["User"]
    assert child == "Avatar"

def test_model_generate_hierarchy_from_controller_name_contiguous_parent_models(model_project):
    (model_project / "app" / "models" / "__init__.py")\
        .write_text(
            "from .user import User\n"
            "from .profile import Profile\n")

    namespace, parents, child = model_generate_hierarchy_from_controller_name("AdminUserProfileController")

    assert namespace == ["Admin"]
    assert parents == ["User", "Profile"]
    assert child == ""

def test_model_generate_hierarchy_from_controller_name_prefers_longest_model_match(model_project):
    (model_project / "app" / "models" / "__init__.py")\
        .write_text(
            "from .user import User\n"
            "from .user_profile import UserProfile\n")

    namespace, parents, child = model_generate_hierarchy_from_controller_name("AdminUserProfileAvatarController")

    assert namespace == ["Admin"]
    assert parents == ["UserProfile"]
    assert child == "Avatar"

def test_model_generate_hierarchy_from_controller_name_remaining_segments_become_child(model_project):
    (model_project / "app" / "models" / "__init__.py")\
        .write_text("from .user import User\n")

    namespace, parents, child = model_generate_hierarchy_from_controller_name("AdminUserProfileAvatarController")

    assert namespace == ["Admin"]
    assert parents == ["User"]
    assert child == "ProfileAvatar"

def test_model_generate_hierarchy_from_controller_name_without_controller_suffix(model_project):
    (model_project / "app" / "models" / "__init__.py")\
        .write_text("from .user import User\n")

    namespace, parents, child = model_generate_hierarchy_from_controller_name("AdminUserProfileAvatar")

    assert namespace == ["Admin"]
    assert parents == ["User"]
    assert child == "ProfileAvatar"

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

def test_model_generate_hierarchy_from_model_name_empty_returns_empty(model_project):
    namespace, parents, child = model_generate_hierarchy_from_model_name("")

    assert namespace == []
    assert parents == []
    assert child == ""

def test_model_generate_hierarchy_from_model_name_no_registered_models(model_project):
    namespace, parents, child = model_generate_hierarchy_from_model_name("PostCommentImages")

    assert namespace == ["Post", "Comment", "Images"]
    assert parents == []
    assert child == ""

def test_model_generate_hierarchy_from_model_name_namespace_parent_child(model_project):
    (model_project / "app" / "models" / "__init__.py")\
        .write_text("from .user import User\n")

    namespace, parents, child = model_generate_hierarchy_from_model_name("AdminUserAvatar")

    assert namespace == ["Admin"]
    assert parents == ["User"]
    assert child == "Avatar"

def test_model_generate_hierarchy_from_model_name_contiguous_parent_models(model_project):
    (model_project / "app" / "models" / "__init__.py")\
        .write_text(
            "from .user import User\n"
            "from .profile import Profile\n")

    namespace, parents, child = model_generate_hierarchy_from_model_name("AdminUserProfile")

    assert namespace == ["Admin"]
    assert parents == ["User", "Profile"]
    assert child == ""

def test_model_generate_hierarchy_from_model_name_prefers_longest_model_match(model_project):
    (model_project / "app" / "models" / "__init__.py")\
        .write_text(
            "from .user import User\n"
            "from .user_profile import UserProfile\n")

    namespace, parents, child = model_generate_hierarchy_from_model_name("AdminUserProfileAvatar")

    assert namespace == ["Admin"]
    assert parents == ["UserProfile"]
    assert child == "Avatar"

def test_model_generate_hierarchy_from_model_name_remaining_segments_become_child(model_project):
    (model_project / "app" / "models" / "__init__.py")\
        .write_text("from .user import User\n")

    namespace, parents, child = model_generate_hierarchy_from_model_name("AdminUserProfileAvatar")

    assert namespace == ["Admin"]
    assert parents == ["User"]
    assert child == "ProfileAvatar"

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

def test_model_get_registered_models_deduplicates_and_sorts_with_user_profile(tmp_path, monkeypatch):
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)

    init_file = models_dir / "__init__.py"
    init_file.write_text(
        "from .user_profile import UserProfile\n"
        "from app.models.user_profile import UserProfile\n"
        "from .post import Post\n"
        "from app.models.comment import Comment\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    assert model_get_registered_models() == ["Comment", "Post", "UserProfile"]

def test_model_get_registered_models_uses_imported_symbol_not_alias_name(tmp_path, monkeypatch):
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)

    init_file = models_dir / "__init__.py"
    init_file.write_text(
        "from .post import Post as PostModel\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    assert model_get_registered_models() == ["Post"]

def test_model_get_registered_models_ignores_base_app_models_import(tmp_path, monkeypatch):
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)

    init_file = models_dir / "__init__.py"
    init_file.write_text(
        "from app.models import Post\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    assert model_get_registered_models() == []

def test_model_get_registered_models_ignores_wildcard_import(tmp_path, monkeypatch):
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)

    init_file = models_dir / "__init__.py"
    init_file.write_text(
        "from .post import *\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    assert model_get_registered_models() == []

def test_model_get_registered_models_absolute_submodule_with_mixed_names(tmp_path, monkeypatch):
    models_dir = tmp_path / "app" / "models"
    models_dir.mkdir(parents=True)

    init_file = models_dir / "__init__.py"
    init_file.write_text(
        "from app.models.user_profile import UserProfile, helper\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    assert model_get_registered_models() == ["UserProfile"]

def test_model_generate_model_name_from_controller_name_suffix_only_returns_empty(model_project):
    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_controller_name("Controller")

    assert non_nested_model_name == ""
    assert nested_model_names == []

def test_model_generate_model_name_from_controller_name_no_registered_models(model_project):
    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_controller_name("PostCommentImageController")

    assert non_nested_model_name == "PostCommentImage"
    assert nested_model_names == ["Post", "Comment", "Image"]

def test_model_generate_model_name_from_controller_name_no_registered_models_plural(model_project):
    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_controller_name("PostsController")

    assert non_nested_model_name == "Post"
    assert nested_model_names == ["Posts"]

def test_model_generate_model_name_from_controller_name_namespace_parent_child(model_project):
    (model_project / "app" / "models" / "__init__.py") \
        .write_text("from .user import User\n", encoding="utf-8")

    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_controller_name("AdminUserAvatarController")

    assert non_nested_model_name == "AdminUserAvatar"
    assert nested_model_names == ["Avatar"]

def test_model_generate_model_name_from_controller_name_contiguous_parent_models(model_project):
    (model_project / "app" / "models" / "__init__.py") \
        .write_text(
            "from .user import User\n"
            "from .profile import Profile\n",
            encoding="utf-8",
        )

    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_controller_name("AdminUserProfileController")

    assert non_nested_model_name == "AdminUserProfile"
    assert nested_model_names == []

def test_model_generate_model_name_from_controller_name_prefers_longest_model_match(model_project):
    (model_project / "app" / "models" / "__init__.py") \
        .write_text(
            "from .user import User\n"
            "from .user_profile import UserProfile\n",
            encoding="utf-8",
        )

    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_controller_name("AdminUserProfileAvatarController")

    assert non_nested_model_name == "AdminUserProfileAvatar"
    assert nested_model_names == ["Avatar"]

def test_model_generate_model_name_from_controller_name_remaining_segments_become_child(model_project):
    (model_project / "app" / "models" / "__init__.py") \
        .write_text("from .user import User\n", encoding="utf-8")

    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_controller_name("AdminUserProfileAvatarController")

    assert non_nested_model_name == "AdminUserProfileAvatar"
    assert nested_model_names == ["ProfileAvatar"]

def test_model_generate_model_name_from_controller_name_without_controller_suffix(model_project):
    (model_project / "app" / "models" / "__init__.py") \
        .write_text("from .user import User\n", encoding="utf-8")

    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_controller_name("AdminUserProfileAvatar")

    assert non_nested_model_name == "AdminUserProfileAvatar"
    assert nested_model_names == ["ProfileAvatar"]

def test_model_generate_model_name_from_dotted_path_with_action_with_dot():
    model_name = model_generate_model_name_from_dotted_path_with_action("posts.index")
    assert model_name == "Post"

def test_model_generate_model_name_from_dotted_path_with_action_without_dot():
    model_name = model_generate_model_name_from_dotted_path_with_action("posts")
    assert model_name == "Post"

def test_model_generate_model_name_from_dotted_path_with_action_with_namespace():
    model_name = model_generate_model_name_from_dotted_path_with_action("admin.posts.show")
    assert model_name == "Post"

def test_model_generate_model_name_from_dotted_path_with_action_action_only():
    model_name = model_generate_model_name_from_dotted_path_with_action("index")
    assert model_name == "Index"

def test_model_generate_model_name_from_dotted_path_with_action_with_underscore_resource():
    model_name = model_generate_model_name_from_dotted_path_with_action("user_profiles.index")
    assert model_name == "UserProfile"

def test_model_generate_model_name_from_dotted_path_with_action_namespace_and_underscore_resource():
    model_name = model_generate_model_name_from_dotted_path_with_action("admin.user_profiles.show")
    assert model_name == "UserProfile"

def test_model_generate_model_name_from_dotted_path_with_action_singularizes_ies():
    model_name = model_generate_model_name_from_dotted_path_with_action("categories.index")
    assert model_name == "Category"

def test_model_generate_model_name_from_dotted_path_with_action_singularizes_ses():
    model_name = model_generate_model_name_from_dotted_path_with_action("classes.index")
    assert model_name == "Class"

def test_model_generate_model_name_from_dotted_path_with_action_compound_snake_case():
    model_name = model_generate_model_name_from_dotted_path_with_action("post_comments.index")
    assert model_name == "PostComment"

def test_model_generate_model_name_from_dotted_path_with_action_without_dot_and_underscore():
    model_name = model_generate_model_name_from_dotted_path_with_action("user_profiles")
    assert model_name == "UserProfile"

def test_model_generate_model_name_from_model_name_empty_returns_empty(model_project):
    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_model_name("")

    assert non_nested_model_name == ""
    assert nested_model_names == []

def test_model_generate_model_name_from_model_name_no_registered_models(model_project):
    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_model_name("PostCommentImages")

    assert non_nested_model_name == "PostCommentImage"
    assert nested_model_names == ["Post", "Comment", "Images"]

def test_model_generate_model_name_from_model_name_no_registered_models_plural(model_project):
    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_model_name("Posts")

    assert non_nested_model_name == "Post"
    assert nested_model_names == ["Posts"]

def test_model_generate_model_name_from_model_name_namespace_parent_child(model_project):
    (model_project / "app" / "models" / "__init__.py") \
        .write_text("from .user import User\n")

    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_model_name("AdminUserAvatar")

    assert non_nested_model_name == "AdminUserAvatar"
    assert nested_model_names == ["Avatar"]

def test_model_generate_model_name_from_model_name_contiguous_parent_models(model_project):
    (model_project / "app" / "models" / "__init__.py") \
        .write_text(
            "from .user import User\n"
            "from .profile import Profile\n",
            encoding="utf-8",
        )

    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_model_name("AdminUserProfile")

    assert non_nested_model_name == "AdminUserProfile"
    assert nested_model_names == []

def test_model_generate_model_name_from_model_name_prefers_longest_model_match(model_project):
    (model_project / "app" / "models" / "__init__.py") \
        .write_text(
            "from .user import User\n"
            "from .user_profile import UserProfile\n",
            encoding="utf-8",
        )

    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_model_name("AdminUserProfileAvatar")

    assert non_nested_model_name == "AdminUserProfileAvatar"
    assert nested_model_names == ["Avatar"]

def test_model_generate_model_name_from_model_name_remaining_segments_become_child(model_project):
    (model_project / "app" / "models" / "__init__.py") \
        .write_text("from .user import User\n", encoding="utf-8")

    non_nested_model_name, nested_model_names = \
        model_generate_model_name_from_model_name("AdminUserProfileAvatar")

    assert non_nested_model_name == "AdminUserProfileAvatar"
    assert nested_model_names == ["ProfileAvatar"]

def test_model_make_file_success(model_project):
    created_model, message = model_make_file(model_name="Post")

    model_file = model_project / "app" / "models" / "post.py"
    init_file = model_project / "app" / "models" / "__init__.py"

    assert model_file.exists()
    assert init_file.exists()

    observed_model_content = model_file.read_text(encoding="utf-8")
    observed_init_content = init_file.read_text(encoding="utf-8")
    expected_init_content = (
        "\n"
        "from .post import Post\n"
    )

    assert created_model.is_successful is True
    assert created_model.status == ScaffoldStatus.ADDED
    assert created_model.model_name == "Post"
    assert created_model.model_file_path == "app/models/post.py"
    assert created_model.registration_file_path == "app/models/__init__.py"

    assert "from app import db" in observed_model_content
    assert "class Post(db.Model):" in observed_model_content
    assert "__tablename__ = 'posts'" in observed_model_content
    assert "id = db.Column(db.Integer, primary_key=True)" in observed_model_content
    assert "def store_in_database(self):" in observed_model_content
    assert "def delete_from_database(self):" in observed_model_content
    assert "return f'<Post id:{self.id}>'" in observed_model_content
    assert observed_init_content == expected_init_content

    assert "Created New Model" in message
    assert "Post" in message
    assert "app/models/post.py" in message
    assert "app/models/__init__.py" in message

def test_model_make_file_file_already_exists(model_project):
    model_file = model_project / "app" / "models" / "post.py"
    model_file.write_text("\n", encoding="utf-8")

    created_model, message = model_make_file(model_name="Post")

    init_file = model_project / "app" / "models" / "__init__.py"

    assert created_model.is_successful is False
    assert created_model.status == ScaffoldStatus.EXISTS
    assert created_model.model_name == "Post"
    assert created_model.model_file_path == "app/models/post.py"
    assert created_model.registration_file_path == "app/models/__init__.py"

    assert model_file.read_text(encoding="utf-8") == "\n"
    assert init_file.read_text(encoding="utf-8") == "\n"

    assert "Model Already Exists" in message
    assert "Post" in message

def test_model_make_file_init_missing(tmp_path, monkeypatch):
    project_root = tmp_path
    model_dir = project_root / "app" / "models"
    model_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)

    created_model, message = model_make_file(model_name="Post")

    model_file = project_root / "app" / "models" / "post.py"
    observed_model_content = model_file.read_text(encoding="utf-8")

    assert created_model.is_successful is False
    assert created_model.status == ScaffoldStatus.WARNING
    assert created_model.model_name == "Post"
    assert created_model.model_file_path == "app/models/post.py"
    assert created_model.registration_file_path == "app/models/__init__.py"

    assert "from app import db" in observed_model_content
    assert "class Post(db.Model):" in observed_model_content
    assert "__tablename__ = 'posts'" in observed_model_content
    assert "id = db.Column(db.Integer, primary_key=True)" in observed_model_content
    assert "def store_in_database(self):" in observed_model_content
    assert "def delete_from_database(self):" in observed_model_content
    assert "return f'<Post id:{self.id}>'" in observed_model_content

    assert "Model __init__.py Missing" in message
    assert "Post" in message
    assert "register it manually" in message

def test_model_make_file_file_append_file_exception(model_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("screen failure")

    monkeypatch.setattr(
        "flask_commands.utils.models.file_append_file",
        boom,
    )

    created_model, message = model_make_file(model_name="Post")

    model_file = model_project / "app" / "models" / "post.py"
    init_file = model_project / "app" / "models" / "__init__.py"
    observed_model_content = model_file.read_text(encoding="utf-8")

    assert created_model.is_successful is False
    assert created_model.status == ScaffoldStatus.ERROR
    assert created_model.model_name == "Post"
    assert created_model.model_file_path == "app/models/post.py"
    assert created_model.registration_file_path == "app/models/__init__.py"

    assert "from app import db" in observed_model_content
    assert "class Post(db.Model):" in observed_model_content
    assert "__tablename__ = 'posts'" in observed_model_content
    assert "id = db.Column(db.Integer, primary_key=True)" in observed_model_content
    assert "def store_in_database(self):" in observed_model_content
    assert "def delete_from_database(self):" in observed_model_content
    assert "return f'<Post id:{self.id}>'" in observed_model_content
    assert init_file.read_text(encoding="utf-8") == "\n"

    assert "Failed to update __init__.py" in message
    assert "screen failure" in message

def test_model_make_file_file_write_file_exception(model_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("screen failure")

    monkeypatch.setattr(
        "flask_commands.utils.models.file_write_file",
        boom,
    )

    created_model, message = model_make_file(model_name="Post")

    init_file = model_project / "app" / "models" / "__init__.py"

    assert created_model.is_successful is False
    assert created_model.status == ScaffoldStatus.ERROR
    assert created_model.model_name == "Post"
    assert created_model.model_file_path == "app/models/post.py"
    assert created_model.registration_file_path == "app/models/__init__.py"

    assert not (model_project / "app" / "models" / "post.py").exists()
    assert init_file.read_text(encoding="utf-8") == "\n"

    assert "Failed to create model" in message
    assert "screen failure" in message

def test_model_make_file_compound_name_uses_snake_case_file_import_and_table(model_project):
    created_model, message = model_make_file(model_name="UserProfile")

    model_file = model_project / "app" / "models" / "user_profile.py"
    init_file = model_project / "app" / "models" / "__init__.py"

    observed_model_content = model_file.read_text(encoding="utf-8")
    observed_init_content = init_file.read_text(encoding="utf-8")
    expected_init_content = (
        "\n"
        "from .user_profile import UserProfile\n"
    )

    assert created_model.is_successful is True
    assert created_model.status == ScaffoldStatus.ADDED
    assert created_model.model_name == "UserProfile"
    assert created_model.model_file_path == "app/models/user_profile.py"
    assert created_model.registration_file_path == "app/models/__init__.py"

    assert "from app import db" in observed_model_content
    assert "class UserProfile(db.Model):" in observed_model_content
    assert "__tablename__ = 'user_profiles'" in observed_model_content
    assert "id = db.Column(db.Integer, primary_key=True)" in observed_model_content
    assert "def store_in_database(self):" in observed_model_content
    assert "def delete_from_database(self):" in observed_model_content
    assert "return f'<UserProfile id:{self.id}>'" in observed_model_content
    assert observed_init_content == expected_init_content

    assert "Created New Model" in message
    assert "UserProfile" in message
    assert "app/models/user_profile.py" in message
    assert "app/models/__init__.py" in message

def test_model_make_file_acronym_name_uses_camel_to_snake(model_project):
    created_model, message = model_make_file(model_name="UserAPI")

    model_file = model_project / "app" / "models" / "user_api.py"
    init_file = model_project / "app" / "models" / "__init__.py"

    observed_model_content = model_file.read_text(encoding="utf-8")
    observed_init_content = init_file.read_text(encoding="utf-8")
    expected_init_content = (
        "\n"
        "from .user_api import UserAPI\n"
    )

    assert created_model.is_successful is True
    assert created_model.status == ScaffoldStatus.ADDED
    assert created_model.model_name == "UserAPI"
    assert created_model.model_file_path == "app/models/user_api.py"
    assert created_model.registration_file_path == "app/models/__init__.py"

    assert "from app import db" in observed_model_content
    assert "class UserAPI(db.Model):" in observed_model_content
    assert "__tablename__ = 'user_apis'" in observed_model_content
    assert "id = db.Column(db.Integer, primary_key=True)" in observed_model_content
    assert "def store_in_database(self):" in observed_model_content
    assert "def delete_from_database(self):" in observed_model_content
    assert "return f'<UserAPI id:{self.id}>'" in observed_model_content
    assert observed_init_content == expected_init_content

    assert "Created New Model" in message
    assert "UserAPI" in message
    assert "app/models/user_api.py" in message
    assert "app/models/__init__.py" in message

def test_model_make_file_compound_name_file_already_exists(model_project):
    model_file = model_project / "app" / "models" / "user_profile.py"
    model_file.write_text("\n", encoding="utf-8")

    created_model, message = model_make_file(model_name="UserProfile")

    init_file = model_project / "app" / "models" / "__init__.py"

    assert created_model.is_successful is False
    assert created_model.status == ScaffoldStatus.EXISTS
    assert created_model.model_name == "UserProfile"
    assert created_model.model_file_path == "app/models/user_profile.py"
    assert created_model.registration_file_path == "app/models/__init__.py"

    assert model_file.read_text(encoding="utf-8") == "\n"
    assert init_file.read_text(encoding="utf-8") == "\n"

    assert "Model Already Exists" in message
    assert "UserProfile" in message

def test_model_make_file_init_missing_still_creates_compound_model_file(tmp_path, monkeypatch):
    project_root = tmp_path
    model_dir = project_root / "app" / "models"
    model_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)

    created_model, message = model_make_file(model_name="UserProfile")

    model_file = project_root / "app" / "models" / "user_profile.py"
    observed_model_content = model_file.read_text(encoding="utf-8")

    assert created_model.is_successful is False
    assert created_model.status == ScaffoldStatus.WARNING
    assert created_model.model_name == "UserProfile"
    assert created_model.model_file_path == "app/models/user_profile.py"
    assert created_model.registration_file_path == "app/models/__init__.py"

    assert "from app import db" in observed_model_content
    assert "class UserProfile(db.Model):" in observed_model_content
    assert "__tablename__ = 'user_profiles'" in observed_model_content
    assert "id = db.Column(db.Integer, primary_key=True)" in observed_model_content
    assert "def store_in_database(self):" in observed_model_content
    assert "def delete_from_database(self):" in observed_model_content
    assert "return f'<UserProfile id:{self.id}>'" in observed_model_content

    assert "Model __init__.py Missing" in message
    assert "UserProfile" in message
    assert "register it manually" in message

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

def test_model_model_names_to_snake_case_names_acronym_run():
    assert model_model_names_to_snake_case_names(["HTTPResponse"]) == ["http_response"]

def test_model_model_names_to_snake_case_names_single_letter_prefix():
    assert model_model_names_to_snake_case_names(["XCoordinate"]) == ["x_coordinate"]

def test_model_model_names_to_snake_case_names_with_numbers():
    assert model_model_names_to_snake_case_names(["Version2API"]) == ["version2_api"]
    assert model_model_names_to_snake_case_names(["User2FASetting"]) == ["user2_fa_setting"]

def test_model_model_names_to_snake_case_names_mixed_inputs():
    assert model_model_names_to_snake_case_names(
        ["UserProfile", "HTTPResponse", "XCoordinate", "User2FASetting"]
    ) == ["user_profile", "http_response", "x_coordinate", "user2_fa_setting"]

def test_model_model_names_to_snake_case_names_already_snake_case_input():
    assert model_model_names_to_snake_case_names(["user_profile"]) == ["user_profile"]

def test__find_longest_running_model_segment_match_from_index_index_to_large():
    match, match_length = \
        _find_longest_running_model_segment_match_from_index(
            ["Admin", "User", "Profile", "Avatar"], ["User", "UserProfile"], 5)

    assert match is None
    assert match_length == 0
