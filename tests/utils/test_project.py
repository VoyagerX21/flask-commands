from importlib.metadata import PackageNotFoundError
from flask_commands.utils.project import read_project_version


def test_read_project_version_returns_installed_version(monkeypatch):
    monkeypatch.setattr(
        "flask_commands.utils.project.version",
        lambda _package_name: "1.2.3",
    )

    assert read_project_version() == "1.2.3"


def test_read_project_version_falls_back_when_package_metadata_is_missing(monkeypatch):
    def fake_version(_package_name: str) -> str:
        raise PackageNotFoundError

    monkeypatch.setattr("flask_commands.utils.project.version", fake_version)

    assert read_project_version() == "0.0.0"
