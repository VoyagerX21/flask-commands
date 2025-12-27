import os
import pytest
from pathlib import Path
from flask_commands.utils.controllers import (
    controller_add_method,
    controller_infer_name_from,
    controller_make_file
)

@pytest.fixture
def controller_project(tmp_path, monkeypatch):
    """This is a fixture that creates the directory structure, sets the working
    directory, and returns a make_controller function"""
    project_root = tmp_path
    controller_dir = project_root / "app" / "controllers"
    controller_dir.mkdir(parents=True)

    # __init__.py must exist for ...
    init_file = controller_dir / "__init__.py"
    init_file.write_text("", encoding="utf-8")

    monkeypatch.chdir(project_root)

    def make_controller(filename: str, source: str) -> Path:
        controller_file = controller_dir / filename
        controller_file.write_text(source, encoding="utf-8")
        return controller_file

    return make_controller

def test_controller_add_method_already_exists(controller_project):
    controller_file = controller_project(
        "post_controller.py",
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index():\n"
        "        posts = Post.query.all()\n"
        "        return render_template('posts/index.html', posts=posts)\n"
    )

    original_source = controller_file.read_text(encoding="utf-8")

    # Act
    success, message = controller_add_method(
        controller_name="PostController",
        method_name="index",
        relative_view_file_path="posts/index.html"
    )

    # Assert
    assert success is False
    assert "Method Already Exists" in message

    # File should be unchanged
    assert controller_file.read_text(encoding="utf-8") == original_source

def test_controller_no_controller_class(controller_project):
    controller_file = controller_project(
        "post_controller.py",
        "class CommentController:\n"
        "    pass"
    )

    success, message = controller_add_method(
        controller_name="PostController",
        method_name="index",
        relative_view_file_path="posts/index.html"
    )

    assert success is False
    assert "Controller Class Not Found" in message

def test_controller_add_method_success(controller_project):
    """The fixture runs and controller_project is the return from fixture"""
    controller_file = controller_project(
        "post_controller.py",
        "class PostController:\n"
        "\n"
        "    @staticmethod\n"
        "    def create():\n"
        "        pass\n"
        "\n"
        "def helper_function(input):\n"
        "    pass"
    )

    # Act
    success, message = controller_add_method(
        controller_name="PostController",
        method_name="index",
        relative_view_file_path="posts/index.html"
    )

    # Assert
    assert success is True
    assert "Method Added Successfully" in message

    updated_source = controller_file.read_text(encoding="utf-8")

    assert "@staticmethod" in updated_source
    assert "def index()" in updated_source
    assert "return render_template('posts/index.html')" in updated_source

def test_controller_infer_name_from():
    assert controller_infer_name_from('posts') == 'PostController'
    assert controller_infer_name_from('admin/posts') == 'AdminPostController'
    assert controller_infer_name_from('posts/comments') == 'PostCommentController'

def test_controller_make_file_success(controller_project):

    success, message = controller_make_file(
        controller_name="PostController",
        method_name="index",
        relative_view_file_path="posts/index.html"
    )

    assert success == True
    assert "Created controller" in message

def test_controller_make_file_file_already_exists(controller_project):
    # Arrange
    # Create an existing controller file
    controller_project(
        "post_controller.py",
        "class PostController:\n    pass\n"
    )

    # Act
    success, message = controller_make_file(
        controller_name="PostController",
        method_name="index",
        relative_view_file_path="posts/index.html",
    )

    # Assert
    assert success is False
    assert "Controller Already Exists" in message
    assert "PostController" in message

    # And make sure the file was NOT modified
    controller_path = os.path.join("app", "controllers", "post_controller.py")
    with open(controller_path, "r", encoding="utf-8") as f:
        contents = f.read()

    assert contents == "class PostController:\n    pass\n"

def test_controller_make_file_write_file_exception(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("disk exploded")

    # Patch write_file to fail
    monkeypatch.setattr(
        "flask_commands.utils.controllers.write_file",
        boom
    )

    # Prevent open() from failing earlier
    controller_dir = tmp_path / "app" / "controllers"
    controller_dir.mkdir(parents=True)
    controller_file = controller_dir / "post_controller.py"
    controller_file.write_text("")

    monkeypatch.chdir(tmp_path)

    success, message = controller_make_file(
        controller_name="Post",
        method_name="index",
        relative_view_file_path="posts/index.html"
    )

    assert success is False
    assert "Failed to create controller" in message

def test_controller_make_file_init_missing(tmp_path, monkeypatch):
    project_root = tmp_path
    controller_dir = project_root / "app" / "controllers"
    controller_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)

    success, message = controller_make_file(
        controller_name="PostController",
        method_name="index",
        relative_view_file_path="posts/index.html"
    )

    assert success is False
    assert "__init__.py Missing" in message
    assert "You may need to register it manually" in message

def test_controller_make_file_init_exception(controller_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("permission denied")

    monkeypatch.setattr(
        "flask_commands.utils.controllers.append_file",
        boom
    )

    success, message = controller_make_file(
        controller_name="Post",
        method_name="index",
        relative_view_file_path="posts/index.html"
    )

    assert success is False
    assert "Failed to update __init__.py" in message
