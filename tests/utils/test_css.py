import json
from flask_commands.utils.css import install_tailwind, _append_tailwind_scripts


def test_install_tailwind_skip_when_npm_missing(tmp_path, monkeypatch, capsys):
    project = tmp_path / "my_app"
    project.mkdir()

    monkeypatch.setattr("shutil.which", lambda _: None)

    install_tailwind("my_app")

    captured = capsys.readouterr()
    assert "npm not found on PATH" in captured.out


def test_install_tailwind_handles_npm_failure(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/npm")

    import subprocess

    def fake_run(*a, **k):
        raise subprocess.CalledProcessError(1, a[0])

    monkeypatch.setattr(subprocess, "run", fake_run)

    from flask_commands.commands.new import install_tailwind
    install_tailwind("my_app")

    out = capsys.readouterr().out
    assert "npm install failed" in out


def test__append_tailwind_scripts_merges_scripts(tmp_path):
    project = tmp_path / "my_app"
    project.mkdir()

    package_json = project / "package.json"
    package_json.write_text(
        json.dumps({"scripts": {"start": "node app.js"}}),
        encoding="utf-8",
    )

    _append_tailwind_scripts(str(project))

    data = json.loads(package_json.read_text(encoding="utf-8"))

    assert data["scripts"]["start"] == "node app.js"
    assert "build:css" in data["scripts"]
    assert "watch:css" in data["scripts"]


def test__append_tailwind_scripts_invalid_json(tmp_path):
    project = tmp_path / "my_app"
    project.mkdir()

    package_json = project / "package.json"
    package_json.write_text("{ not valid json }", encoding="utf-8")

    _append_tailwind_scripts(str(project))

    data = json.loads(package_json.read_text(encoding="utf-8"))
    assert "build:css" in data["scripts"]
    assert "watch:css" in data["scripts"]

