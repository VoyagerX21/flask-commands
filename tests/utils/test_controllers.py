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
    directory, and returns"""
    project_root = tmp_path
    controller_dir = project_root / "app" / "controllers"
    controller_dir.mkdir(parents=True)

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
