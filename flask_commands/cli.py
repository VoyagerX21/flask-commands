import click
from flask_commands.commands.new import new

@click.group()
def cli() -> None:
    """Flask Artisan-style command line tools."""
    print("I'm working")

cli.add_command(new)
