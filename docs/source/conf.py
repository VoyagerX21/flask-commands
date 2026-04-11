import os
import sys

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "_ext")))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_copybutton",
    "youtube_embed",
]

exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "logo": {
        "text": "Flask-Commands",
        "image_light": "_static/flask-commands-logo.png",
        "image_dark": "_static/flask-commands-logo.png",
    },
    # Core layout
    "navbar_align": "left",
    "show_prev_next": True,
    "navigation_with_keys": True,
    "collapse_navigation": False,
    "navigation_depth": 4,
    "show_nav_level": 1,
    "show_toc_level": 2,
    "back_to_top_button": True,

    # Header layout
    "navbar_start": ["navbar-logo"],
    "navbar_center": [],
    "navbar_persistent": [],
    "navbar_end": ["navbar-nav", "search-button-field", "theme-switcher", "navbar-icon-links"],

    # Article header and right sidebar
    "article_header_start": ["breadcrumbs"],
    "article_header_end": [],
    "secondary_sidebar_items": {
        "**": ["page-toc"],
        "index": [],
    },

    # Search
    "search_bar_text": "Search Flask-Commands docs...",

    # Header links
    "external_links": [],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/drewbutcher/flask-commands",
            "icon": "fa-brands fa-github",
        },
    ],

    # Branding / UX cleanup
    "header_links_before_dropdown": 6,
}

html_context = {
    "github_user": "drewbutcher",
    "github_repo": "flask-commands",
    "github_version": "main",
    "doc_path": "docs/source/",
}

html_show_sphinx = False
html_logo = "_static/flask-commands-logo.png"
html_favicon = "_static/flask-commands-logo.png"
html_static_path = ["_static"]
html_css_files = ["theme-overrides.css", "video-library.css"]
html_js_files = [
    "video-library.js",
    "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"]
html_sidebars = {
    "index": [],
}

source_suffix = {'.rst': 'restructuredtext'}

def setup(app):
    app.add_js_file(
        None,
        body="""
const style = document.createElement("style");
style.type = "text/tailwindcss";
style.textContent = `
@custom-variant dark (&:where([data-theme="dark"], [data-theme="dark"] *));
`;
document.head.appendChild(style);
""",
        priority=700,
    )
