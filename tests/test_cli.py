from click.testing import CliRunner
from flask_commands.cli import cli

def test_cli_help():
    """Running `--help` should exit 0 and show the docstring."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Flask command line tools" in result.output

def test_commands_registered():
    """Ensure the expected commands are registered on the CLI group."""
    assert "new" in cli.commands
    assert "make:view" in cli.commands
