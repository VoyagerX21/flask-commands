from importlib.metadata import PackageNotFoundError, version


def read_project_version() -> str:
    try:
        return version("flask-commands")
    except PackageNotFoundError:
        return "0.0.0"