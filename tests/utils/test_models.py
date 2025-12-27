import os
import pytest
from pathlib import Path
from flask_commands.utils.models import (
    generate_table_name_from_model_name,
    model_infer_name_from,
    model_make_file
)

@pytest.fixture
def model_project(tmp_path, monkeypatch):
    project_root = tmp_path
    model_dir = project_root / "app" / "models"
    model_dir.mkdir(parents=True)

    # __init__.py must exist for append_file
    init_file = model_dir / "__init__.py"
    init_file.write_text("", encoding="utf-8")

    monkeypatch.chdir(project_root)

    return project_root

def test_generate_table_name_from_model_name():
    assert generate_table_name_from_model_name('Post') == "posts"
    assert generate_table_name_from_model_name('Category') == "categories"
    assert generate_table_name_from_model_name('Class') == "classes"

def test_model_infer_name_from_reative_path():
    message, model_name = model_infer_name_from("posts", "posts.index")
    assert "Infered the model name" in message
    assert model_name == "Post"

def test_model_infer_name_from_dotted_path_with_name():
    message, model_name = model_infer_name_from("", "posts")
    assert "Infered the model name" in message
    assert model_name == "Post"

def test_model_make_file_success(model_project):
    is_successfull, message = model_make_file(
        model_name="Post",
        model_init_path=os.path.join("app", "models", "__init__.py"),
        model_file_path=os.path.join("app", "models", "post.py"),
    )

    # --- Return value assertions ---
    assert is_successfull is True
    assert "Model Created Successfully" in message

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
    model_file.write_text("")

    is_successfull, message = model_make_file(
        model_name="Post",
        model_init_path=os.path.join("app", "models", "__init__.py"),
        model_file_path=os.path.join("app", "models", "post.py"),
    )

    assert is_successfull is False
    assert "Model Already Exists" in message

def test_model_make_file_write_file_exception(model_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("screen failure")

    # Patch write_file to fail
    monkeypatch.setattr(
        "flask_commands.utils.models.write_file",
        boom
    )

    is_successfull, message = model_make_file(
        model_name="Post",
        model_init_path=os.path.join("app", "models", "__init__.py"),
        model_file_path=os.path.join("app", "models", "post.py"),
    )

    assert is_successfull is False
    assert "Failed to create model" in message

def test_model_make_file_init_missing(tmp_path, monkeypatch):
    project_root = tmp_path
    model_dir = project_root / "app" / "models"
    model_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)

    is_successfull, message = model_make_file(
        model_name="Post",
        model_init_path=os.path.join("app", "models", "__init__.py"),
        model_file_path=os.path.join("app", "models", "post.py"),
    )

    assert is_successfull is False
    assert " __init__.py Missing" in message


def test_model_make_file_append_file_exception(model_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("screen failure")

    # Patch write_file to fail
    monkeypatch.setattr(
        "flask_commands.utils.models.append_file",
        boom
    )

    is_successfull, message = model_make_file(
        model_name="Post",
        model_init_path=os.path.join("app", "models", "__init__.py"),
        model_file_path=os.path.join("app", "models", "post.py"),
    )

    assert is_successfull is False
    assert "Failed to update __init__.py" in message
