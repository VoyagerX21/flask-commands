from click.testing import CliRunner
from flask_commands.commands.new import new

def test_new_command_creates_project_with_db(tmp_path, monkeypatch):
    """When I run 'new my_app' in an empty directory, the command should
    succeed and create a folder called my_app"""
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(new, ["my_app"], input="y\n")

    assert result.exit_code == 0
    assert (tmp_path / "my_app").exists()
    assert (tmp_path / "my_app" / "app" / "models").is_dir()

    app_init = (tmp_path / "my_app" / "app" / "__init__.py").read_text()
    assert "from app import models" in app_init

def test_new_command_creates_project_without_db(tmp_path, monkeypatch):
    """When I run 'new my_app' in an empty directory, the command should
    succeed and create a folder called my_app"""
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(new, ["my_app"], input="n\n")

    assert result.exit_code == 0
    assert (tmp_path / "my_app").exists()
    assert not (tmp_path / "my_app" / "app" / "models").exists()

    app_init = (tmp_path / "my_app" / "app" / "__init__.py").read_text()
    assert "from app import models" not in app_init

def test_new_command_fails_if_project_exists(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    # Pre-create the project directory
    (tmp_path / "existing_project").mkdir()

    result = runner.invoke(new, ["existing_project"])

    assert result.exit_code == 0
    assert "already exists" in result.output

def test_new_command_cleans_up_on_exception(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("flask_commands.commands.new.create_venv", boom)

    result = runner.invoke(new, ["broken_project"], input="y\n")

    assert result.exit_code == 1
    assert not (tmp_path / "broken_project").exists()
    assert "Project Creation Failed" in result.output
    assert "boom" in result.output
