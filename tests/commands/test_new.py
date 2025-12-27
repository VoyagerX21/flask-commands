from click.testing import CliRunner
from flask_commands.commands.new import new

def test_new_command_creates_project(tmp_path, monkeypatch):
    """When I run 'new my_app' in an empty directory, the command should
    succeed and create a folder called my_app"""
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(new, ["my_app"])

    assert result.exit_code == 0
    assert (tmp_path / "my_app").exists()

def test_new_command_fails_if_project_exists(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    # Pre-create the project directory
    (tmp_path / "existing_project").mkdir()

    result = runner.invoke(new, ["existing_project"])

    assert result.exit_code == 0
    assert "already exists" in result.output
