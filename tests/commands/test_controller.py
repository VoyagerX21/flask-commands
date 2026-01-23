import pytest
from click.testing import CliRunner
from flask_commands.commands.controller import make_controller

@pytest.fixture
def project(tmp_path, monkeypatch):
    """
    Create the project structure for testing
    app/
      controllers/
        __init__.py
    """
    root = tmp_path
    # Create the project subfolders
    (root / "app" / "controllers").mkdir(parents=True)
    (root / "app" / "models").mkdir()
    (root / "app" / "routes").mkdir()
    (root / "app" / "templates").mkdir()

     # Create a minimal app/__init__.py so blueprint registration works
    init_file_path = root / "app" / "__init__.py"
    init_file_path.write_text(
        "from flask import Flask\n"
        "from config import config\n"
        "\n"
        "\n"
        "def create_app(config_name) -> Flask:\n"
        "    app = Flask(__name__)\n"
        "\n"
        "    # apply configuration\n"
        "    app.config.from_object(config[config_name])\n"
        "\n"
        "    from app.routes.mains import bp as mains_blueprint\n"
        "    app.register_blueprint(mains_blueprint)\n"
        "\n"
        "    return app\n"
    )

    # Create a minimal app/__init__.py so blueprint registration works
    init_file_path = root / "app" / "controllers" / "__init__.py"
    init_file_path.write_text(
        "from .main_controller import MainController\n"
        "from .post_controller import PostController")

    main_controller_file_path = root / "app" / "controllers" / "main_controller.py"
    main_controller_file_path.write_text(
        "from flask import render_template\n"
        "\n"
        "class MainController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('mains/index.html')\n"
    )

    app_run_file_path = root / "run.py"
    app_run_file_path.write_text(
        "import os\n"
        "from app import create_app\n"
        "\n"
        "app = create_app(os.getenv('FLASK_CONFIG') or 'development')\n"
    )

    post_model_path = root / "app" / "models" / "post.py"
    post_model_path.write_text(
        "from app import db\n"
        "from datetime import datetime, timezone\n"
        "\n"
        "class Post(db.Model):\n"
        "    __tablename__ = 'posts'\n"
        "    # Columns\n"
        "    id = db.Column(db.Integer, primary_key=True)\n"
        "    created_at = db.Column(db.DateTime(timezone=True),\n"
        "                           index=True, \n"
        "                           default=lambda: datetime.now(timezone.utc))\n"
        "    updated_at = db.Column(db.DateTime(timezone=True),\n"
        "                           default=lambda: datetime.now(timezone.utc), \n"
        "                           onupdate=lambda: datetime.now(timezone.utc))\n"
        "\n"
        "    def store_in_database(self):\n"
        "        db.session.add(self)\n"
        "        db.session.commit()\n"
        "\n"
        "    def delete_from_database(self):\n"
        "        db.session.delete(self)\n"
        "        db.session.commit()\n"
        "\n"
        "    def __repr__(self):\n"
        '        """Model representation for Code Debugging"""\n'
        "        return f'<Post id:{self.id}>'\n"
    )

    post_controller_path = root / "app" / "controllers" / "post_controller.py"
    post_controller_path.write_text(
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')\n"
        "\n"
    )

    monkeypatch.chdir(root)
    return root

def test_make_controller_not_in_project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(make_controller, ["PostController"])

    assert result.exit_code == 0
    assert "Warning: You are not currently in a Flask project root directory" in result.output
    assert not (tmp_path / "app" / "controllers" / "post_controller.py").exists()

def test_make_controller_component_only(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["RecipeController"])

    assert result.exit_code == 0
    new_controller_file_path = project / "app" / "controllers" / "recipe_controller.py"
    assert new_controller_file_path.exists()
    assert new_controller_file_path.read_text(encoding="utf-8") == "class RecipeController:\n    pass\n"

    controller_init_file_path = project / "app" / "controllers" / "__init__.py"
    contents = controller_init_file_path.read_text(encoding="utf-8")
    assert "from .recipe_controller import RecipeController" in contents


def test_make_controller_file_exists(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["MainController"])

    assert result.exit_code == 0
    assert "Controller Already Exists" in result.output
    main_controller_path = project / "app" / "controllers" / "main_controller.py"
    expected_contents = (
        "from flask import render_template\n"
        "\n"
        "class MainController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('mains/index.html')\n"
    )
    assert main_controller_path.read_text(encoding="utf-8") == expected_contents
    controller_init_path = project / "app" / "controllers" / "__init__.py"
    content = controller_init_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController"
    )
    assert content == expected_contents

def test_make_controller_with_crud(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["CommentController", "--crud"])

    assert result.exit_code == 0

    # File comment_controller should exist
    comment_controller_file_path = project / "app" / "controllers" / "comment_controller.py"
    assert comment_controller_file_path.exists()

    # Check the contents of the new controller file
    expected_contents = (
        "from flask import render_template\n"
        "from flask import redirect, url_for\n"
        "\n"
        "class CommentController:\n"
        "\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('comments/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def show(comment_id: int) -> str:\n"
        "        return render_template('comments/show.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def create() -> str:\n"
        "        return render_template('comments/create.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def store() -> str:\n"
        "        return redirect(url_for('comments.index'))\n"
        "\n"
        "    @staticmethod\n"
        "    def edit(comment_id: int) -> str:\n"
        "        return render_template('comments/edit.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def update(comment_id: int) -> str:\n"
        "        return redirect(url_for('comments.index'))\n"
        "\n"
        "    @staticmethod\n"
        "    def destroy(comment_id: int) -> str:\n"
        "        return redirect(url_for('comments.index'))"
    )
    assert comment_controller_file_path.read_text(encoding="utf-8") == expected_contents

    # Check the contents of the new routes
    routes_comments_directory_path = project / "app" / "routes" / "comments"
    assert routes_comments_directory_path.exists()

    routes_comments_init_file_path = routes_comments_directory_path / "__init__.py"
    assert routes_comments_init_file_path.exists()

    routes_comments_route_file_path = routes_comments_directory_path / "routes.py"
    assert routes_comments_route_file_path.exists()
    expected_contents = (
        "from app.controllers import CommentController\n"
        "from app.routes.comments import bp\n"
        "\n"
        "@bp.route('/comments', methods=['GET'])\n"
        "def index():\n"
        "    return CommentController.index()\n"
        "\n"
        "@bp.route('/comments/<int:comment_id>', methods=['GET'])\n"
        "def show(comment_id: int):\n"
        "    return CommentController.show(comment_id)\n"
        "\n"
        "@bp.route('/comments/create', methods=['GET'])\n"
        "def create():\n"
        "    return CommentController.create()\n"
        "\n"
        "@bp.route('/comments', methods=['POST'])\n"
        "def store():\n"
        "    return CommentController.store()\n"
        "\n"
        "@bp.route('/comments/<int:comment_id>/edit', methods=['GET'])\n"
        "def edit(comment_id: int):\n"
        "    return CommentController.edit(comment_id)\n"
        "\n"
        "@bp.route('/comments/<int:comment_id>', methods=['POST'])\n"
        "def update(comment_id: int):\n"
        "    return CommentController.update(comment_id)\n"
        "\n"
        "@bp.route('/comments/<int:comment_id>/delete', methods=['POST'])\n"
        "def destroy(comment_id: int):\n"
        "    return CommentController.destroy(comment_id)\n"
    )
    assert routes_comments_route_file_path.read_text(encoding="utf-8") == expected_contents

    # Check the contents of the new templates
    create_template_file_path = project / "app" / "templates" / "comments" / "create.html"
    assert create_template_file_path.exists()
    edit_template_file_path = project / "app" / "templates" / "comments" / "edit.html"
    assert edit_template_file_path.exists()
    index_template_file_path = project / "app" / "templates" / "comments" / "index.html"
    assert index_template_file_path.exists()
    show_template_file_path = project / "app" / "templates" / "comments" / "show.html"
    assert show_template_file_path.exists()


# def test_make_controller_with_crud_nested_relationship(project):
#     pass
