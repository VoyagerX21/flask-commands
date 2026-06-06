import pytest
from click.testing import CliRunner
from flask_commands.commands.controller import make_controller
from flask_commands.utils.naming import camel_to_snake

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
        "    return PostController().index()\n",
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
        "    from app.routes.posts import bp as posts_blueprint\n"
        "    app.register_blueprint(posts_blueprint)\n"
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
        "    def index(self) -> str:\n"
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
        "    def index(self) -> str:\n"
        "        return render_template('posts/index.html')\n"
        "\n"
    )

    monkeypatch.chdir(root)
    return root

def _register_doc_model(project, model_name: str) -> None:
    snake_model_name = camel_to_snake(model_name)
    (project / "app"/ "models" / f"{snake_model_name}.py").write_text(
        f"class {model_name}:\n    pass\n", encoding="utf-8"
    )
    init_file = project / "app" / "models" / "__init__.py"
    init_model_contents = init_file.read_text(encoding="utf-8")
    model_import_line = f"from .{snake_model_name} import {model_name}"
    if model_import_line not in init_model_contents:
        separator = "\n" \
            if init_model_contents \
                and not init_model_contents.endswith("\n") else ""
        init_file.write_text(
            f"{init_model_contents}{separator}{model_import_line}\n",
            encoding="utf-8")

def _assert_route_contains(project, relative_path: str, route: str) -> None:
    route_file = project / "app" / "routes" / relative_path / "routes.py"
    assert route_file.exists()
    assert route in route_file.read_text(encoding="utf-8")

def test_make_controller_not_in_project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(make_controller, ["PostController"])

    assert result.exit_code == 0, result.output
    assert "Warning: You are not currently in a Flask project root directory" in result.output
    assert not (tmp_path / "app" / "controllers" / "post_controller.py").exists()

def test_make_controller_component_only(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["RecipeController"])

    assert result.exit_code == 0, result.output
    new_controller_file_path = project / "app" / "controllers" / "recipe_controller.py"
    assert new_controller_file_path.exists()
    assert new_controller_file_path.read_text(encoding="utf-8") == "class RecipeController:\n    pass\n"

    controller_init_file_path = project / "app" / "controllers" / "__init__.py"
    contents = controller_init_file_path.read_text(encoding="utf-8")
    assert "from .recipe_controller import RecipeController" in contents

def test_make_controller_file_exists(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["MainController"])

    assert result.exit_code == 0, result.output
    assert "Controller Already Exists" in result.output
    main_controller_path = project / "app" / "controllers" / "main_controller.py"
    expected_contents = (
        "from flask import render_template\n"
        "\n"
        "class MainController:\n"
        "    def index(self) -> str:\n"
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

def test_make_controller_with_explicit_model_creates_controller_and_model(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["TagController", "--model", "Tag"])

    assert result.exit_code == 0, result.output

    # Controller file + exact contents
    controller_file_path = project / "app" / "controllers" / "tag_controller.py"
    assert controller_file_path.exists()
    observed_contents = controller_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "class TagController:\n"
        "    pass\n"
    )
    assert observed_contents == expected_contents

    # Controller registration + exact contents
    controller_init_file_path = project / "app" / "controllers" / "__init__.py"
    observed_contents = controller_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
        "from .tag_controller import TagController\n"
    )
    assert observed_contents == expected_contents

    # Model file + exact contents
    model_file_path = project / "app" / "models" / "tag.py"
    assert model_file_path.exists()

    # Model registration + exact contents
    models_init_file_path = project / "app" / "models" / "__init__.py"
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .post import Post\n"
        "from .tag import Tag\n"
    )
    assert observed_contents == expected_contents

def test_make_controller_generate_model_nested_parent_chain_nested_choice(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["PostCommentController", "-m"], input="2\n")

    assert result.exit_code == 0, result.output

    # Controller was created
    controller_file_path = project / "app" / "controllers" / "post_comment_controller.py"
    assert controller_file_path.exists()
    observed_contents = controller_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "class PostCommentController:\n"
        "    pass\n"
    )
    assert observed_contents == expected_contents

    controller_init_file_path = project / "app" / "controllers" / "__init__.py"
    observed_contents = controller_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
        "from .post_comment_controller import PostCommentController\n"
    )
    assert observed_contents == expected_contents

    # Nested choice created Comment model
    comment_model_file_path = project / "app" / "models" / "comment.py"
    assert comment_model_file_path.exists()

    models_init_file_path = project / "app" / "models" / "__init__.py"
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .post import Post\n"
        "from .comment import Comment\n"
    )
    assert observed_contents == expected_contents

def test_make_controller_generate_model_nested_parent_chain_nested_choice_with_namespace(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["AdminPostCommentController", "-m"], input="2\n")

    assert result.exit_code == 0, result.output

    # Controller was created
    controller_file_path = project / "app" / "controllers" / "admin_post_comment_controller.py"
    assert controller_file_path.exists(), result.output
    observed_contents = controller_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "class AdminPostCommentController:\n"
        "    pass\n"
    )
    assert observed_contents == expected_contents

    controller_init_file_path = project / "app" / "controllers" / "__init__.py"
    observed_contents = controller_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
        "from .admin_post_comment_controller import AdminPostCommentController\n"
    )
    assert observed_contents == expected_contents

    # Nested choice created Comment model
    comment_model_file_path = project / "app" / "models" / "comment.py"
    assert comment_model_file_path.exists()

    models_init_file_path = project / "app" / "models" / "__init__.py"
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .post import Post\n"
        "from .comment import Comment\n"
    )
    assert observed_contents == expected_contents

def test_make_controller_generate_model_nested_parent_chain_flatten_choice(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["PostCommentController", "-m"], input="1\n")

    assert result.exit_code == 0, result.output

    # Controller was created
    controller_file_path = project / "app" / "controllers" / "post_comment_controller.py"
    assert controller_file_path.exists(), result.output
    observed_contents = controller_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "class PostCommentController:\n"
        "    pass\n"
    )
    assert observed_contents == expected_contents

    controller_init_file_path = project / "app" / "controllers" / "__init__.py"
    observed_contents = controller_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
        "from .post_comment_controller import PostCommentController\n"
    )
    assert observed_contents == expected_contents

    model_file_path = project / "app" / "models" / "post_comment.py"
    assert model_file_path.exists()

    models_init_file_path = project / "app" / "models" / "__init__.py"
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .post import Post\n"
        "from .post_comment import PostComment\n"
    )
    assert observed_contents == expected_contents

def test_make_controller_generate_model_nested_parent_chain_flatten_choice_with_namespace(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["AdminPostCommentController", "-m"], input="1\n")

    assert result.exit_code == 0, result.output

    # Controller was created
    controller_file_path = project / "app" / "controllers" / "admin_post_comment_controller.py"
    assert controller_file_path.exists(), result.output
    observed_contents = controller_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "class AdminPostCommentController:\n"
        "    pass\n"
    )
    assert observed_contents == expected_contents

    controller_init_file_path = project / "app" / "controllers" / "__init__.py"
    observed_contents = controller_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
        "from .admin_post_comment_controller import AdminPostCommentController\n"
    )
    assert observed_contents == expected_contents

    model_file_path = project / "app" / "models" / "admin_post_comment.py"
    assert model_file_path.exists()


    models_init_file_path = project / "app" / "models" / "__init__.py"
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .post import Post\n"
        "from .admin_post_comment import AdminPostComment\n"
    )
    assert observed_contents == expected_contents

def test_make_controller_generate_model_multi_child_segments_nested_choice(project):
    runner = CliRunner()
    result = runner.invoke(
        make_controller,
        ["AdminCommentController", "-m"],
        input="2\n",
    )

    assert result.exit_code == 0, result.output
    assert "Detected multiple child-like segments" in result.output

    # controller created
    controller_file_path = project / "app" / "controllers" / "admin_comment_controller.py"
    observed_contents = controller_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "class AdminCommentController:\n"
        "    pass\n"
    )
    assert observed_contents == expected_contents

    # nested choice created both models
    assert (project / "app" / "models" / "admin.py").exists()
    assert (project / "app" / "models" / "comment.py").exists()

    models_init_file_path = project / "app" / "models" / "__init__.py"
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .post import Post\n"
        "from .admin import Admin\n"
        "from .comment import Comment\n"
    )
    assert observed_contents == expected_contents

def test_make_controller_generate_model_multi_child_segments_flatten_choice(project):
    runner = CliRunner()
    result = runner.invoke(
        make_controller,
        ["AdminCommentController", "-m"],
        input="1\n",
    )

    assert result.exit_code == 0, result.output
    assert "Detected multiple child-like segments" in result.output

    # flatten choice creates one combined model
    assert (project / "app" / "models" / "admin_comment.py").exists()
    assert not (project / "app" / "models" / "admin.py").exists()
    assert not (project / "app" / "models" / "comment.py").exists()

    models_init_file_path = project / "app" / "models" / "__init__.py"
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .post import Post\n"
        "from .admin_comment import AdminComment\n"
    )
    assert observed_contents == expected_contents

def test_make_controller_generate_model_no_nested_candidates_uses_non_nested(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["AdminPostController", "-m"])

    assert result.exit_code == 0, result.output
    assert "Generated model(s)" in result.output
    assert "AdminPost" in result.output

    # Controller created
    controller_file_path = project / "app" / "controllers" / "admin_post_controller.py"
    observed_contents = controller_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "class AdminPostController:\n"
        "    pass\n"
    )
    assert observed_contents == expected_contents

    # Model created from non_nested_model_name branch (line 106)
    model_file_path = project / "app" / "models" / "admin_post.py"
    assert model_file_path.exists()

    models_init_file_path = project / "app" / "models" / "__init__.py"
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    expected_contents = (
        "from .post import Post\n"
        "from .admin_post import AdminPost\n"
    )
    assert observed_contents == expected_contents

def test_make_controller_with_crud(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["CommentController", "--crud"])

    assert result.exit_code == 0, result.output
    # File comment_controller should exist
    comment_controller_file_path = project / "app" / "controllers" / "comment_controller.py"
    assert comment_controller_file_path.exists()

    # Check the contents of the new controller file
    expected_contents = (
        "from flask import render_template, redirect, url_for\n"
        "from flask.typing import ResponseReturnValue\n"
        "\n"
        "class CommentController:\n"
        "\n"
        "    def index(self) -> str:\n"
        "        return render_template('comments/index.html')\n"
        "\n"
        "    def show(self, comment_id: int) -> str:\n"
        "        return render_template('comments/show.html')\n"
        "\n"
        "    def create(self) -> str:\n"
        "        return render_template('comments/create.html')\n"
        "\n"
        "    def store(self) -> ResponseReturnValue:\n"
        "        return redirect(url_for('comments.index'))\n"
        "\n"
        "    def edit(self, comment_id: int) -> str:\n"
        "        return render_template('comments/edit.html')\n"
        "\n"
        "    def update(self, comment_id: int) -> ResponseReturnValue:\n"
        "        return redirect(url_for('comments.index'))\n"
        "\n"
        "    def destroy(self, comment_id: int) -> ResponseReturnValue:\n"
        "        return redirect(url_for('comments.index'))"
    )
    observed_content = comment_controller_file_path.read_text(encoding="utf-8")
    assert observed_content == expected_contents

    assert not (project / "app" / "models" / "comment.py").exists()

    models_init_file_path = project / "app" / "models" / "__init__.py"
    models_init_contents = models_init_file_path.read_text(encoding="utf-8")
    assert "from .comment import Comment" not in models_init_contents


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
        "    return CommentController().index()\n"
        "\n"
        "@bp.route('/comments/<int:comment_id>', methods=['GET'])\n"
        "def show(comment_id: int):\n"
        "    return CommentController().show(comment_id)\n"
        "\n"
        "@bp.route('/comments/create', methods=['GET'])\n"
        "def create():\n"
        "    return CommentController().create()\n"
        "\n"
        "@bp.route('/comments', methods=['POST'])\n"
        "def store():\n"
        "    return CommentController().store()\n"
        "\n"
        "@bp.route('/comments/<int:comment_id>/edit', methods=['GET'])\n"
        "def edit(comment_id: int):\n"
        "    return CommentController().edit(comment_id)\n"
        "\n"
        "@bp.route('/comments/<int:comment_id>', methods=['POST'])\n"
        "def update(comment_id: int):\n"
        "    return CommentController().update(comment_id)\n"
        "\n"
        "@bp.route('/comments/<int:comment_id>/delete', methods=['POST'])\n"
        "def destroy(comment_id: int):\n"
        "    return CommentController().destroy(comment_id)\n"
    )
    observed_content = routes_comments_route_file_path.read_text(encoding="utf-8")
    assert observed_content == expected_contents

    # Check the contents of the new templates
    create_template_file_path = project / "app" / "templates" / "comments" / "create.html"
    assert create_template_file_path.exists()
    edit_template_file_path = project / "app" / "templates" / "comments" / "edit.html"
    assert edit_template_file_path.exists()
    index_template_file_path = project / "app" / "templates" / "comments" / "index.html"
    assert index_template_file_path.exists()
    show_template_file_path = project / "app" / "templates" / "comments" / "show.html"
    assert show_template_file_path.exists()

def test_make_controller_with_crud_nested_relationship(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["PostCommentController", "--crud"])

    assert result.exit_code == 0, result.output
     # File post_comment_controller should exist
    post_comment_controller_file_path = project / "app" / "controllers" / "post_comment_controller.py"
    assert post_comment_controller_file_path.exists()

    # Check the contents of the new controller file
    expected_contents = (
        "from flask import render_template, redirect, url_for\n"
        "from flask.typing import ResponseReturnValue\n"
        "\n"
        "class PostCommentController:\n"
        "\n"
        "    def index(self, post_id: int) -> str:\n"
        "        return render_template('posts/comments/index.html')\n"
        "\n"
        "    def show(self, post_id: int, comment_id: int) -> str:\n"
        "        return render_template('posts/comments/show.html')\n"
        "\n"
        "    def create(self, post_id: int) -> str:\n"
        "        return render_template('posts/comments/create.html')\n"
        "\n"
        "    def store(self, post_id: int) -> ResponseReturnValue:\n"
        "        return redirect(url_for('posts.comments.index', post_id=post_id))\n"
        "\n"
        "    def edit(self, post_id: int, comment_id: int) -> str:\n"
        "        return render_template('posts/comments/edit.html')\n"
        "\n"
        "    def update(self, post_id: int, comment_id: int) -> ResponseReturnValue:\n"
        "        return redirect(url_for('posts.comments.index', post_id=post_id))\n"
        "\n"
        "    def destroy(self, post_id: int, comment_id: int) -> ResponseReturnValue:\n"
        "        return redirect(url_for('posts.comments.index', post_id=post_id))")
    content = post_comment_controller_file_path.read_text(encoding="utf-8")
    assert content == expected_contents

    controller_init_file_path = project / "app" / "controllers" / "__init__.py"
    assert controller_init_file_path.exists()
    expected_contents = (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
        "from .post_comment_controller import PostCommentController\n")
    content = controller_init_file_path.read_text(encoding="utf-8")
    assert content == expected_contents

    route_post_comment_route_file_path = project / "app" / "routes" / "posts" / "comments" / "routes.py"
    assert route_post_comment_route_file_path.exists()
    expected_contents = (
        "from app.controllers import PostCommentController\n"
        "from app.routes.posts.comments import bp\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments', methods=['GET'])\n"
        "def index(post_id: int):\n"
        "    return PostCommentController().index(post_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['GET'])\n"
        "def show(post_id: int, comment_id: int):\n"
        "    return PostCommentController().show(post_id, comment_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments/create', methods=['GET'])\n"
        "def create(post_id: int):\n"
        "    return PostCommentController().create(post_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments', methods=['POST'])\n"
        "def store(post_id: int):\n"
        "    return PostCommentController().store(post_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>/edit', methods=['GET'])\n"
        "def edit(post_id: int, comment_id: int):\n"
        "    return PostCommentController().edit(post_id, comment_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['POST'])\n"
        "def update(post_id: int, comment_id: int):\n"
        "    return PostCommentController().update(post_id, comment_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>/delete', methods=['POST'])\n"
        "def destroy(post_id: int, comment_id: int):\n"
        "    return PostCommentController().destroy(post_id, comment_id)\n"
    )
    content = route_post_comment_route_file_path.read_text(encoding="utf-8")
    assert content == expected_contents

    route_post_comment_init_file_path = project / "app" / "routes" / "posts" / "comments" / "__init__.py"
    assert route_post_comment_init_file_path.exists()
    expected_contents = (
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('comments', __name__)\n"
        "\n"
        "from app.routes.posts.comments import routes\n")
    content = route_post_comment_init_file_path.read_text(encoding="utf-8")
    assert content == expected_contents

    route_post_init_file_path = project / "app" / "routes" / "posts" / "__init__.py"
    assert route_post_init_file_path.exists()
    expected_contents = (
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('posts', __name__)\n"
        "\n"
        "from app.routes.posts import routes\n"
        "\n"
        "from app.routes.posts.comments import bp as posts_comments_blueprint\n"
        "bp.register_blueprint(posts_comments_blueprint)\n")
    content = route_post_init_file_path.read_text(encoding="utf-8")
    assert content == expected_contents

    # Check the contents of the new templates
    create_template_file_path = project / "app" / "templates" / "posts" / "comments" / "create.html"
    assert create_template_file_path.exists()
    edit_template_file_path = project / "app" / "templates" / "posts" / "comments" / "edit.html"
    assert edit_template_file_path.exists()
    index_template_file_path = project / "app" / "templates" / "posts" / "comments" / "index.html"
    assert index_template_file_path.exists()
    show_template_file_path = project / "app" / "templates" / "posts" / "comments" / "show.html"
    assert show_template_file_path.exists()

def test_make_controller_with_generate_model(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["PostCommentController", "-m"], input="2\n")

    assert result.exit_code == 0, result.output
    model_file_path = project / "app" / "models" / "comment.py"
    assert model_file_path.exists()

    init_file_path = project / "app" / "models" / "__init__.py"
    init_contents = init_file_path.read_text(encoding="utf-8")
    assert "from .comment import Comment" in init_contents

def test_make_controller_warns_when_init_missing(project):
    controller_init_path = project / "app" / "controllers" / "__init__.py"
    controller_init_path.unlink()

    runner = CliRunner()
    result = runner.invoke(make_controller, ["CommentController"])

    assert result.exit_code == 0, result.output
    assert "Warning: One or more make controller steps produced a warning or failure." in result.output

def test_make_controller_generate_model_flat_flag_skips_prompt_and_creates_flat_model(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["PostCommentController", "-m", "--flat"])

    assert result.exit_code == 0, result.output
    assert "Choose model structure" not in result.output
    assert "Detected nested models:" not in result.output
    assert "Using --flat. Generated model(s): PostComment" in result.output

    # Controller file created
    controller_file_path = project / "app" / "controllers" / "post_comment_controller.py"
    assert controller_file_path.exists()
    assert controller_file_path.read_text(encoding="utf-8") == (
        "class PostCommentController:\n"
        "    pass\n"
    )

    # Controller registration updated
    controller_init_file_path = project / "app" / "controllers" / "__init__.py"
    assert controller_init_file_path.read_text(encoding="utf-8") == (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
        "from .post_comment_controller import PostCommentController\n"
    )

    # Flat model created, nested model not created
    assert (project / "app" / "models" / "post_comment.py").exists()
    assert not (project / "app" / "models" / "comment.py").exists()

    # Model registration updated correctly
    models_init_file_path = project / "app" / "models" / "__init__.py"
    assert models_init_file_path.read_text(encoding="utf-8") == (
        "from .post import Post\n"
        "from .post_comment import PostComment\n"
    )

    # No CRUD artifacts
    assert not (project / "app" / "routes" / "post_comments").exists()
    assert not (project / "app" / "templates" / "post_comments").exists()

def test_make_controller_generate_model_nest_flag_skips_prompt_and_creates_nested_model(project):
    runner = CliRunner()
    result = runner.invoke(make_controller, ["PostCommentController", "-m", "--nest"])

    assert result.exit_code == 0, result.output
    assert "Choose model structure" not in result.output
    assert "Detected nested models:" not in result.output
    assert "Using --nest. Generated model(s): Comment" in result.output

    # Controller file created
    controller_file_path = project / "app" / "controllers" / "post_comment_controller.py"
    assert controller_file_path.exists()
    assert controller_file_path.read_text(encoding="utf-8") == (
        "class PostCommentController:\n"
        "    pass\n"
    )

    # Controller registration updated
    controller_init_file_path = project / "app" / "controllers" / "__init__.py"
    assert controller_init_file_path.read_text(encoding="utf-8") == (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
        "from .post_comment_controller import PostCommentController\n"
    )

    # Nested model created, flat model not created
    assert not (project / "app" / "models" / "post_comment.py").exists()
    assert (project / "app" / "models" / "comment.py").exists()

    # Model registration updated correctly
    models_init_file_path = project / "app" / "models" / "__init__.py"
    assert models_init_file_path.read_text(encoding="utf-8") == (
        "from .post import Post\n"
        "from .comment import Comment\n"
    )

    # No CRUD artifacts
    assert not (project / "app" / "routes" / "post_comments").exists()
    assert not (project / "app" / "templates" / "post_comments").exists()

def test_make_controller_rejects_flat_and_nest_together(project):
    runner = CliRunner()
    result = runner.invoke(
        make_controller,
        ["GuardOneController", "-m", "--flat", "--nest"],
    )

    assert result.exit_code == 2
    assert "Use either --flat or --nest, not both." in result.output
    assert not (project / "app" / "controllers" / "guard_one_controller.py").exists()

def test_make_controller_rejects_flat_without_generate_model(project):
    runner = CliRunner()
    result = runner.invoke(
        make_controller,
        ["GuardTwoController", "--flat"],
    )

    assert result.exit_code == 2
    assert "--flat and --nest can only be used with --generate-model." in result.output
    assert not (project / "app" / "controllers" / "guard_two_controller.py").exists()

def test_make_controller_rejects_flat_with_explicit_model(project):
    runner = CliRunner()
    result = runner.invoke(
        make_controller,
        ["GuardThreeController", "-m", "--flat", "--model", "Tag"],
    )

    assert result.exit_code == 2
    assert "--flat and --nest cannot be used with --model." in result.output
    assert not (project / "app" / "controllers" / "guard_three_controller.py").exists()
    assert not (project / "app" / "models" / "tag.py").exists()

def test_docs_make_controller_the_basics_create_a_simple_controller_recipe_controller(project):
    result = CliRunner().invoke(make_controller, ["RecipeController"])
    assert result.exit_code == 0, result.output
    assert (project / "app/controllers/recipe_controller.py").read_text(encoding="utf-8") == (
        "class RecipeController:\n    pass\n"
    )

def test_docs_make_controller_the_basics_add_restful_actions_with_crud_recipe_controller(project):
    result = CliRunner().invoke(make_controller, ["RecipeController", "--crud"])
    assert result.exit_code == 0, result.output
    _assert_route_contains(project, "recipes", "@bp.route('/recipes/<int:recipe_id>', methods=['GET'])")
    assert (project / "app/templates/recipes/index.html").exists()
    assert (project / "app/templates/recipes/show.html").exists()
    assert (project / "app/templates/recipes/create.html").exists()
    assert (project / "app/templates/recipes/edit.html").exists()

def test_docs_controllers_and_models_name_the_model_directly_recipe_model(project):
    result = CliRunner().invoke(make_controller, ["RecipeController", "--model", "Recipe"])
    assert result.exit_code == 0, result.output
    assert (project / "app/models/recipe.py").exists()
    assert "from .recipe import Recipe" in (project / "app/models/__init__.py").read_text(encoding="utf-8")

def test_docs_controllers_and_models_generate_the_model_name_recipe_controller(project):
    result = CliRunner().invoke(make_controller, ["RecipeController", "-m"])
    assert result.exit_code == 0, result.output
    assert (project / "app/models/recipe.py").exists()

def test_docs_controllers_and_models_generating_a_restful_controller_with_a_model_recipe(project):
    result = CliRunner().invoke(make_controller, ["RecipeController", "--crud", "-m"])
    assert result.exit_code == 0, result.output
    assert (project / "app/models/recipe.py").exists()
    _assert_route_contains(project, "recipes", "@bp.route('/recipes/<int:recipe_id>', methods=['GET'])")

def test_docs_controllers_and_models_single_data_structures_shopping_list_model(project):
    result = CliRunner().invoke(
        make_controller,
        ["ShoppingListController", "--crud", "--model", "ShoppingList"],
    )
    assert result.exit_code == 0, result.output
    assert (project / "app/models/shopping_list.py").exists()
    _assert_route_contains(
        project,
        "shopping_lists",
        "@bp.route('/shopping-lists/<int:shopping_list_id>', methods=['GET'])",
    )

def test_docs_controllers_and_models_when_to_namespace_admin_user_crud(project):
    _register_doc_model(project, "User")
    result = CliRunner().invoke(make_controller, ["AdminUserController", "--crud"])
    assert result.exit_code == 0, result.output
    _assert_route_contains(project, "admin/users", "@bp.route('/admin/users/<int:user_id>', methods=['GET'])")

def test_docs_controllers_and_models_nested_relationship_recipe_ingredient_crud(project):
    _register_doc_model(project, "Recipe")
    result = CliRunner().invoke(make_controller, ["RecipeIngredientController", "--crud"])
    assert result.exit_code == 0, result.output
    _assert_route_contains(
        project,
        "recipes/ingredients",
        "@bp.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>', methods=['GET'])",
    )

def test_docs_flat_vs_nested_flat_or_nest_flat_flag_recipe_ingredient(project):
    _register_doc_model(project, "Recipe")
    result = CliRunner().invoke(make_controller, ["RecipeIngredientController", "--crud", "-m", "--flat"])
    assert result.exit_code == 0, result.output
    assert (project / "app/models/recipe_ingredient.py").exists()
    _assert_route_contains(
        project,
        "recipe_ingredients",
        "@bp.route('/recipe-ingredients/<int:recipe_ingredient_id>', methods=['GET'])",
    )

def test_docs_flat_vs_nested_flat_or_nest_nest_flag_recipe_ingredient(project):
    _register_doc_model(project, "Recipe")
    result = CliRunner().invoke(make_controller, ["RecipeIngredientController", "--crud", "-m", "--nest"])
    assert result.exit_code == 0, result.output
    assert (project / "app/models/ingredient.py").exists()
    _assert_route_contains(
        project,
        "recipes/ingredients",
        "@bp.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>', methods=['GET'])",
    )

def test_docs_flat_vs_nested_choose_flat_for_one_multi_word_model_shopping_list(project):
    result = CliRunner().invoke(make_controller, ["ShoppingListController", "--crud", "-m", "--flat"])
    assert result.exit_code == 0, result.output
    assert (project / "app/models/shopping_list.py").exists()
    _assert_route_contains(
        project,
        "shopping_lists",
        "@bp.route('/shopping-lists/<int:shopping_list_id>', methods=['GET'])",
    )

def test_docs_flat_vs_nested_build_nested_resources_one_level_at_a_time_shopping_list_chain(project):
    runner = CliRunner()
    assert runner.invoke(make_controller, ["ShoppingListController", "--crud", "-m", "--flat"]).exit_code == 0
    assert runner.invoke(make_controller, ["ShoppingListStoreController", "--crud", "-m", "--nest"]).exit_code == 0
    assert runner.invoke(make_controller, ["ShoppingListStoreIngredientController", "--crud", "-m", "--nest"]).exit_code == 0
    _assert_route_contains(project, "shopping_lists", "@bp.route('/shopping-lists', methods=['GET'])")
    _assert_route_contains(project, "shopping_lists/stores", "@bp.route('/shopping-lists/<int:shopping_list_id>/stores', methods=['GET'])")
    _assert_route_contains(project, "shopping_lists/stores/ingredients", "@bp.route('/shopping-lists/<int:shopping_list_id>/stores/<int:store_id>/ingredients', methods=['GET'])")

def test_docs_flat_vs_nested_build_nested_resources_skip_middle_creates_store_ingredient(project):
    runner = CliRunner()
    assert runner.invoke(make_controller, ["ShoppingListController", "--crud", "-m", "--flat"]).exit_code == 0
    assert runner.invoke(make_controller, ["ShoppingListStoreIngredientController", "--crud", "-m", "--nest"]).exit_code == 0
    assert (project / "app/models/store_ingredient.py").exists()
    _assert_route_contains(project, "shopping_lists/store_ingredients", "@bp.route('/shopping-lists/<int:shopping_list_id>/store-ingredients', methods=['GET'])")

def test_docs_flat_vs_nested_use_namespaces_without_models_staff_recipe(project):
    runner = CliRunner()
    assert runner.invoke(make_controller, ["RecipeController", "--crud", "-m"]).exit_code == 0
    assert runner.invoke(make_controller, ["StaffRecipeController", "--crud"]).exit_code == 0
    _assert_route_contains(project, "staff/recipes", "@bp.route('/staff/recipes/<int:recipe_id>', methods=['GET'])")

def test_docs_flat_vs_nested_combine_namespaces_with_nested_model_generation_staff_recipe_chain(project):
    runner = CliRunner()
    assert runner.invoke(make_controller, ["RecipeController", "--crud", "-m"]).exit_code == 0
    assert runner.invoke(make_controller, ["StaffRecipeController", "--crud"]).exit_code == 0
    assert runner.invoke(make_controller, ["StaffRecipeCookStepController", "--crud", "-m", "--nest"]).exit_code == 0
    assert runner.invoke(make_controller, ["StaffRecipeCookStepTipController", "--crud", "-m", "--nest"]).exit_code == 0
    _assert_route_contains(project, "staff/recipes/cook_steps", "@bp.route('/staff/recipes/<int:recipe_id>/cook-steps', methods=['GET'])")
    _assert_route_contains(project, "staff/recipes/cook_steps/tips", "@bp.route('/staff/recipes/<int:recipe_id>/cook-steps/<int:cook_step_id>/tips', methods=['GET'])")

def test_docs_flat_vs_nested_use_multi_word_namespace_front_desk_order(project):
    _register_doc_model(project, "Order")

    result = CliRunner().invoke(
        make_controller,
        ["FrontDeskOrderController", "--crud"],
    )

    assert result.exit_code == 0, result.output
    _assert_route_contains(
        project,
        "front_desk/orders",
        "@bp.route('/front-desk/orders/<int:order_id>', methods=['GET'])",
    )

def test_register_doc_model_does_not_duplicate_existing_import(project):
    _register_doc_model(project, "Recipe")
    _register_doc_model(project, "Recipe")

    init_contents = (project / "app" / "models" / "__init__.py").read_text(
        encoding="utf-8"
    )

    assert init_contents.count("from .recipe import Recipe") == 1
