import os
import json
import click
import shutil
import subprocess

def install_tailwind(project_name):
    if shutil.which("npm") is None:
        click.echo("npm not found on PATH; skipping Tailwind installation.")
        click.echo("You will need to install npm on your system first and "
                   "then you can follow these directions to install tailwind")
        click.echo(f"To install later: cd {project_name} && npm install "
                   "tailwindcss @tailwindcss/cli")
        return
    try:
        click.echo("Installing Tailwind CSS (tailwindcss @tailwindcss/cli) via npm...")
        subprocess.run(
            ["npm", "install", "tailwindcss", "@tailwindcss/cli"],
            check=True,
            cwd=project_name,
            capture_output=True,
            text=True,
        )
        _append_tailwind_scripts(project_name)
        click.echo("Tailwind installed.")
    except subprocess.CalledProcessError as exc:
        click.echo(f"npm install failed: {exc}")


def _append_tailwind_scripts(project_name):
    package_json_path = os.path.join(project_name, "package.json")

    tailwind_scripts = {
        "build:css": (
            "npx @tailwindcss/cli "
            "-i ./app/static/src/input.css "
            "-o ./app/static/tailwind.min.css "
            "--watch --minify"
        ),
        "watch:css": (
            "npx @tailwindcss/cli "
            "-i ./app/static/src/input.css "
            "-o ./app/static/tailwind.css --watch"
        ),
    }

    pkg = {}

    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, "r", encoding="utf-8") as f:
                pkg = json.load(f)
        except Exception:
            pkg = {}

    scripts = pkg.get("scripts")
    if not isinstance(scripts, dict):
        scripts = {}

    scripts.update(tailwind_scripts)
    pkg["scripts"] = scripts

    with open(package_json_path, "w", encoding="utf-8") as f:
        json.dump(pkg, f, indent=2)
