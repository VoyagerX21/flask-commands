import click
from flask_commands.commands.new import new

@click.group()
def cli() -> None:
    """Flask command line tools that will help you build a flask application with blueprints quickly."""
    pass

cli.add_command(new)
