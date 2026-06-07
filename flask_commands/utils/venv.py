import os
import sys
import click
import subprocess
from typing import Optional, Iterable
from .files import file_write_file

def create_venv(project_path: str, packages: Optional[Iterable[str]] = None, freeze_requirements: bool = False) -> str:
    """
    Create a virtual environment at <project_path>/venv using the current
    Python interpreter. If `packages` is provided, install them into the
    new venv using the venv's pip.

    Args:
        project_path (str): Directory where the venv should be created.
        packages (Optional[Iterable[str]]): Package names to install in the venv.
        freeze_requirements (bool): Whether to write requirements.txt from `pip freeze`.

    Returns:
        str: Path to the created virtual environment.

    Examples:
        >>> create_venv("/tmp/myapp", packages=None, freeze_requirements=False)
        '/tmp/myapp/venv'
    """
    # Ensure the project directory exists
    os.makedirs(project_path, exist_ok=True)

    venv_dir = os.path.join(project_path, "venv")
    subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    if packages:
        _pip_install_in_venv(venv_dir, packages)

    if freeze_requirements:
        _write_requirements_from_venv(venv_dir, project_path)

    return venv_dir


def venv_executable(venv_dir: str, name: str) -> str:
    """
    Return the path to an executable inside a virtual environment.

    Virtual environments store command-line executables in different
    directories depending on the operating system. On Windows they live in
    the ``Scripts`` directory and usually use an ``.exe`` suffix. On POSIX
    systems such as macOS and Linux they live in the ``bin`` directory.

    Args:
        venv_dir: Path to the virtual environment directory.
        name: Executable name without any platform-specific suffix.

    Returns:
        The platform-specific path to the requested virtualenv executable.
    """
    scripts_dir = "Scripts" if _is_windows() else "bin"
    executable = f"{name}.exe" if _is_windows() else name
    return os.path.join(venv_dir, scripts_dir, executable)

def _is_windows() -> bool:
    return os.name == "nt"

def _pip_install_in_venv(venv_dir: str, packages):
    """
    Install packages into an existing virtual environment using its pip.

    Args:
        venv_dir (str): Path to the virtual environment directory.
        packages (Iterable[str]): Packages to install.

    Returns:
        None

    Examples:
        >>> _pip_install_in_venv("/tmp/myapp/venv", ["flask"])
        None
    """
    click.secho("Installing Python Dependencies...", bold=True)
    pip_path = venv_executable(venv_dir, "pip")
    subprocess.run([pip_path, "install", *packages], check=True, capture_output=True, text=True)
    click.secho("    - ✅ Success: Python Dependencies Installed", fg="green")

def _write_requirements_from_venv(venv_dir: str, project_path: str):
    """
    Run `pip freeze` inside the venv and write the output to
    `<project_path>/requirements.txt`.

    Args:
        venv_dir (str): Path to the virtual environment directory.
        project_path (str): Project directory where requirements.txt is written.

    Returns:
        None

    Examples:
        >>> _write_requirements_from_venv("/tmp/myapp/venv", "/tmp/myapp")
        None
    """
    pip_path = venv_executable(venv_dir, "pip")

    # Capture pip freeze output
    requirements_content = \
        subprocess.check_output([pip_path, "freeze"], text=True).splitlines()

    requirements_path = os.path.join(project_path, "requirements.txt")

    file_write_file(requirements_path, requirements_content)
