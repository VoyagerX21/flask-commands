import os
import pytest
from click import ClickException
from flask_commands.utils.databases import install_sqlitedb
import flask_commands.utils.databases as databases_module

def test_install_sqlitedb_success(tmp_path, monkeypatch):
    project_path = tmp_path / "proj"
    (project_path / "venv" / "bin").mkdir(parents=True)
    (project_path / "venv" / "bin" / "flask").write_text("", encoding="utf-8")

    calls = []

    def fake_run(args, check, cwd, stdout, stderr):
        calls.append((args, check, cwd))

    monkeypatch.setattr(databases_module.subprocess, "run", fake_run)
    monkeypatch.setattr(databases_module.click, "secho", lambda *args, **kwargs: None)

    install_sqlitedb(project_path)

    venv_flask = os.path.join(project_path, "venv", "bin", "flask")
    assert calls == [
        ([venv_flask, "db", "init"], True, project_path),
        ([venv_flask, "db", "migrate", "-m", "Initial migration."], True, project_path),
        ([venv_flask, "db", "upgrade"], True, project_path),
    ]

def test_install_sqlitedb_raises_when_flask_missing(tmp_path, monkeypatch, capsys):
    project_path = tmp_path / "proj"
    project_path.mkdir()

    with pytest.raises(ClickException, match="venv/bin/flask not found"):
        install_sqlitedb(project_path)

    captured = capsys.readouterr()
    assert "Setting up sqlite database for development..." in captured.out

