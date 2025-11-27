import os
import shutil
import subprocess
import json
import click
from flask_commands.utils import create_venv, copy_templates

@click.command()
@click.argument("project_name")
def new(project_name):
    """Create a new Flask project"""
    if os.path.exists(project_name):
        click.echo(f"Error: '{project_name}' already exists in this "
                    "directory.  Please pick a new name.")
        return

    os.makedirs(project_name)

    # Create a Virtual Enviroment and install dependancies and generate a requirments file
    dependencies = [
        "Flask",
        "python-dotenv",
        "python-slugify"
    ]
    create_venv(project_name, packages=dependencies, freeze_requirements=True)

    copy_templates(project_name, replacements={"project_name": project_name})

    # Make run.sh executable
    run_sh_path = os.path.join(project_name, "run.sh")
    os.chmod(run_sh_path, 0o755)

    # Install Tailwind CSS via npm in the project directory (dev dependency)
    if shutil.which("npm") is None:
        click.echo("npm not found on PATH; skipping Tailwind installation.")
        click.echo(f"To install later: cd {project_name} && npm install tailwindcss @tailwindcss/cli")
    else:
        try:
            click.echo("Installing Tailwind CSS (tailwindcss @tailwindcss/cli) via npm...")
            subprocess.run(["npm", "install", "tailwindcss", "@tailwindcss/cli"], check=True, cwd=project_name, capture_output=True, text=True)


            # Ensure package.json contains the build/watch scripts for Tailwind
            package_json_path = os.path.join(project_name, "package.json")
            tailwind_scripts = {
                "build:css": "npx @tailwindcss/cli -i ./app/static/src/input.css -o ./app/static/tailwind.min.css --watch --minify",
                "watch:css": "npx @tailwindcss/cli -i ./app/static/src/input.css -o ./app/static/tailwind.css --watch"
            }

            pkg = {}
            if os.path.exists(package_json_path):
                try:
                    with open(package_json_path, "r", encoding="utf-8") as f:
                        pkg = json.load(f)
                except Exception:
                    pkg = {}

            # Merge scripts (preserve existing scripts)
            existing_scripts = pkg.get("scripts", {}) if isinstance(pkg.get("scripts", {}), dict) else {}
            existing_scripts.update(tailwind_scripts)
            pkg["scripts"] = existing_scripts

            with open(package_json_path, "w", encoding="utf-8") as f:
                json.dump(pkg, f, indent=2)
            click.echo("Tailwind installed.")
        except subprocess.CalledProcessError as exc:
            click.echo(f"npm install failed: {exc}")

    click.echo("Your project is all ready!!! Run the following:")
    click.echo(f"1) cd {project_name}")
    click.echo(f"2) ./run.sh")
