import os
import sys

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# If you use src-layout: sys.path.insert(0, os.path.abspath("../../src"))
# If not src-layout:
sys.path.insert(0, os.path.abspath("../.."))


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Flask-Commands'
copyright = '2026, Drew Butcher'
author = 'Drew Butcher'


def _read_project_data() -> dict:
    pyproject_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "pyproject.toml")
    )
    try:
        with open(pyproject_path, "rb") as pyproject_file:
            data = tomllib.load(pyproject_file)
        return data.get("project", {})
    except Exception:
        return {}


_project_data = _read_project_data()
release = _project_data.get("version", "0.0.0")
project_description = _project_data.get("description", "")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_theme_options = {
    "description": project_description,
    "github_user": "drewbutcher",
    "github_repo": "flask-commands",
    "github_button": True,
    "github_banner": True,
    "extra_nav_links": {
        "GitHub": "https://github.com/drewbutcher/flask-commands",
        "PyPI": "https://pypi.org/project/flask-commands/",
        "Changelog": "https://github.com/drewbutcher/flask-commands/releases",
    },
}
html_static_path = ['_static']
html_css_files = ["theme-overrides.css"]
source_suffix = ".rst"
