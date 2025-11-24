import click

@click.command()
@click.argument("project_name")
def new(project_name):
    click.echo(f"creating project {project_name}")
