import os
import re
import pytest
import builtins
from pathlib import Path
from flask_commands.utils.controllers import (
    controller_add_method,
    controller_generate_controller_name_from_relative_path,
    controller_generate_relative_path_from_controller_name,
    controller_make_file
)

@pytest.fixture
def controller_project(tmp_path, monkeypatch):
    """This is a fixture that creates the directory structure, sets the working
    directory, and returns a make_controller function"""
    project_root = tmp_path
    controller_dir = project_root / "app" / "controllers"
    controller_dir.mkdir(parents=True)
    controller_init_file = controller_dir / "__init__.py"
    controller_init_file.write_text("\n", encoding="utf-8")

    model_directory = project_root / "app" / "models"
    model_directory.mkdir()
    model_init_file = model_directory / "__init__.py"
    model_init_file.write_text("from .users import User\n", encoding="utf-8")


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
    is_successful, message = controller_add_method(
        relative_path="posts",
        action="index",
        controller_name="PostController"
    )

    # Assert
    assert is_successful is False
    assert "Method Already Exists" in message

    # File should be unchanged
    assert controller_file.read_text(encoding="utf-8") == original_source

def test_controller_add_method_no_controller_class(controller_project):
    controller_file = controller_project(
        "post_controller.py",
        "class CommentController:\n"
        "    pass"
    )

    is_successful, message = controller_add_method(
        relative_path="posts",
        action="index",
        controller_name="PostController"
    )

    assert is_successful is False
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
    is_successful, message = controller_add_method(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        route_name="/posts"
    )

    # Assert
    assert is_successful is True
    assert "Method Added" in message

    updated_source = controller_file.read_text(encoding="utf-8")

    assert "@staticmethod" in updated_source
    assert "def index()" in updated_source
    assert "return render_template('posts/index.html')" in updated_source

def test_controller_add_method_success_with_relation(controller_project):
    """The fixture runs and controller_project is the return from fixture"""
    controller_file = controller_project(
        "user_post_controller.py",
        "from flask import render_template\n"
        "\n"
        "class UserPostController:\n"
        "    @staticmethod\n"
        "    def index(user_id: int):\n"
        "        return render_template('users/posts/index.html')\n"
    )

    # Act
    is_successful, message = controller_add_method(
        relative_path="users/posts",
        action="show",
        controller_name="UserPostController",
        route_name="/users/<int:user_id>/posts/<int:post_id>"
    )

    # Assert
    assert is_successful is True
    assert "Method Added" in message

    updated_source = controller_file.read_text(encoding="utf-8")

    assert "@staticmethod" in updated_source
    assert "def show(user_id: int, post_id: int)" in updated_source
    assert "return render_template('users/posts/index.html')" in updated_source

def test_controller_add_method_exception(controller_project, monkeypatch):
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

    real_open = builtins.open

    # Patch open() so that ONLY write mode fails
    def boom_open(*args, **kwargs):
        if len(args) >= 2 and "w" in args[1]:
            raise RuntimeError("kaboom")
        return real_open(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", boom_open)

    # Act
    is_successful, message = controller_add_method(
        relative_path="posts",
        action="index",
        controller_name="PostController"
    )

    assert is_successful is False
    assert "Failed to add Controller Method" in message

def test_controller_generate_controller_name_from_relative_path():
    assert controller_generate_controller_name_from_relative_path('posts') == 'PostController'
    assert controller_generate_controller_name_from_relative_path('admin/posts') == 'AdminPostController'
    assert controller_generate_controller_name_from_relative_path('posts/comments') == 'PostCommentController'
    assert controller_generate_controller_name_from_relative_path('admin/users/user_profiles') == 'AdminUserUserProfileController'

def test_controller_generate_relative_path_from_controller_name():
    assert controller_generate_relative_path_from_controller_name("PostController") == 'posts'
    assert controller_generate_relative_path_from_controller_name("PostCommentController") == 'posts/comments'
    assert controller_generate_relative_path_from_controller_name("PostCommentImageController") == 'posts/comments/images'
    assert controller_generate_relative_path_from_controller_name("UserAPIController") == 'users/apis'


def test_controller_make_file_success(controller_project):

    is_successful, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="PostController"
    )

    assert is_successful is True
    assert "Created Controller" in message

def test_controller_make_file_success_with_route_name(controller_project):
    is_successful, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        route_name="/posts"
    )

    assert is_successful is True
    assert "Created Controller" in message

def test_controller_make_file_file_already_exists(controller_project):
    # Arrange
    # Create an existing controller file
    controller_project(
        "post_controller.py",
        "class PostController:\n    pass\n"
    )

    # Act
    is_successful, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="PostController"
    )

    # Assert
    assert is_successful is False
    assert "Controller Already Exists" in message
    assert "PostController" in message

    # And make sure the file was NOT modified
    controller_path = os.path.join("app", "controllers", "post_controller.py")
    with open(controller_path, "r", encoding="utf-8") as f:
        contents = f.read()

    assert contents == "class PostController:\n    pass\n"

def test_controller_make_file_file_write_file_exception(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("disk exploded")

    # Patch file_write_file to fail
    monkeypatch.setattr(
        "flask_commands.utils.controllers.file_write_file",
        boom
    )

    # Prevent open() from failing earlier
    controller_dir = tmp_path / "app" / "controllers"
    controller_dir.mkdir(parents=True)
    controller_file = controller_dir / "post_controller.py"
    controller_file.write_text("\n")

    monkeypatch.chdir(tmp_path)

    is_successful, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="Post" #TODO: i think this should be PostController
    )

    assert is_successful is False
    assert "Failed to create controller" in message

def test_controller_make_file_init_missing(tmp_path, monkeypatch):
    project_root = tmp_path
    controller_dir = project_root / "app" / "controllers"
    controller_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)

    is_successful, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="PostController"
    )

    assert is_successful is False
    assert "Controller __init__.py Missing" in message
    assert "You may need to register the controller manually" in message

def test_controller_make_file_init_exception(controller_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("permission denied")

    monkeypatch.setattr(
        "flask_commands.utils.controllers.file_append_file",
        boom
    )

    is_successful, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="Post"
    )

    assert is_successful is False
    assert "Failed to update __init__.py" in message

def test_controller_make_file_method_name_no_relative_view_file_path():
    is_successful, message = controller_make_file(
        relative_path="posts",
        action=None,
        controller_name="PostController"
    )
    assert is_successful is False
    assert "action required when relative_path present" in message

def test_controller_make_file_relative_view_file_path_no_method_name():
    is_successful, message = controller_make_file(
        relative_path=None,
        action="index",
        controller_name="PostController"
    )
    assert is_successful is False
    assert "relative_path required when action present" in message

def test_controller_make_file_with_a_post(tmp_path, controller_project):
    is_successful, message = controller_make_file(
        relative_path="posts",
        action="store",
        controller_name="PostController"
    )

    assert is_successful is True
    assert "Created Controller" in message

    post_controller_file_path = tmp_path / "app" / "controllers" / "post_controller.py"
    assert post_controller_file_path.exists()
    expected_content = (
        "from flask import redirect, url_for\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def store() -> str:\n"
        "        return redirect(url_for('posts.index'))\n"
    )
    content = post_controller_file_path.read_text(encoding="utf-8")
    assert content == expected_content
