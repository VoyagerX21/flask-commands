import os
from click.testing import CliRunner
from flask_commands.commands.new import new



def _requirements_packages(project_path):
    req = (project_path / "requirements.txt").read_text(encoding="utf-8").splitlines()
    return {line.split("==", 1)[0].strip().lower() for line in req if "==" in line}

def _assert_common_project_scaffold(project_path, project_name):
    # Core paths
    assert (project_path / "run.py").exists()
    assert (project_path / "run.sh").exists()
    assert (project_path / ".env").exists()
    assert (project_path / ".env.example").exists()
    assert (project_path / "requirements.txt").exists()
    assert (project_path / "venv" / "bin" / "python").exists()

    assert (project_path / "app" / "controllers" / "__init__.py").exists()
    assert (project_path / "app" / "controllers" / "main_controller.py").exists()
    assert (project_path / "app" / "routes" / "mains" / "__init__.py").exists()
    assert (project_path / "app" / "routes" / "mains" / "routes.py").exists()
    assert (project_path / "app" / "templates" / "mains" / "index.html").exists()
    assert (project_path / "app" / "static" / "src" / "input.css").exists()
    assert (project_path / "config" / "__init__.py").exists()
    assert (project_path / "config" / "base_config.py").exists()
    assert (project_path / "config" / "development_config.py").exists()
    assert (project_path / "config" / "production_config.py").exists()

    # Executable run.sh
    assert os.access(project_path / "run.sh", os.X_OK)

    # Exact content checks
    expected_main_controller = (
        "from flask import render_template\n"
        "\n"
        "class MainController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('mains/index.html')\n"
    )
    assert (project_path / "app" / "controllers" / "main_controller.py").read_text(encoding="utf-8") == expected_main_controller

    expected_main_routes = (
        "from app.controllers import MainController\n"
        "from app.routes.mains import bp\n"
        "\n"
        "@bp.route('/', methods=['GET'])\n"
        "def index():\n"
        "    return MainController.index()\n"
    )
    assert (project_path / "app" / "routes" / "mains" / "routes.py").read_text(encoding="utf-8") == expected_main_routes

    run_sh = (project_path / "run.sh").read_text(encoding="utf-8")
    assert "project_path" not in run_sh
    assert f"cd {project_path}" in run_sh

def test_new_command_creates_project_with_db(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(new, ["my_app"])

    assert result.exit_code == 0, result.output
    assert "cd my_app" in result.output
    assert "./run.sh" in result.output

    project_path = tmp_path / "my_app"
    _assert_common_project_scaffold(project_path, "my_app")

    expected_env = (
        "SECRET_KEY=PUT_SOMETHING_SECRET_HERE\n"
        "FLASK_APP=run.py\n"
        "FLASK_CONFIG=development\n"
        f"APP_NAME=my_app\n"
        f"SQLALCHEMY_DEVELOPMENT_DATABASE_URI=sqlite:///{project_path}/my_app_dev.db\n"
        f"SQLALCHEMY_PRODUCTION_DATABASE_URI=mysql+pymysql://username:password@localhost:3306/my_app_prod\n"
    )
    assert (project_path / ".env").read_text(encoding="utf-8") == expected_env


    assert (project_path / "app" / "models").is_dir()
    assert (project_path / "app" / "models" / "__init__.py").read_text(encoding="utf-8") == "from .user import User\n"

    user_model = (project_path / "app" / "models" / "user.py").read_text(encoding="utf-8")
    assert "class User(UserMixin, db.Model):" in user_model
    assert "__tablename__ = 'users'" in user_model
    assert "@login_manager.user_loader" in user_model

    app_init = (project_path / "app" / "__init__.py").read_text(encoding="utf-8")
    assert "from flask_login import LoginManager" in app_init
    assert "from flask_migrate import Migrate" in app_init
    assert "from flask_sqlalchemy import SQLAlchemy" in app_init
    assert "from app import models" in app_init

    pkgs = _requirements_packages(project_path)
    assert "flask" in pkgs
    assert "python-dotenv" in pkgs
    assert "flask-login" in pkgs
    assert "flask-migrate" in pkgs
    assert "flask-sqlalchemy" in pkgs

    # DB path created by flask db init
    assert (project_path / "migrations").exists()

def test_new_command_creates_project_without_db(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(new, ["my_app", "--no-db"])

    assert result.exit_code == 0, result.output
#     assert "cd my_app" in result.output
    assert "./run.sh" in result.output

    project = tmp_path / "my_app"
    _assert_common_project_scaffold(project, "my_app")


    expected_env = (
        "SECRET_KEY=PUT_SOMETHING_SECRET_HERE\n"
        "FLASK_APP=run.py\n"
        "FLASK_CONFIG=development\n"
        f"APP_NAME=my_app\n"
    )
    assert (project / ".env").read_text(encoding="utf-8") == expected_env

    expected_env_example = (
        "SECRET_KEY=\n"
        "FLASK_APP=\n"
        "FLASK_CONFIG=\n"
        "APP_NAME=\n"
    )
    assert (project / ".env.example").read_text(encoding="utf-8") == expected_env_example

    assert not (project / "app" / "models").exists()
    assert not (project / "migrations").exists()

    app_init = (project / "app" / "__init__.py").read_text(encoding="utf-8")
    assert "from app import models" not in app_init

    # Desired no-db behavior assertions:
    assert "from flask_login import LoginManager" not in app_init
    assert "from flask_migrate import Migrate" not in app_init
    assert "from flask_sqlalchemy import SQLAlchemy" not in app_init

    pkgs = _requirements_packages(project)
    assert "flask" in pkgs
    assert "python-dotenv" in pkgs
    assert "flask-login" not in pkgs
    assert "flask-migrate" not in pkgs
    assert "flask-sqlalchemy" not in pkgs

def test_new_command_fails_if_project_exists(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    # Pre-create the project directory
    (tmp_path / "existing_project").mkdir()

    result = runner.invoke(new, ["existing_project"])

    assert result.exit_code == 0, result.output
    assert "already exists" in result.output

def test_new_command_cleans_up_on_exception(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("flask_commands.commands.new.create_venv", boom)

    result = runner.invoke(new, ["broken_project"])

    assert result.exit_code == 1
    assert not (tmp_path / "broken_project").exists()
    assert "Project Creation Failed" in result.output
    assert "boom" in result.output

def test_new_command_exception_before_project_directory_exists_does_not_cleanup(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    blocking_file = tmp_path / "taken"
    blocking_file.write_text("not a directory", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(new, ["taken/my_app"])

    assert result.exit_code != 0
    assert "Project Creation Failed" in result.output
    assert "Not a directory" in result.output or "not a directory" in result.output

    assert blocking_file.exists()
    assert not (tmp_path / "taken" / "my_app").exists()
