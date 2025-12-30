import pytest
from click import ClickException
from flask_commands.utils.databases import install_sqlitedb


def test_install_sqlitedb_raises_when_flask_missing(tmp_path):
    project_path = tmp_path / "proj"
    project_path.mkdir()

    with pytest.raises(ClickException, match="venv/bin/flask not found"):
        install_sqlitedb(project_path)
