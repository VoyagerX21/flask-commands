import pytest
import flask_commands.utils.wirings as wirings_module
from flask_commands.utils.wirings import wire_controller_route_view


@pytest.fixture
def project(tmp_path, monkeypatch):
    project_root = tmp_path

    app_dir = project_root / "app"
    controllers_dir = app_dir / "controllers"
    routes_dir = app_dir / "routes" / "mains"
    templates_dir = app_dir / "templates" / "mains"

    controllers_dir.mkdir(parents=True)
    routes_dir.mkdir(parents=True)
    templates_dir.mkdir(parents=True)

    (app_dir / "__init__.py").write_text(
        "from flask import Flask\n"
        "from config import config\n"
        "\n"
        "def create_app(config_name) -> Flask:\n"
        "    app = Flask(__name__)\n"
        "    app.config.from_object(config[config_name])\n"
        "\n"
        "    from app.routes.mains import bp as mains_blueprint\n"
        "    app.register_blueprint(mains_blueprint)\n"
        "\n"
        "    return app\n",
        encoding="utf-8",
    )

    (controllers_dir / "__init__.py").write_text(
        "from .main_controller import MainController\n",
        encoding="utf-8",
    )

    (controllers_dir / "main_controller.py").write_text(
        "from flask import render_template\n"
        "\n"
        "class MainController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('mains/index.html')\n",
        encoding="utf-8",
    )

    (routes_dir / "__init__.py").write_text(
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('mains', __name__)\n"
        "\n"
        "from app.routes.mains import routes\n",
        encoding="utf-8",
    )

    (routes_dir / "routes.py").write_text(
        "from app.controllers import MainController\n"
        "from app.routes.mains import bp\n"
        "\n"
        "@bp.route('/', methods=['GET'])\n"
        "def index():\n"
        "    return MainController.index()\n",
        encoding="utf-8",
    )

    (templates_dir / "index.html").write_text(
        "<h1>Index</h1>\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(project_root)
    return project_root

def test_wire_controller_route_view_root_action_updates_mains_files(project):
    main_controller_file = project / "app" / "controllers" / "main_controller.py"
    mains_routes_file = project / "app" / "routes" / "mains" / "routes.py"
    controllers_init_file = project / "app" / "controllers" / "__init__.py"

    is_successful, messages = wire_controller_route_view(
        relative_path="",
        action="landing",
        controller_name="MainController",
        route_name="/landing",
    )

    observed_controller_content = main_controller_file.read_text(encoding="utf-8")
    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class MainController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('mains/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def landing() -> str:\n"
        "        return render_template('landing.html')"
    )

    observed_routes_content = mains_routes_file.read_text(encoding="utf-8")
    expected_routes_content = (
        "from app.controllers import MainController\n"
        "from app.routes.mains import bp\n"
        "\n"
        "@bp.route('/', methods=['GET'])\n"
        "def index():\n"
        "    return MainController.index()\n"
        "\n"
        "@bp.route('/landing', methods=['GET'])\n"
        "def landing():\n"
        "    return MainController.landing()\n"
    )

    observed_messages = "\n".join(messages)
    observed_controllers_init_content = controllers_init_file.read_text(encoding="utf-8")
    expected_controllers_init_content = (
        "from .main_controller import MainController\n"
    )

    assert is_successful is True
    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert observed_controllers_init_content == expected_controllers_init_content
    assert "url_for('mains.landing')" in observed_messages
    assert not (project / "app" / "controllers" / "landing_controller.py").exists()
    assert not (project / "app" / "routes" / "landing").exists()

def test_wire_controller_route_view_root_action_uses_mains_template_when_requested(project):
    main_controller_file = project / "app" / "controllers" / "main_controller.py"
    mains_routes_file = project / "app" / "routes" / "mains" / "routes.py"

    is_successful, messages = wire_controller_route_view(
        relative_path="",
        action="landing",
        controller_name="MainController",
        route_name="/landing",
        is_view_directory_mains=True,
    )

    observed_controller_content = main_controller_file.read_text(encoding="utf-8")
    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class MainController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('mains/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def landing() -> str:\n"
        "        return render_template('mains/landing.html')"
    )

    observed_routes_content = mains_routes_file.read_text(encoding="utf-8")
    expected_routes_content = (
        "from app.controllers import MainController\n"
        "from app.routes.mains import bp\n"
        "\n"
        "@bp.route('/', methods=['GET'])\n"
        "def index():\n"
        "    return MainController.index()\n"
        "\n"
        "@bp.route('/landing', methods=['GET'])\n"
        "def landing():\n"
        "    return MainController.landing()\n"
    )

    observed_messages = "\n".join(messages)

    assert is_successful is True
    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert (project / "app" / "templates" / "mains" / "landing.html").exists()
    assert not (project / "app" / "templates" / "landing.html").exists()
    assert "app/templates/mains/landing.html" in observed_messages
    assert "url_for('mains.landing')" in observed_messages


def test_wire_controller_route_view_root_action_keeps_root_template_when_mains_not_requested(project):
    main_controller_file = project / "app" / "controllers" / "main_controller.py"
    mains_routes_file = project / "app" / "routes" / "mains" / "routes.py"

    is_successful, messages = wire_controller_route_view(
        relative_path="",
        action="landing",
        controller_name="MainController",
        route_name="/landing",
        is_view_directory_mains=False,
    )

    observed_controller_content = main_controller_file.read_text(encoding="utf-8")
    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class MainController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('mains/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def landing() -> str:\n"
        "        return render_template('landing.html')"
    )

    observed_routes_content = mains_routes_file.read_text(encoding="utf-8")
    expected_routes_content = (
        "from app.controllers import MainController\n"
        "from app.routes.mains import bp\n"
        "\n"
        "@bp.route('/', methods=['GET'])\n"
        "def index():\n"
        "    return MainController.index()\n"
        "\n"
        "@bp.route('/landing', methods=['GET'])\n"
        "def landing():\n"
        "    return MainController.landing()\n"
    )

    observed_messages = "\n".join(messages)

    assert is_successful is True
    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert (project / "app" / "templates" / "landing.html").exists()
    assert not (project / "app" / "templates" / "mains" / "landing.html").exists()
    assert "app/templates/landing.html" in observed_messages
    assert "url_for('mains.landing')" in observed_messages


def test_wire_get_with_existing_controller_and_route(monkeypatch):
    calls = []

    monkeypatch.setattr(wirings_module, "route_http_method_for_action", lambda *_: "GET")
    monkeypatch.setattr(wirings_module.os.path, "exists", lambda *_: True)

    monkeypatch.setattr(
        wirings_module,
        "view_make_file",
        lambda path: (calls.append(("view", path)) or (True, "view successful")),
    )
    monkeypatch.setattr(
        wirings_module,
        "controller_add_method",
        lambda *args: (calls.append(("controller_add", args)) or (True, "controller successful")),
    )
    monkeypatch.setattr(
        wirings_module,
        "route_add_method",
        lambda *args: (calls.append(("route_add", args)) or (True, "route successful")),
    )

    is_successful, messages = wire_controller_route_view(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        route_name="/posts",
    )

    assert is_successful is True
    assert messages == ["view successful", "controller successful", "route successful"]
    assert calls[0][0] == "view"
    assert calls[1][0] == "controller_add"
    assert calls[2][0] == "route_add"

def test_wire_post_skips_view(monkeypatch):
    calls = []

    monkeypatch.setattr(wirings_module, "route_http_method_for_action", lambda *_: "POST")
    monkeypatch.setattr(wirings_module.os.path, "exists", lambda *_: True)

    monkeypatch.setattr(
        wirings_module,
        "view_make_file",
        lambda *_: (calls.append("view") or (True, "view successful")),
    )
    monkeypatch.setattr(
        wirings_module,
        "controller_add_method",
        lambda *args: (calls.append("controller_add") or (True, "controller successful")),
    )
    monkeypatch.setattr(
        wirings_module,
        "route_add_method",
        lambda *args: (calls.append("route_add") or (True, "route successful")),
    )

    is_successful, messages = wire_controller_route_view(
        relative_path="posts",
        action="store",
        controller_name="PostController",
        route_name="/posts",
    )

    assert is_successful is True
    assert messages == ["controller successful", "route successful"]
    assert "view" not in calls

def test_wire_uses_make_file_when_controller_missing(monkeypatch):
    calls = []

    monkeypatch.setattr(wirings_module, "route_http_method_for_action", lambda *_: "GET")

    def fake_exists(path):
        if path.endswith("app/controllers/post_controller.py"):
            return False
        if path.endswith("app/routes/posts"):
            return True
        return False

    monkeypatch.setattr(wirings_module.os.path, "exists", fake_exists)

    monkeypatch.setattr(
        wirings_module,
        "view_make_file",
        lambda *_: (True, "view successful"),
    )
    monkeypatch.setattr(
        wirings_module,
        "controller_make_file",
        lambda *args: (calls.append("controller_make") or (True, "controller successful")),
    )
    monkeypatch.setattr(
        wirings_module,
        "route_add_method",
        lambda *args: (True, "route successful"),
    )

    is_successful, messages = wire_controller_route_view(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        route_name="/posts",
    )

    assert is_successful is True
    assert "controller successful" in messages
    assert calls == ["controller_make"]

def test_wire_route_exception_sets_failure(monkeypatch):
    monkeypatch.setattr(wirings_module, "route_http_method_for_action", lambda *_: "GET")
    monkeypatch.setattr(wirings_module.os.path, "exists", lambda *_: True)

    monkeypatch.setattr(
        wirings_module,
        "view_make_file",
        lambda *_: (True, "view successful"),
    )
    monkeypatch.setattr(
        wirings_module,
        "controller_add_method",
        lambda *args: (True, "controller successful"),
    )

    def boom(*_):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(wirings_module, "route_add_method", boom)

    is_successful, messages = wire_controller_route_view(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        route_name="/posts",
    )

    assert is_successful is False
    assert "view successful" in messages
    assert "controller successful" in messages
    assert any("Error:" in msg for msg in messages)

def test_wire_creates_route_directory_when_missing(monkeypatch):
    monkeypatch.setattr(wirings_module, "route_http_method_for_action", lambda *_: "GET")

    def fake_exists(path):
        if path.endswith("app/controllers/post_controller.py"):
            return True  # so controller_add_method is used
        if path.endswith("app/routes/posts"):
            return False  # triggers route_write_directory_and_register_blueprint
        return False

    monkeypatch.setattr(wirings_module.os.path, "exists", fake_exists)

    monkeypatch.setattr(
        wirings_module,
        "view_make_file",
        lambda *_: (True, "view successful"),
    )
    monkeypatch.setattr(
        wirings_module,
        "controller_add_method",
        lambda *args: (True, "controller successful"),
    )
    monkeypatch.setattr(
        wirings_module,
        "route_write_directory_and_register_blueprint",
        lambda *args: (True, "route made"),
    )

    is_successful, messages = wire_controller_route_view(
        relative_path="posts",
        action="index",
        controller_name="PostController",
        route_name="/posts",
    )

    assert is_successful is True
    assert messages == ["view successful", "controller successful", "route made"]
