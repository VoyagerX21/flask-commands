import os
import pytest
from click.testing import CliRunner
from flask_commands.commands.view import make_view

@pytest.fixture
def project(tmp_path, monkeypatch):
    """
    Create the project structure for testing
    app/
      __init__.py
      controllers/
      models/
      routes/
      static/
      templates/
    """
    root = tmp_path
    # Create the project subfolders
    (root / "app" / "controllers").mkdir(parents=True)
    (root / "app" / "models").mkdir()
    (root / "app" / "routes").mkdir()
    (root / "app" / "static").mkdir()
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

def test_make_view_not_in_project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(make_view, ["card"])

    assert result.exit_code == 0
    assert "Warning: You are not currently in a Flask project root directory" in result.output
    assert not (tmp_path / "app" / "templates" / "card.py").exists()

def test_make_view_component_only(project):
    """
    This should:
    1) create app/templates/card.html
    2) Not create any routes, controllers, or models
    3) print the "File Created" message
    """

    runner = CliRunner()
    result = runner.invoke(make_view, ["card"])

    assert result.exit_code == 0

     # File should exist
    template_file = project / "app" / "templates" / "card.html"
    assert template_file.exists()

    # Output should mention file created
    assert "Created New View" in result.output

def test_make_view_with_generated_controller(project):
    """
    This should
    1) create app/templates/posts/index.html
    2) infer controller name = PostController
    3) create controller file
    4) add the method to the controller file
    """
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.index", "-c"])

    assert result.exit_code == 0

    template_file = project / "app" / "templates" / "posts" / "index.html"
    assert template_file.exists()

    controller_file = project / "app" / "controllers" / "post_controller.py"
    assert controller_file.exists()

    # Controller contains method
    controller_text = controller_file.read_text()
    assert "class PostController" in controller_text
    assert "def index" in controller_text

def test_make_view_with_generated_controller_and_no_relationship(project):
    runner = CliRunner()
    result = runner.invoke(make_view, ["card", "-c"])

    assert result.exit_code == 0
    assert "Method Added To Controller" in result.output

def test_make_view_with_generated_route(project):
    """
    This should
    1) create app/templates/posts/index.html
    2) infer route + blueprint for posts
    """
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.index", "-r"])

    assert result.exit_code == 0

    template_file = project / "app" / "templates" / "posts" / "index.html"
    assert template_file.exists()

    # Route folder exists
    route_dir = project / "app" / "routes" / "posts"
    assert route_dir.exists()

    # routes.py should exist
    routes_file = route_dir / "routes.py"
    assert routes_file.exists()

    assert "/posts" in routes_file.read_text()

def test_make_view_with_generated_route_add_method(project):
    route_file = project / "app" / "routes" / "posts" / "routes.py"
    route_file.parent.mkdir(parents=True)
    route_file.write_text(
        "from app.controllers import MainController\n"
        "\n"
        "from app.routes.posts import bp\n"
        "@bp.route('/posts', methods=['GET'])\n"
        "def index():\n"
        "    return PostController.index()"
    )
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.show", "-r"])

    assert result.exit_code == 0

    assert "Added Route" in result.output

def test_make_view_with_generated_route_exception(project, monkeypatch):
    # Keep the real function around
    real_exists = os.path.exists

    def boom(path):
        # Raise only for our route folder lookup
        if "app/routes" in str(path):
            raise RuntimeError("boom boom boom")
        return real_exists(path)

    monkeypatch.setattr("os.path.exists", boom)

    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.index", "-r"])

    assert result.exit_code == 0
    assert "💣 Error:" in result.output
    assert "boom boom boom" in result.output

def test_make_view_with_generated_model(project):
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.index", "-m"])

    assert result.exit_code == 0

    model_file = project / "app" / "models" / "post.py"
    assert model_file.exists()

    model_file_content = model_file.read_text()
    assert "class Post(db.Model)" in model_file_content
    assert "__tablename__ = 'posts'" in model_file_content

def test_make_view_file_exists(project):
    # Pre-create
    template_file = project / "app" / "templates" / "card.html"
    template_file.write_text("hi")

    runner = CliRunner()
    result = runner.invoke(make_view, ["card"])

    assert result.exit_code == 0

    assert "View Already Exist" in result.output
    assert "hi" == template_file.read_text()

def test_make_view_controller_exist(project):
    # Pre-create
    controller_file = project / "app" / "controllers" / "post_controller.py"
    controller_file.write_text(
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')"
    )
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.show", '-c'])

    assert result.exit_code == 0

    assert "Method Added" in result.output
    assert "def show" in controller_file.read_text()
