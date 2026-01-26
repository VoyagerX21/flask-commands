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

    assert result.exit_code == 0
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

    assert result.exit_code == 0
    assert "Warning: One or more make model steps failed." in result.output
