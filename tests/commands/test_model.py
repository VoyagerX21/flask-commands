import pytest
from click.testing import CliRunner
from flask_commands.commands.model import make_model


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

    models_init_file_path = root / "app" / "models" / "__init__.py"
    models_init_file_path.write_text(
        "from .user import User\n",
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
        "from .main_controller import MainController\n")

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


    monkeypatch.chdir(root)
    return root

def test_make_model_component_one(project):
    runner = CliRunner()
    result = runner.invoke(make_model, ["Post"])

    assert result.exit_code == 0, result.output
    model_file_path = project / "app" / "models" / "post.py"
    assert model_file_path.exists()
    expected_contents = (
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
    content = model_file_path.read_text(encoding="utf-8")
    assert content == expected_contents

    init_file_path = project / "app" / "models" / "__init__.py"
    init_contents = init_file_path.read_text(encoding="utf-8")
    assert "from .post import Post" in init_contents

def test_make_model_with_crud(project):
    runner = CliRunner()
    result = runner.invoke(make_model, ["Comment", "--crud"])

    assert result.exit_code == 0, result.output
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

def test_make_model_warns_when_init_missing(project):
    model_init_path = project / "app" / "models" / "__init__.py"
    model_init_path.unlink()

    runner = CliRunner()
    result = runner.invoke(make_model, ["Comment"])

    assert result.exit_code == 0, result.output
    assert "Warning: One or more make model steps produced a warning or failure." in result.output

def test_make_model_not_in_project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(make_model, ["Post"])

    assert result.exit_code == 0, result.output
    assert "Warning: You are not currently in a Flask project root directory" in result.output
    assert not (tmp_path / "app" / "models" / "post.py").exists()

def test_make_model_errors_when_name_cannot_be_generated(project):
    runner = CliRunner()
    result = runner.invoke(make_model, ["comment"])

    assert result.exit_code == 0, result.output
    expected_output = "💣 Error: Could not generate model name from input."
    observed_output = result.output
    assert expected_output in observed_output

    model_file_path = project / "app" / "models" / "comment.py"
    assert not model_file_path.exists()

def test_make_model_with_crud_nested_leaf_flatten_choice(project):
    runner = CliRunner()
    result = runner.invoke(make_model, ["UserComment", "--crud"], input="flat\n")

    assert result.exit_code == 0, result.output

    expected_output = (
        "Detected nested model structure:\n"
        "  1) (flatten model) = UserComment\n"
        "  2) (nested leaf model) = Comment"
    )
    observed_output = result.output
    assert expected_output in observed_output

    user_comment_controller_file_path = project / "app" / "controllers" / "user_comment_controller.py"
    assert user_comment_controller_file_path.exists()
    expected_contents = (
        "from flask import render_template\n"
        "from flask import redirect, url_for\n"
        "\n"
        "class UserCommentController:\n"
        "\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('user_comments/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def show(user_comment_id: int) -> str:\n"
        "        return render_template('user_comments/show.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def create() -> str:\n"
        "        return render_template('user_comments/create.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def store() -> str:\n"
        "        return redirect(url_for('user_comments.index'))\n"
        "\n"
        "    @staticmethod\n"
        "    def edit(user_comment_id: int) -> str:\n"
        "        return render_template('user_comments/edit.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def update(user_comment_id: int) -> str:\n"
        "        return redirect(url_for('user_comments.index'))\n"
        "\n"
        "    @staticmethod\n"
        "    def destroy(user_comment_id: int) -> str:\n"
        "        return redirect(url_for('user_comments.index'))"
    )
    observed_contents = user_comment_controller_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

    routes_user_comments_route_file_path = project / "app" / "routes" / "user_comments" / "routes.py"
    assert routes_user_comments_route_file_path.exists()
    expected_contents = (
        "from app.controllers import UserCommentController\n"
        "from app.routes.user_comments import bp\n"
        "\n"
        "@bp.route('/user-comments', methods=['GET'])\n"
        "def index():\n"
        "    return UserCommentController.index()\n"
        "\n"
        "@bp.route('/user-comments/<int:user_comment_id>', methods=['GET'])\n"
        "def show(user_comment_id: int):\n"
        "    return UserCommentController.show(user_comment_id)\n"
        "\n"
        "@bp.route('/user-comments/create', methods=['GET'])\n"
        "def create():\n"
        "    return UserCommentController.create()\n"
        "\n"
        "@bp.route('/user-comments', methods=['POST'])\n"
        "def store():\n"
        "    return UserCommentController.store()\n"
        "\n"
        "@bp.route('/user-comments/<int:user_comment_id>/edit', methods=['GET'])\n"
        "def edit(user_comment_id: int):\n"
        "    return UserCommentController.edit(user_comment_id)\n"
        "\n"
        "@bp.route('/user-comments/<int:user_comment_id>', methods=['POST'])\n"
        "def update(user_comment_id: int):\n"
        "    return UserCommentController.update(user_comment_id)\n"
        "\n"
        "@bp.route('/user-comments/<int:user_comment_id>/delete', methods=['POST'])\n"
        "def destroy(user_comment_id: int):\n"
        "    return UserCommentController.destroy(user_comment_id)\n"
    )
    observed_contents = routes_user_comments_route_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

    models_init_file_path = project / "app" / "models" / "__init__.py"
    expected_contents = (
        "from .user import User\n"
        "from .user_comment import UserComment\n"
    )
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

    # Check the contents of the new templates
    create_template_file_path = project / "app" / "templates" / "user_comments" / "create.html"
    assert create_template_file_path.exists()
    edit_template_file_path = project / "app" / "templates" / "user_comments" / "edit.html"
    assert edit_template_file_path.exists()
    index_template_file_path = project / "app" / "templates" / "user_comments" / "index.html"
    assert index_template_file_path.exists()
    show_template_file_path = project / "app" / "templates" / "user_comments" / "show.html"
    assert show_template_file_path.exists()

def test_make_model_with_crud_nested_leaf_nested_choice(project):
    runner = CliRunner()
    result = runner.invoke(make_model, ["UserComment", "--crud"], input="nest\n")

    assert result.exit_code == 0, result.output

    expected_output = (
        "Detected nested model structure:\n"
        "  1) (flatten model) = UserComment\n"
        "  2) (nested leaf model) = Comment"
    )
    observed_output = result.output
    assert expected_output in observed_output

    user_comment_controller_file_path = project / "app" / "controllers" / "user_comment_controller.py"
    assert user_comment_controller_file_path.exists()
    expected_contents = (
        "from flask import render_template\n"
        "from flask import redirect, url_for\n"
        "\n"
        "class UserCommentController:\n"
        "\n"
        "    @staticmethod\n"
        "    def index(user_id: int) -> str:\n"
        "        return render_template('users/comments/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def show(user_id: int, comment_id: int) -> str:\n"
        "        return render_template('users/comments/show.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def create(user_id: int) -> str:\n"
        "        return render_template('users/comments/create.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def store(user_id: int) -> str:\n"
        "        return redirect(url_for('users.comments.index', user_id=user_id))\n"
        "\n"
        "    @staticmethod\n"
        "    def edit(user_id: int, comment_id: int) -> str:\n"
        "        return render_template('users/comments/edit.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def update(user_id: int, comment_id: int) -> str:\n"
        "        return redirect(url_for('users.comments.index', user_id=user_id))\n"
        "\n"
        "    @staticmethod\n"
        "    def destroy(user_id: int, comment_id: int) -> str:\n"
        "        return redirect(url_for('users.comments.index', user_id=user_id))"
    )
    observed_contents = user_comment_controller_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

    routes_user_comments_route_file_path = project / "app" / "routes" / "users" / "comments" / "routes.py"
    assert routes_user_comments_route_file_path.exists()
    expected_contents = (
        "from app.controllers import UserCommentController\n"
        "from app.routes.users.comments import bp\n"
        "\n"
        "@bp.route('/users/<int:user_id>/comments', methods=['GET'])\n"
        "def index(user_id: int):\n"
        "    return UserCommentController.index(user_id)\n"
        "\n"
        "@bp.route('/users/<int:user_id>/comments/<int:comment_id>', methods=['GET'])\n"
        "def show(user_id: int, comment_id: int):\n"
        "    return UserCommentController.show(user_id, comment_id)\n"
        "\n"
        "@bp.route('/users/<int:user_id>/comments/create', methods=['GET'])\n"
        "def create(user_id: int):\n"
        "    return UserCommentController.create(user_id)\n"
        "\n"
        "@bp.route('/users/<int:user_id>/comments', methods=['POST'])\n"
        "def store(user_id: int):\n"
        "    return UserCommentController.store(user_id)\n"
        "\n"
        "@bp.route('/users/<int:user_id>/comments/<int:comment_id>/edit', methods=['GET'])\n"
        "def edit(user_id: int, comment_id: int):\n"
        "    return UserCommentController.edit(user_id, comment_id)\n"
        "\n"
        "@bp.route('/users/<int:user_id>/comments/<int:comment_id>', methods=['POST'])\n"
        "def update(user_id: int, comment_id: int):\n"
        "    return UserCommentController.update(user_id, comment_id)\n"
        "\n"
        "@bp.route('/users/<int:user_id>/comments/<int:comment_id>/delete', methods=['POST'])\n"
        "def destroy(user_id: int, comment_id: int):\n"
        "    return UserCommentController.destroy(user_id, comment_id)\n"
    )
    observed_contents = routes_user_comments_route_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

    user_comment_model_file_path = project / "app" / "models" / "user_comment.py"
    assert not user_comment_model_file_path.exists()

    models_init_file_path = project / "app" / "models" / "__init__.py"
    expected_contents = (
        "from .user import User\n"
        "from .comment import Comment\n"
    )
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

    # Check the contents of the new templates
    create_template_file_path = project / "app" / "templates" / "users" / "comments" / "create.html"
    assert create_template_file_path.exists()
    edit_template_file_path = project / "app" / "templates" / "users" / "comments" / "edit.html"
    assert edit_template_file_path.exists()
    index_template_file_path = project / "app" / "templates" / "users" / "comments" / "index.html"
    assert index_template_file_path.exists()
    show_template_file_path = project / "app" / "templates" / "users" / "comments" / "show.html"
    assert show_template_file_path.exists()

def test_make_model_with_crud_nested_chain_nested_choice(project):
    runner = CliRunner()
    result = runner.invoke(make_model, ["PostComment", "--crud"], input="nest\n")

    assert result.exit_code == 0, result.output

    expected_output = (
        "Detected nested model structure:\n"
        "  1) (flatten model) = PostComment\n"
        "  2) (nested model chain) = Post -> Comment"
    )
    observed_output = result.output
    assert expected_output in observed_output

    post_comment_controller_file_path = project / "app" / "controllers" / "post_comment_controller.py"
    assert post_comment_controller_file_path.exists()
    expected_contents = (
        "from flask import render_template\n"
        "from flask import redirect, url_for\n"
        "\n"
        "class PostCommentController:\n"
        "\n"
        "    @staticmethod\n"
        "    def index(post_id: int) -> str:\n"
        "        return render_template('posts/comments/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def show(post_id: int, comment_id: int) -> str:\n"
        "        return render_template('posts/comments/show.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def create(post_id: int) -> str:\n"
        "        return render_template('posts/comments/create.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def store(post_id: int) -> str:\n"
        "        return redirect(url_for('posts.comments.index', post_id=post_id))\n"
        "\n"
        "    @staticmethod\n"
        "    def edit(post_id: int, comment_id: int) -> str:\n"
        "        return render_template('posts/comments/edit.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def update(post_id: int, comment_id: int) -> str:\n"
        "        return redirect(url_for('posts.comments.index', post_id=post_id))\n"
        "\n"
        "    @staticmethod\n"
        "    def destroy(post_id: int, comment_id: int) -> str:\n"
        "        return redirect(url_for('posts.comments.index', post_id=post_id))"
    )
    observed_contents = post_comment_controller_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

    route_post_comment_route_file_path = project / "app" / "routes" / "posts" / "comments" / "routes.py"
    assert route_post_comment_route_file_path.exists()
    expected_contents = (
        "from app.controllers import PostCommentController\n"
        "from app.routes.posts.comments import bp\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments', methods=['GET'])\n"
        "def index(post_id: int):\n"
        "    return PostCommentController.index(post_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['GET'])\n"
        "def show(post_id: int, comment_id: int):\n"
        "    return PostCommentController.show(post_id, comment_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments/create', methods=['GET'])\n"
        "def create(post_id: int):\n"
        "    return PostCommentController.create(post_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments', methods=['POST'])\n"
        "def store(post_id: int):\n"
        "    return PostCommentController.store(post_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>/edit', methods=['GET'])\n"
        "def edit(post_id: int, comment_id: int):\n"
        "    return PostCommentController.edit(post_id, comment_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['POST'])\n"
        "def update(post_id: int, comment_id: int):\n"
        "    return PostCommentController.update(post_id, comment_id)\n"
        "\n"
        "@bp.route('/posts/<int:post_id>/comments/<int:comment_id>/delete', methods=['POST'])\n"
        "def destroy(post_id: int, comment_id: int):\n"
        "    return PostCommentController.destroy(post_id, comment_id)\n"
    )
    observed_contents = route_post_comment_route_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

    models_init_file_path = project / "app" / "models" / "__init__.py"
    expected_contents = (
        "from .user import User\n"
        "from .post import Post\n"
        "from .comment import Comment\n"
    )
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

def test_make_model_with_crud_controller(project):
    runner = CliRunner()
    result = runner.invoke(make_model, ["Controller", "--crud"])

    assert result.exit_code == 0, result.output
    assert "💣 Error: Could not generate model name from input." not in result.output
    assert "Detected nested model structure:" not in result.output


    model_file_path = project / "app" / "models" / "controller.py"
    assert model_file_path.exists()

    controllers_init_file_path = project / "app" / "controllers" / "__init__.py"
    assert "from .controller_controller import ControllerController" in \
        controllers_init_file_path.read_text(encoding="utf-8")

    controller_file_path = project / "app" / "controllers" / "controller_controller.py"
    assert controller_file_path.exists()
    expected_contents = (
        "from flask import render_template\n"
        "from flask import redirect, url_for\n"
        "\n"
        "class ControllerController:\n"
        "\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('controllers/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def show(controller_id: int) -> str:\n"
        "        return render_template('controllers/show.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def create() -> str:\n"
        "        return render_template('controllers/create.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def store() -> str:\n"
        "        return redirect(url_for('controllers.index'))\n"
        "\n"
        "    @staticmethod\n"
        "    def edit(controller_id: int) -> str:\n"
        "        return render_template('controllers/edit.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def update(controller_id: int) -> str:\n"
        "        return redirect(url_for('controllers.index'))\n"
        "\n"
        "    @staticmethod\n"
        "    def destroy(controller_id: int) -> str:\n"
        "        return redirect(url_for('controllers.index'))"
    )
    observed_contents = controller_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

    routes_file_path = project / "app" / "routes" / "controllers" / "routes.py"
    assert routes_file_path.exists()
    expected_contents = (
        "from app.controllers import ControllerController\n"
        "from app.routes.controllers import bp\n"
        "\n"
        "@bp.route('/controllers', methods=['GET'])\n"
        "def index():\n"
        "    return ControllerController.index()\n"
        "\n"
        "@bp.route('/controllers/<int:controller_id>', methods=['GET'])\n"
        "def show(controller_id: int):\n"
        "    return ControllerController.show(controller_id)\n"
        "\n"
        "@bp.route('/controllers/create', methods=['GET'])\n"
        "def create():\n"
        "    return ControllerController.create()\n"
        "\n"
        "@bp.route('/controllers', methods=['POST'])\n"
        "def store():\n"
        "    return ControllerController.store()\n"
        "\n"
        "@bp.route('/controllers/<int:controller_id>/edit', methods=['GET'])\n"
        "def edit(controller_id: int):\n"
        "    return ControllerController.edit(controller_id)\n"
        "\n"
        "@bp.route('/controllers/<int:controller_id>', methods=['POST'])\n"
        "def update(controller_id: int):\n"
        "    return ControllerController.update(controller_id)\n"
        "\n"
        "@bp.route('/controllers/<int:controller_id>/delete', methods=['POST'])\n"
        "def destroy(controller_id: int):\n"
        "    return ControllerController.destroy(controller_id)\n"
    )
    observed_contents = routes_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

    models_init_file_path = project / "app" / "models" / "__init__.py"
    expected_contents = (
        "from .user import User\n"
        "from .controller import Controller\n"
    )
    observed_contents = models_init_file_path.read_text(encoding="utf-8")
    assert observed_contents == expected_contents

    create_template_file_path = project / "app" / "templates" / "controllers" / "create.html"
    assert create_template_file_path.exists()
    edit_template_file_path = project / "app" / "templates" / "controllers" / "edit.html"
    assert edit_template_file_path.exists()
    index_template_file_path = project / "app" / "templates" / "controllers" / "index.html"
    assert index_template_file_path.exists()
    show_template_file_path = project / "app" / "templates" / "controllers" / "show.html"
    assert show_template_file_path.exists()

def test_make_model_with_crud_flat_flag_skips_prompt(project):
    runner = CliRunner()
    result = runner.invoke(make_model, ["UserComment", "--crud", "--flat"])

    assert result.exit_code == 0, result.output
    assert "Choose model structure" not in result.output
    assert "Detected nested model structure" not in result.output
    assert "- Using --flat. Generated model(s): UserComment" in result.output

    assert (project / "app" / "models" / "user_comment.py").exists()
    assert not (project / "app" / "models" / "comment.py").exists()

    models_init = (project / "app" / "models" / "__init__.py").read_text(encoding="utf-8")
    assert "from .user_comment import UserComment" in models_init

def test_make_model_with_crud_nest_flag_skips_prompt(project):
    runner = CliRunner()
    result = runner.invoke(make_model, ["UserComment", "--crud", "--nest"])

    assert result.exit_code == 0, result.output
    assert "Choose model structure" not in result.output
    assert "Detected nested model structure" not in result.output
    assert "- Using --nest. Generated model(s): Comment" in result.output

    assert not (project / "app" / "models" / "user_comment.py").exists()
    assert (project / "app" / "models" / "comment.py").exists()

    models_init = (project / "app" / "models" / "__init__.py").read_text(encoding="utf-8")
    assert "from .comment import Comment" in models_init
    assert "from .user_comment import UserComment" not in models_init

def test_make_model_rejects_flat_and_nest_together(project):
    runner = CliRunner()
    result = runner.invoke(make_model, ["UserComment", "--crud", "--flat", "--nest"])

    assert result.exit_code == 2
    assert "Use either --flat or --nest, not both." in result.output

def test_make_model_rejects_flat_without_crud(project):
    runner = CliRunner()
    result = runner.invoke(make_model, ["UserComment", "--flat"])

    assert result.exit_code == 2
    assert "--flat and --nest can only be used with --crud." in result.output


