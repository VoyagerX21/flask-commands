import click
from flask_commands.commands.controller import make_controller
from flask_commands.commands.model import make_model
from flask_commands.commands.new import new
from flask_commands.commands.view import make_view
from flask_commands.utils.project import read_project_version

@click.group()
@click.version_option(
    read_project_version(),
    "-v",
    "--version",
    prog_name="flask",
    message="%(prog)s %(version)s",
)
def cli() -> None:
    """Flask command line tools that will help you build a flask application with blueprints quickly."""
    pass # pragma: no cover

# Add commands to the CLI
cli.add_command(new)
cli.add_command(make_controller)
cli.add_command(make_view)
cli.add_command(make_model)
