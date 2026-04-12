import click

from flask_commands.utils.project import read_project_version


@click.group(name="commands")
@click.version_option(
    read_project_version(),
    "-v",
    "--version",
    prog_name="flask-commands",
    message="%(prog)s %(version)s",
)
def commands() -> None:
    """Utilities for the flask-commands plugin."""
    pass
