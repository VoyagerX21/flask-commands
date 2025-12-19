from click.testing import CliRunner
from flask_commands.commands.new import new

def test_new_command_creates_project(tmp_path, monkeypatch):
    runner = CliRunner()

    monkeypatch.chdir(tmp_path)

    result = runner.invoke(new, ["my_app"])

    assert result.exit_code == 0
    assert (tmp_path / "my_app").exists()
