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
    (root / "app" / "routes" / "posts").mkdir(parents=True)
    (root / "app" / "templates").mkdir()

    models_init_file_path = root / "app" / "models" / "__init__.py"
    models_init_file_path.write_text(
        "from .post import Post",
        encoding="utf-8"
    )

    routes_posts_init_file_path = root / "app" / "routes" / "posts" / "__init__.py"
    routes_posts_init_file_path.write_text(
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('posts', __name__)\n"
        "\n"
        "from app.routes.posts import routes\n",
        encoding="utf-8"
    )

    routes_posts_routes_file_path = root / "app" / "routes" / "posts" / "routes.py"
    routes_posts_routes_file_path.write_text(
        "from app.controllers import PostController\n"
        "from app.routes.posts import bp\n"
        "\n"
        "@bp.route('/posts', methods=['GET'])\n"
        "def index():\n"
        "    return PostController.index()\n",
        encoding="utf-8"
    )


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

# def test_make_controller_with_crud(project):
#     runner = CliRunner()
#     result = runner.invoke(make_controller, ["CommentController", "--crud"])

#     assert result.exit_code == 0

#     # File comment_controller should exist
#     comment_controller_file_path = project / "app" / "controllers" / "comment_controller.py"
#     assert comment_controller_file_path.exists()

#     # Check the contents of the new controller file
#     expected_contents = (
#         "from flask import render_template\n"
#         "from flask import redirect, url_for\n"
#         "\n"
#         "class CommentController:\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def index() -> str:\n"
#         "        return render_template('comments/index.html')\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def show(comment_id: int) -> str:\n"
#         "        return render_template('comments/show.html')\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def create() -> str:\n"
#         "        return render_template('comments/create.html')\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def store() -> str:\n"
#         "        return redirect(url_for('comments.index'))\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def edit(comment_id: int) -> str:\n"
#         "        return render_template('comments/edit.html')\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def update(comment_id: int) -> str:\n"
#         "        return redirect(url_for('comments.index'))\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def destroy(comment_id: int) -> str:\n"
#         "        return redirect(url_for('comments.index'))"
#     )
#     observed_content = comment_controller_file_path.read_text(encoding="utf-8")
#     assert observed_content == expected_contents

#     # Check the contents of the new routes
#     routes_comments_directory_path = project / "app" / "routes" / "comments"
#     assert routes_comments_directory_path.exists()

#     routes_comments_init_file_path = routes_comments_directory_path / "__init__.py"
#     assert routes_comments_init_file_path.exists()

#     routes_comments_route_file_path = routes_comments_directory_path / "routes.py"
#     assert routes_comments_route_file_path.exists()
#     expected_contents = (
#         "from app.controllers import CommentController\n"
#         "from app.routes.comments import bp\n"
#         "\n"
#         "@bp.route('/comments', methods=['GET'])\n"
#         "def index():\n"
#         "    return CommentController.index()\n"
#         "\n"
#         "@bp.route('/comments/<int:comment_id>', methods=['GET'])\n"
#         "def show(comment_id: int):\n"
#         "    return CommentController.show(comment_id)\n"
#         "\n"
#         "@bp.route('/comments/create', methods=['GET'])\n"
#         "def create():\n"
#         "    return CommentController.create()\n"
#         "\n"
#         "@bp.route('/comments', methods=['POST'])\n"
#         "def store():\n"
#         "    return CommentController.store()\n"
#         "\n"
#         "@bp.route('/comments/<int:comment_id>/edit', methods=['GET'])\n"
#         "def edit(comment_id: int):\n"
#         "    return CommentController.edit(comment_id)\n"
#         "\n"
#         "@bp.route('/comments/<int:comment_id>', methods=['POST'])\n"
#         "def update(comment_id: int):\n"
#         "    return CommentController.update(comment_id)\n"
#         "\n"
#         "@bp.route('/comments/<int:comment_id>/delete', methods=['POST'])\n"
#         "def destroy(comment_id: int):\n"
#         "    return CommentController.destroy(comment_id)\n"
#     )
#     observed_content = routes_comments_route_file_path.read_text(encoding="utf-8")
#     assert observed_content == expected_contents

#     # Check the contents of the new templates
#     create_template_file_path = project / "app" / "templates" / "comments" / "create.html"
#     assert create_template_file_path.exists()
#     edit_template_file_path = project / "app" / "templates" / "comments" / "edit.html"
#     assert edit_template_file_path.exists()
#     index_template_file_path = project / "app" / "templates" / "comments" / "index.html"
#     assert index_template_file_path.exists()
#     show_template_file_path = project / "app" / "templates" / "comments" / "show.html"
#     assert show_template_file_path.exists()

# def test_make_controller_with_crud_nested_relationship(project):
#     runner = CliRunner()
#     result = runner.invoke(make_controller, ["PostCommentController", "--crud"])

#     assert result.exit_code == 0

#      # File post_comment_controller should exist
#     post_comment_controller_file_path = project / "app" / "controllers" / "post_comment_controller.py"
#     assert post_comment_controller_file_path.exists()

#     # Check the contents of the new controller file
#     expected_contents = (
#         "from flask import render_template\n"
#         "from flask import redirect, url_for\n"
#         "\n"
#         "class PostCommentController:\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def index(post_id: int) -> str:\n"
#         "        return render_template('posts/comments/index.html')\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def show(post_id: int, comment_id: int) -> str:\n"
#         "        return render_template('posts/comments/show.html')\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def create(post_id: int) -> str:\n"
#         "        return render_template('posts/comments/create.html')\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def store(post_id: int) -> str:\n"
#         "        return redirect(url_for('posts.comments.index', post_id=post_id))\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def edit(post_id: int, comment_id: int) -> str:\n"
#         "        return render_template('posts/comments/edit.html')\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def update(post_id: int, comment_id: int) -> str:\n"
#         "        return redirect(url_for('posts.comments.index', post_id=post_id))\n"
#         "\n"
#         "    @staticmethod\n"
#         "    def destroy(post_id: int, comment_id: int) -> str:\n"
#         "        return redirect(url_for('posts.comments.index', post_id=post_id))")
#     content = post_comment_controller_file_path.read_text(encoding="utf-8")
#     assert content == expected_contents

#     controller_init_file_path = project / "app" / "controllers" / "__init__.py"
#     assert controller_init_file_path.exists()
#     expected_contents = (
#         "from .main_controller import MainController\n"
#         "from .post_controller import PostController\n"
#         "from .post_comment_controller import PostCommentController\n")
#     content = controller_init_file_path.read_text(encoding="utf-8")
#     assert content == expected_contents

#     route_post_comment_route_file_path = project / "app" / "routes" / "posts" / "comments" / "routes.py"
#     assert route_post_comment_route_file_path.exists()
#     expected_contents = (
#         "from app.controllers import PostCommentController\n"
#         "from app.routes.posts.comments import bp\n"
#         "\n"
#         "@bp.route('/posts/<int:post_id>/comments', methods=['GET'])\n"
#         "def index(post_id: int):\n"
#         "    return PostCommentController.index(post_id)\n"
#         "\n"
#         "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['GET'])\n"
#         "def show(post_id: int, comment_id: int):\n"
#         "    return PostCommentController.show(post_id, comment_id)\n"
#         "\n"
#         "@bp.route('/posts/<int:post_id>/comments/create', methods=['GET'])\n"
#         "def create(post_id: int):\n"
#         "    return PostCommentController.create(post_id)\n"
#         "\n"
#         "@bp.route('/posts/<int:post_id>/comments', methods=['POST'])\n"
#         "def store(post_id: int):\n"
#         "    return PostCommentController.store(post_id)\n"
#         "\n"
#         "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>/edit', methods=['GET'])\n"
#         "def edit(post_id: int, comment_id: int):\n"
#         "    return PostCommentController.edit(post_id, comment_id)\n"
#         "\n"
#         "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['POST'])\n"
#         "def update(post_id: int, comment_id: int):\n"
#         "    return PostCommentController.update(post_id, comment_id)\n"
#         "\n"
#         "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>/delete', methods=['POST'])\n"
#         "def destroy(post_id: int, comment_id: int):\n"
#         "    return PostCommentController.destroy(post_id, comment_id)\n"
#     )
#     content = route_post_comment_route_file_path.read_text(encoding="utf-8")
#     assert content == expected_contents

#     route_post_comment_init_file_path = project / "app" / "routes" / "posts" / "comments" / "__init__.py"
#     assert route_post_comment_init_file_path.exists()
#     expected_contents = (
#         "from flask import Blueprint\n"
#         "\n"
#         "bp = Blueprint('comments', __name__)\n"
#         "\n"
#         "from app.routes.posts.comments import routes\n")
#     content = route_post_comment_init_file_path.read_text(encoding="utf-8")
#     assert content == expected_contents

#     route_post_init_file_path = project / "app" / "routes" / "posts" / "__init__.py"
#     assert route_post_init_file_path.exists()
#     expected_contents = (
#         "from flask import Blueprint\n"
#         "\n"
#         "bp = Blueprint('posts', __name__)\n"
#         "\n"
#         "from app.routes.posts import routes\n"
#         "\n"
#         "from app.routes.posts.comments import bp as posts_comments_blueprint\n"
#         "bp.register_blueprint(posts_comments_blueprint)\n")
#     content = route_post_init_file_path.read_text(encoding="utf-8")
#     assert content == expected_contents

#     # Check the contents of the new templates
#     create_template_file_path = project / "app" / "templates" / "posts" / "comments" / "create.html"
#     assert create_template_file_path.exists()
#     edit_template_file_path = project / "app" / "templates" / "posts" / "comments" / "edit.html"
#     assert edit_template_file_path.exists()
#     index_template_file_path = project / "app" / "templates" / "posts" / "comments" / "index.html"
#     assert index_template_file_path.exists()
#     show_template_file_path = project / "app" / "templates" / "posts" / "comments" / "show.html"
#     assert show_template_file_path.exists()

# def test_make_controller_with_generate_model(project):
#     runner = CliRunner()
#     result = runner.invoke(make_controller, ["AdminPostCommentImageController", "-m"])

#     assert result.exit_code == 0
#     model_file_path = project / "app" / "models" / "image.py"
#     assert model_file_path.exists()

#     init_file_path = project / "app" / "models" / "__init__.py"
#     init_contents = init_file_path.read_text(encoding="utf-8")
#     assert "from .image import Image" in init_contents

def test_make_controller_warns_when_init_missing(project):
    controller_init_path = project / "app" / "controllers" / "__init__.py"
    controller_init_path.unlink()

    runner = CliRunner()
    result = runner.invoke(make_controller, ["CommentController"])

    assert result.exit_code == 0
    assert "Warning: One or more make controller steps produced a warning or failure." in result.output
