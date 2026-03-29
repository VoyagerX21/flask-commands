import json
import flask_commands.utils.css as css_module
from flask_commands.utils.css import install_tailwind, _append_tailwind_scripts

def test_install_tailwind_skip_when_npm_missing(tmp_path, monkeypatch, capsys):
    project = tmp_path / "my_app"
    project.mkdir()

    monkeypatch.setattr("shutil.which", lambda _: None)

    install_tailwind("my_app")

    captured = capsys.readouterr()
    assert "npm not found on PATH" in captured.out

def test_install_tailwind_handles_npm_failure(tmp_path, monkeypatch, capsys):
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

def test_install_tailwind_success_calls_append_and_success_message(tmp_path, monkeypatch):
    monkeypatch.setattr(css_module.shutil, "which", lambda _: "/usr/bin/npm")
    monkeypatch.setattr(css_module.subprocess, "run", lambda *a, **k: None)

    called = {"append": None, "secho": []}

    def fake_append(path):
        called["append"] = path

    def fake_secho(message, **kwargs):
        called["secho"].append(message)

    monkeypatch.setattr(css_module, "_append_tailwind_scripts", fake_append)
    monkeypatch.setattr(css_module.click, "secho", fake_secho)

    css_module.install_tailwind(str(tmp_path))

    assert called["append"] == str(tmp_path)
    assert any("Success: Tailwind installed" in msg for msg in called["secho"])

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



def test__append_tailwind_scripts_creates_package_json_when_missing(tmp_path):
    project = tmp_path / "my_app"
    project.mkdir()

    package_json = project / "package.json"
    assert not package_json.exists()

    _append_tailwind_scripts(str(project))

    assert package_json.exists()

    data = json.loads(package_json.read_text(encoding="utf-8"))
    assert data["scripts"]["build:css"] == (
        "npx @tailwindcss/cli "
        "-i ./app/static/src/input.css "
        "-o ./app/static/tailwind.min.css "
        "--watch --minify"
    )
    assert data["scripts"]["watch:css"] == (
        "npx @tailwindcss/cli "
        "-i ./app/static/src/input.css "
        "-o ./app/static/tailwind.css --watch"
    )
