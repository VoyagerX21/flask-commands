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

    # Create a minimal app/__init__.py so blueprint registration works
    init_file_path = root / "app" / "controllers" / "__init__.py"
    init_file_path.write_text("from .main_controller import MainController")

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
    app_run_file_path.write_text("", encoding="utf-8")

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
    new_controller_file = project / "app" / "controllers" / "recipe_controller.py"
    assert new_controller_file.exists()
    assert new_controller_file.read_text(encoding="utf-8") == "class RecipeController:\n    pass\n"

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
    assert controller_init_path.read_text(encoding="utf-8") == "from .main_controller import MainController"
