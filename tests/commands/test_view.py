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

    monkeypatch.chdir(root)
    return root

def test_make_view_component_only(project):
    """
    This should:
    1) create app/templates/card.html
    2) Not create any routes, controllers, or models
    3) prin the "File Created" message
    """

    runner = CliRunner()

    result = runner.invoke(make_view, ["card"])

    assert result.exit_code == 0

     # File should exist
    template_file = project / "app" / "templates" / "card.html"
    assert template_file.exists()

    # Output should mention file created
    assert "File created" in result.output


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


def test_make_view_with_generated_route(project):
    """
    This should
    1) create app/templates/posts/index.html
    2) infer route + blueprint for posts
    """
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.index", "-r"])

    assert result.exit_code == 0

    print(result.output)

    template_file = project / "app" / "templates" / "posts" / "index.html"
    assert template_file.exists()

    # Route folder exists
    route_dir = project / "app" / "routes" / "posts"
    assert route_dir.exists()

    # routes.py should exist
    routes_file = route_dir / "routes.py"
    assert routes_file.exists()

    assert "/posts" in routes_file.read_text()
