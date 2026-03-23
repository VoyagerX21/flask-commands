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
from flask_commands.utils.data_types import ScaffoldStatus

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

    controller_result, message = controller_add_method(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
    )

    updated_source = controller_file.read_text(encoding="utf-8")

    assert controller_result.is_successful is False
    assert controller_result.status == ScaffoldStatus.EXISTS
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.methods_added == []

    assert "Method Already Exists" in message
    assert "PostController" in message
    assert "index" in message
    assert updated_source == original_source

def test_controller_add_method_no_controller_class(controller_project):
    controller_file = controller_project(
        "post_controller.py",
        "class CommentController:\n"
        "    pass\n"
    )

    original_source = controller_file.read_text(encoding="utf-8")

    controller_result, message = controller_add_method(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
    )

    updated_source = controller_file.read_text(encoding="utf-8")

    assert controller_result.is_successful is False
    assert controller_result.status == ScaffoldStatus.WARNING
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.methods_added == []

    assert "Controller Class Not Found" in message
    assert "PostController" in message
    assert "app/controllers/post_controller.py" in message
    assert updated_source == original_source


def test_controller_add_method_success(controller_project):
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

    controller_result, message = controller_add_method(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
        route_name="/posts",
    )

    updated_source = controller_file.read_text(encoding="utf-8")

    expected_source = (
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "\n"
        "    @staticmethod\n"
        "    def create():\n"
        "        pass\n"
        "\n"
        "\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')\n"
        "def helper_function(input):\n"
        "    pass"
    )

    assert controller_result.is_successful is True
    assert controller_result.status == ScaffoldStatus.ADDED
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.methods_added == ["index"]

    assert "Method Added To Controller" in message
    assert "index" in message
    assert "PostController" in message
    assert "app/controllers/post_controller.py" in message
    assert updated_source == expected_source


def test_controller_add_method_success_with_relation(controller_project):
    controller_file = controller_project(
        "user_post_controller.py",
        "from flask import render_template\n"
        "\n"
        "class UserPostController:\n"
        "    @staticmethod\n"
        "    def index(user_id: int):\n"
        "        return render_template('users/posts/index.html')\n"
    )

    controller_result, message = controller_add_method(
        relative_path="users/posts",
        action="show",
        controller_name="UserPostController",
        controller_file_path="app/controllers/user_post_controller.py",
        route_name="/users/<int:user_id>/posts/<int:post_id>",
    )

    updated_source = controller_file.read_text(encoding="utf-8")

    expected_source = (
        "from flask import render_template\n"
        "\n"
        "class UserPostController:\n"
        "    @staticmethod\n"
        "    def index(user_id: int):\n"
        "        return render_template('users/posts/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def show(user_id: int, post_id: int) -> str:\n"
        "        return render_template('users/posts/show.html')"
    )

    assert controller_result.is_successful is True
    assert controller_result.status == ScaffoldStatus.ADDED
    assert controller_result.controller_name == "UserPostController"
    assert controller_result.controller_file_path == "app/controllers/user_post_controller.py"
    assert controller_result.methods_added == ["show"]

    assert "Method Added To Controller" in message
    assert "show" in message
    assert "UserPostController" in message
    assert "app/controllers/user_post_controller.py" in message
    assert updated_source == expected_source


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

    original_source = controller_file.read_text(encoding="utf-8")

    real_open = builtins.open

    def boom_open(*args, **kwargs):
        if len(args) >= 2 and "w" in args[1]:
            raise RuntimeError("kaboom")
        return real_open(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", boom_open)

    controller_result, message = controller_add_method(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
    )

    updated_source = controller_file.read_text(encoding="utf-8")

    assert controller_result.is_successful is False
    assert controller_result.status == ScaffoldStatus.ERROR
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.methods_added == []

    assert "Failed to add Controller Method" in message
    assert "kaboom" in message
    assert updated_source == original_source


def test_controller_add_method_inserts_redirect_imports(controller_project):
    controller_file = controller_project(
        "post_controller.py",
        "class PostController:\n"
        "    pass\n"
    )

    controller_result, message = controller_add_method(
        relative_path="posts",
        action="store",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
        route_name="/posts",
    )

    updated_source = controller_file.read_text(encoding="utf-8")

    expected_source = (
        "from flask import redirect, url_for\n"
        "\n"
        "class PostController:\n"
        "\n"
        "    @staticmethod\n"
        "    def store() -> str:\n"
        "        return redirect(url_for('posts.index'))"
    )

    assert controller_result.is_successful is True
    assert controller_result.status == ScaffoldStatus.ADDED
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.methods_added == ["store"]

    assert "Method Added To Controller" in message
    assert "store" in message
    assert "PostController" in message
    assert "app/controllers/post_controller.py" in message
    assert updated_source == expected_source


def test_controller_add_method_redirect_return_line_uses_nested_param_reference(controller_project):
    controller_file = controller_project(
        "post_comment_controller.py",
        "class PostCommentController:\n"
        "    def helper(self):\n"
        "        pass\n"
    )

    controller_result, message = controller_add_method(
        relative_path="posts/comments",
        action="update",
        controller_name="PostCommentController",
        controller_file_path="app/controllers/post_comment_controller.py",
        route_name="/posts/<int:post_id>/comments/<int:comment_id>",
    )

    updated_source = controller_file.read_text(encoding="utf-8")

    expected_source = (
        "from flask import redirect, url_for\n"
        "\n"
        "class PostCommentController:\n"
        "    def helper(self):\n"
        "        pass\n"
        "\n"
        "    @staticmethod\n"
        "    def update(post_id: int, comment_id: int) -> str:\n"
        "        return redirect(url_for('posts.comments.index', post_id=post_id))"
    )

    assert controller_result.is_successful is True
    assert controller_result.status == ScaffoldStatus.ADDED
    assert controller_result.controller_name == "PostCommentController"
    assert controller_result.controller_file_path == "app/controllers/post_comment_controller.py"
    assert controller_result.methods_added == ["update"]

    assert "Method Added To Controller" in message
    assert "update" in message
    assert "PostCommentController" in message
    assert "app/controllers/post_comment_controller.py" in message
    assert updated_source == expected_source


def test_controller_add_method_removes_pass_only_class_body(controller_project):
    controller_file = controller_project(
        "user_controller.py",
        "class UserController:\n"
        "    pass\n"
    )

    controller_result, message = controller_add_method(
        relative_path="users",
        action="index",
        controller_name="UserController",
        controller_file_path="app/controllers/user_controller.py",
        route_name="/users",
    )

    updated_source = controller_file.read_text(encoding="utf-8")

    expected_source = (
        "from flask import render_template\n"
        "\n"
        "class UserController:\n"
        "\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('users/index.html')"
    )

    assert controller_result.is_successful is True
    assert controller_result.status == ScaffoldStatus.ADDED
    assert controller_result.controller_name == "UserController"
    assert controller_result.controller_file_path == "app/controllers/user_controller.py"
    assert controller_result.methods_added == ["index"]

    assert "Method Added To Controller" in message
    assert "index" in message
    assert "UserController" in message
    assert "app/controllers/user_controller.py" in message
    assert updated_source == expected_source


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
    controller_result, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
    )

    controller_file = Path("app/controllers/post_controller.py")
    controller_init_file = Path("app/controllers/__init__.py")

    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')\n"
    )

    expected_init_content = (
        "\n"
        "from .post_controller import PostController\n"
    )

    assert controller_result.is_successful is True
    assert controller_result.status == ScaffoldStatus.ADDED
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.registration_file_path == "app/controllers/__init__.py"
    assert controller_result.methods_added == ["index"]

    assert controller_file.read_text(encoding="utf-8") == expected_controller_content
    assert controller_init_file.read_text(encoding="utf-8") == expected_init_content

    assert "Created Controller Class With Method" in message
    assert "PostController" in message
    assert "index" in message
    assert "app/controllers/post_controller.py" in message
    assert "app/controllers/__init__.py" in message


def test_controller_make_file_success_with_route_name(controller_project):
    controller_result, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
        route_name="/posts",
    )

    controller_file = Path("app/controllers/post_controller.py")
    controller_init_file = Path("app/controllers/__init__.py")

    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')\n"
    )

    expected_init_content = (
        "\n"
        "from .post_controller import PostController\n"
    )

    assert controller_result.is_successful is True
    assert controller_result.status == ScaffoldStatus.ADDED
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.registration_file_path == "app/controllers/__init__.py"
    assert controller_result.methods_added == ["index"]

    assert controller_file.read_text(encoding="utf-8") == expected_controller_content
    assert controller_init_file.read_text(encoding="utf-8") == expected_init_content

    assert "Created Controller Class With Method" in message
    assert "PostController" in message
    assert "index" in message
    assert "app/controllers/post_controller.py" in message
    assert "app/controllers/__init__.py" in message


def test_controller_make_file_file_already_exists(controller_project):
    controller_project(
        "post_controller.py",
        "class PostController:\n"
        "    pass\n"
    )

    controller_result, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
    )

    controller_file = Path("app/controllers/post_controller.py")
    controller_init_file = Path("app/controllers/__init__.py")

    expected_controller_content = (
        "class PostController:\n"
        "    pass\n"
    )

    expected_init_content = "\n"

    assert controller_result.is_successful is False
    assert controller_result.status == ScaffoldStatus.EXISTS
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.registration_file_path is None
    assert controller_result.methods_added == []

    assert controller_file.read_text(encoding="utf-8") == expected_controller_content
    assert controller_init_file.read_text(encoding="utf-8") == expected_init_content

    assert "Controller Already Exists" in message
    assert "PostController" in message

def test_controller_make_file_file_write_file_exception(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("disk exploded")

    monkeypatch.setattr(
        "flask_commands.utils.controllers.file_write_file",
        boom,
    )
    monkeypatch.chdir(tmp_path)

    controller_result, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
    )

    assert controller_result.is_successful is False
    assert controller_result.status == ScaffoldStatus.ERROR
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.registration_file_path is None
    assert controller_result.methods_added == []

    assert "Failed to create controller" in message
    assert "disk exploded" in message


def test_controller_make_file_init_missing(tmp_path, monkeypatch):
    project_root = tmp_path
    controller_dir = project_root / "app" / "controllers"
    controller_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)

    controller_result, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
    )

    controller_file = Path("app/controllers/post_controller.py")

    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')\n"
    )

    assert controller_result.is_successful is False
    assert controller_result.status == ScaffoldStatus.WARNING
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.registration_file_path == "app/controllers/__init__.py"
    assert controller_result.methods_added == ["index"]

    assert controller_file.read_text(encoding="utf-8") == expected_controller_content

    assert "Controller __init__.py Missing" in message
    assert "PostController" in message
    assert "register the controller manually" in message


def test_controller_make_file_init_exception(controller_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("permission denied")

    monkeypatch.setattr(
        "flask_commands.utils.controllers.file_append_file",
        boom,
    )

    controller_result, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
    )

    controller_file = Path("app/controllers/post_controller.py")
    controller_init_file = Path("app/controllers/__init__.py")

    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')\n"
    )

    expected_init_content = "\n"

    assert controller_result.is_successful is False
    assert controller_result.status == ScaffoldStatus.ERROR
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.registration_file_path == "app/controllers/__init__.py"
    assert controller_result.methods_added == ["index"]

    assert controller_file.read_text(encoding="utf-8") == expected_controller_content
    assert controller_init_file.read_text(encoding="utf-8") == expected_init_content

    assert "Failed to update __init__.py" in message
    assert "permission denied" in message


def test_controller_make_file_init_exception(controller_project, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("permission denied")

    monkeypatch.setattr(
        "flask_commands.utils.controllers.file_append_file",
        boom,
    )

    controller_result, message = controller_make_file(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
    )

    controller_file = Path("app/controllers/post_controller.py")
    controller_init_file = Path("app/controllers/__init__.py")

    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')\n"
    )

    expected_init_content = "\n"

    assert controller_result.is_successful is False
    assert controller_result.status == ScaffoldStatus.ERROR
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.registration_file_path == "app/controllers/__init__.py"
    assert controller_result.methods_added == ["index"]

    assert controller_file.read_text(encoding="utf-8") == expected_controller_content
    assert controller_init_file.read_text(encoding="utf-8") == expected_init_content

    assert "Failed to update __init__.py" in message
    assert "permission denied" in message


def test_controller_make_file_relative_view_file_path_no_method_name():
    controller_result, message = controller_make_file(
        relative_path=None,
        action="index",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
    )

    assert controller_result.is_successful is False
    assert controller_result.status == ScaffoldStatus.ERROR
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.registration_file_path is None
    assert controller_result.methods_added == []

    assert "relative_path required when action present" in message


def test_controller_make_file_with_a_post(controller_project):
    controller_result, message = controller_make_file(
        relative_path="posts",
        action="store",
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
    )

    post_controller_file = Path("app/controllers/post_controller.py")
    controller_init_file = Path("app/controllers/__init__.py")

    expected_controller_content = (
        "from flask import redirect, url_for\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def store() -> str:\n"
        "        return redirect(url_for('posts.index'))\n"
    )

    expected_init_content = (
        "\n"
        "from .post_controller import PostController\n"
    )

    assert controller_result.is_successful is True
    assert controller_result.status == ScaffoldStatus.ADDED
    assert controller_result.controller_name == "PostController"
    assert controller_result.controller_file_path == "app/controllers/post_controller.py"
    assert controller_result.registration_file_path == "app/controllers/__init__.py"
    assert controller_result.methods_added == ["store"]

    assert post_controller_file.read_text(encoding="utf-8") == expected_controller_content
    assert controller_init_file.read_text(encoding="utf-8") == expected_init_content

    assert "Created Controller Class With Method" in message
    assert "PostController" in message
    assert "store" in message
    assert "app/controllers/post_controller.py" in message
    assert "app/controllers/__init__.py" in message

