import os
import subprocess
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

def test_new_command_skips_tailwind_when_npm_missing(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    # Hijack the create_venv and copy_template functions and replaces them
    # with a function that accepts anything and returns nothing.
    monkeypatch.setattr(
        "flask_commands.utils.venv.create_venv", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "flask_commands.utils.files.copy_templates", lambda *args, **kwargs: None)

    # Hijack shutil which and replace it with a function that returns None
    monkeypatch.setattr("shutil.which", lambda _: None)

    result = runner.invoke(new, ["my_app"])

    assert result.exit_code == 0
    assert (tmp_path / "my_app").exists()
    assert "npm not found on PATH" in result.output

def test_new_command_invalid_package_json(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        "flask_commands.utils.venv.create_venv", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "flask_commands.utils.files.copy_templates", lambda *args, **kwargs: None)

    # Fake npm install that writes a broken package.json
    def fake_run(*args, **kwargs):
        pkg_path = os.path.join("my_app", "package.json")
        with open(pkg_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", fake_run)
    result = runner.invoke(new, ["my_app"])
    assert result.exit_code == 0

# def test_new_handles_npm_install_failure(tmp_path, monkeypatch):
#     runner = CliRunner()
#     monkeypatch.chdir(tmp_path)

#     monkeypatch.setattr(
#         "flask_commands.utils.venv.create_venv", lambda *args, **kwargs: None)
#     monkeypatch.setattr(
#         "flask_commands.utils.files.copy_templates", lambda *args, **kwargs: None)

#     def fake_run(*args, **kwargs):
#         raise subprocess.CalledProcessError(1, "npm")

#     monkeypatch.setattr("subprocess.run", fake_run)
#     result = runner.invoke(new, ["my_app"])
#     assert "npm install failed" in result.output


