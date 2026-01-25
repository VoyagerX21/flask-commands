import os
import pytest
from pathlib import Path
from flask_commands.utils.models import (
    model_infer_name_from_controller,
    model_infer_name_from_dotted_view_path,
    model_make_file
)

@pytest.fixture
def model_project(tmp_path, monkeypatch):
    project_root = tmp_path
    model_dir = project_root / "app" / "models"
    model_dir.mkdir(parents=True)

    # __init__.py must exist for append_file
    init_file = model_dir / "__init__.py"
    init_file.write_text("\n", encoding="utf-8")

    monkeypatch.chdir(project_root)

    return project_root

def test_model_infer_name_from_dotted_view_path_with_dot():
    model_name = model_infer_name_from_dotted_view_path("posts.index")
    assert model_name == "Post"

def test_model_infer_name_from_dotted_view_path_without_dot():
    model_name = model_infer_name_from_dotted_view_path("posts")
    assert model_name == "Post"

def test_model_infer_name_from_controller():
    model_name = model_infer_name_from_controller("PostCommentImageController")
    assert model_name == "Image"

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

def test_model_make_file_write_file_exception(model_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("screen failure")

    # Patch write_file to fail
    monkeypatch.setattr(
        "flask_commands.utils.models.write_file",
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


def test_model_make_file_append_file_exception(model_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("screen failure")

    # Patch write_file to fail
    monkeypatch.setattr(
        "flask_commands.utils.models.append_file",
        boom
    )

    is_successful, message = model_make_file(
        model_name="Post",
        model_init_path=os.path.join("app", "models", "__init__.py"),
        model_file_path=os.path.join("app", "models", "post.py"),
    )

    assert is_successful is False
    assert "Failed to update __init__.py" in message
