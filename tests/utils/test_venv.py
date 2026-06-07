import os
import flask_commands.utils.venv as venv_module
from flask_commands.utils.venv import (
    create_venv,
    venv_executable,
    _pip_install_in_venv,
    _write_requirements_from_venv
)

def test_create_venv_calls_check_call_and_returns_path(tmp_path, monkeypatch):
    calls = {"makedirs": None, "check_call": None}

    def fake_makedirs(path, exist_ok=False):
        calls["makedirs"] = (path, exist_ok)

    def fake_check_call(args):
        calls["check_call"] = args

    monkeypatch.setattr(venv_module.os, "makedirs", fake_makedirs)
    monkeypatch.setattr(venv_module.subprocess, "check_call", fake_check_call)
    monkeypatch.setattr(venv_module, "_pip_install_in_venv", lambda *_: None)
    monkeypatch.setattr(venv_module, "_write_requirements_from_venv", lambda *_: None)

    project_path = tmp_path / "proj"
    venv_path = create_venv(str(project_path))

    assert venv_path == os.path.join(str(project_path), "venv")
    assert calls["makedirs"] == (str(project_path), True)
    assert calls["check_call"][0].endswith("python")
    assert calls["check_call"][1:] == ["-m", "venv", venv_path]

def test_create_venv_installs_packages_and_freezes(tmp_path, monkeypatch):
    called = {"pip": None, "freeze": None}

    monkeypatch.setattr(venv_module.os, "makedirs", lambda *args, **kwargs: None)
    monkeypatch.setattr(venv_module.subprocess, "check_call", lambda *_: None)

    def fake_pip(venv_dir, packages):
        called["pip"] = (venv_dir, list(packages))

    def fake_freeze(venv_dir, project_path):
        called["freeze"] = (venv_dir, project_path)

    monkeypatch.setattr(venv_module, "_pip_install_in_venv", fake_pip)
    monkeypatch.setattr(venv_module, "_write_requirements_from_venv", fake_freeze)

    project_path = tmp_path / "proj"
    venv_path = create_venv(
        str(project_path),
        packages=["flask", "click"],
        freeze_requirements=True
    )

    assert called["pip"] == (venv_path, ["flask", "click"])
    assert called["freeze"] == (venv_path, str(project_path))

def test_venv_executable_uses_bin_on_posix(monkeypatch):
    monkeypatch.setattr(venv_module, "_is_windows", lambda: False)

    assert venv_executable("/tmp/myapp/venv", "pip") == os.path.join(
        "/tmp/myapp/venv",
        "bin",
        "pip",
    )


def test_venv_executable_uses_scripts_and_exe_on_windows(monkeypatch):
    monkeypatch.setattr(venv_module, "_is_windows", lambda: True)

    assert venv_executable(r"C:\Users\me\app\venv", "pip") == os.path.join(
        r"C:\Users\me\app\venv",
        "Scripts",
        "pip.exe",
    )

def test__pip_install_in_venv_runs_pip(monkeypatch):
    calls = []

    def fake_run(args, check, capture_output, text):
        calls.append((args, check, capture_output, text))

    monkeypatch.setattr(venv_module.subprocess, "run", fake_run)
    monkeypatch.setattr(venv_module.click, "secho", lambda *a, **k: None)

    _pip_install_in_venv("/tmp/myapp/venv", ["flask"])

    expected_pip = os.path.join("/tmp/myapp/venv", "bin", "pip")
    assert calls == [([expected_pip, "install", "flask"], True, True, True)]

def test__write_requirements_from_venv_writes_file(monkeypatch):
    monkeypatch.setattr(
        venv_module.subprocess,
        "check_output",
        lambda *a, **k: "flask==2.0.0\nclick==8.0.0\n"
    )

    written = {}

    def fake_write(path, contents):
        written["path"] = path
        written["contents"] = contents

    monkeypatch.setattr(venv_module, "file_write_file", fake_write)

    _write_requirements_from_venv("/tmp/myapp/venv", "/tmp/myapp")

    assert written["path"] == os.path.join("/tmp/myapp", "requirements.txt")
    assert written["contents"] == ["flask==2.0.0", "click==8.0.0"]
