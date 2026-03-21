import pytest
from flask_commands.utils.data_types import ScaffoldStatus
from flask_commands.utils.wirings import wiring_generate_wiring_result


@pytest.fixture
def project(tmp_path, monkeypatch):
    project_root = tmp_path

    app_dir = project_root / "app"
    controllers_dir = app_dir / "controllers"
    mains_routes_dir = app_dir / "routes" / "mains"
    posts_routes_dir = app_dir / "routes" / "posts"
    comments_routes_dir = app_dir / "routes" / "comments"
    mains_templates_dir = app_dir / "templates" / "mains"
    posts_templates_dir = app_dir / "templates" / "posts"

    controllers_dir.mkdir(parents=True)
    mains_routes_dir.mkdir(parents=True)
    posts_routes_dir.mkdir(parents=True)
    comments_routes_dir.mkdir(parents=True)
    mains_templates_dir.mkdir(parents=True)
    posts_templates_dir.mkdir(parents=True)

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
        "    from app.routes.posts import bp as posts_blueprint\n"
        "    app.register_blueprint(posts_blueprint)\n"
        "\n"
        "    from app.routes.comments import bp as comments_blueprint\n"
        "    app.register_blueprint(comments_blueprint)\n"
        "\n"
        "    return app\n",
        encoding="utf-8",
    )

    (controllers_dir / "__init__.py").write_text(
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n",
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

    (mains_routes_dir / "__init__.py").write_text(
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('mains', __name__)\n"
        "\n"
        "from app.routes.mains import routes\n",
        encoding="utf-8",
    )

    (controllers_dir / "post_controller.py").write_text(
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')\n",
        encoding="utf-8",
    )

    (mains_routes_dir / "routes.py").write_text(
        "from app.controllers import MainController\n"
        "from app.routes.mains import bp\n"
        "\n"
        "@bp.route('/', methods=['GET'])\n"
        "def index():\n"
        "    return MainController.index()\n",
        encoding="utf-8",
    )

    (posts_routes_dir / "__init__.py").write_text(
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('posts', __name__)\n"
        "\n"
        "from app.routes.posts import routes\n",
        encoding="utf-8",
    )

    (posts_routes_dir / "routes.py").write_text(
        "from app.controllers import PostController\n"
        "from app.routes.posts import bp\n"
        "\n"
        "@bp.route('/posts', methods=['GET'])\n"
        "def index():\n"
        "    return PostController.index()\n",
        encoding="utf-8",
    )

    (comments_routes_dir / "__init__.py").write_text(
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('comments', __name__)\n"
        "\n"
        "from app.routes.comments import routes\n",
        encoding="utf-8",
    )

    
    (comments_routes_dir / "routes.py").write_text(
        "from app.controllers import CommentController\n"
        "from app.routes.comments import bp\n",
        encoding="utf-8",
    )


    (mains_templates_dir / "index.html").write_text(
        "<h1>Index</h1>\n",
        encoding="utf-8",
    )

    (posts_templates_dir / "index.html").write_text(
        "<h1>Posts Index</h1>\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(project_root)
    return project_root

def test_wiring_generate_wiring_result_root_action_updates_mains_files(project):
    main_controller_file = project / "app" / "controllers" / "main_controller.py"
    mains_routes_file = project / "app" / "routes" / "mains" / "routes.py"
    controllers_init_file = project / "app" / "controllers" / "__init__.py"

    wiring_result = wiring_generate_wiring_result(
        relative_path="",
        action="landing",
        controller_name="MainController",
        route_name="/landing",
    )

    observed_messages = "\n".join(wiring_result.success_messages + wiring_result.warning_messages)

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


    observed_controllers_init_content = controllers_init_file.read_text(encoding="utf-8")
    expected_controllers_init_content = (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
    )

    assert wiring_result.action_result.is_successful is True
    assert wiring_result.action_result.view_status == ScaffoldStatus.ADDED
    assert wiring_result.action_result.route_status == ScaffoldStatus.ADDED
    assert wiring_result.controller_result is not None
    assert wiring_result.controller_result.is_successful is True
    assert wiring_result.route_result is None

    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert observed_controllers_init_content == expected_controllers_init_content

    assert wiring_result.action_result.view_file_path is not None
    assert (project / wiring_result.action_result.view_file_path).exists()
    assert "url_for('mains.landing')" in observed_messages
    assert not (project / "app" / "controllers" / "landing_controller.py").exists()
    assert not (project / "app" / "routes" / "landing").exists()

def test_generate_wiring_result_root_action_uses_mains_template_when_requested(project):
    main_controller_file = project / "app" / "controllers" / "main_controller.py"
    mains_routes_file = project / "app" / "routes" / "mains" / "routes.py"

    wiring_result = wiring_generate_wiring_result(
        relative_path="",
        action="landing",
        controller_name="MainController",
        route_name="/landing",
        is_view_directory_mains=True,
    )

    observed_messages = "\n".join(wiring_result.success_messages + wiring_result.warning_messages)

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

    assert wiring_result.action_result.is_successful is True
    assert wiring_result.action_result.view_status == ScaffoldStatus.ADDED
    assert wiring_result.action_result.route_status == ScaffoldStatus.ADDED
    assert wiring_result.controller_result is not None
    assert wiring_result.controller_result.is_successful is True
    assert wiring_result.route_result is None

    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert (project / "app" / "templates" / "mains" / "landing.html").exists()
    assert not (project / "app" / "templates" / "landing.html").exists()
    assert "app/templates/mains/landing.html" in observed_messages
    assert "url_for('mains.landing')" in observed_messages

def test_generate_wiring_result_root_action_keeps_root_template_when_mains_not_requested(project):
    main_controller_file = project / "app" / "controllers" / "main_controller.py"
    mains_routes_file = project / "app" / "routes" / "mains" / "routes.py"

    result = wiring_generate_wiring_result(
        relative_path="",
        action="landing",
        controller_name="MainController",
        route_name="/landing",
        is_view_directory_mains=False,
    )

    observed_messages = "\n".join(result.success_messages + result.warning_messages)


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

    assert result.action_result.is_successful is True
    assert result.action_result.view_status == ScaffoldStatus.ADDED
    assert result.action_result.route_status == ScaffoldStatus.ADDED
    assert result.controller_result is not None
    assert result.controller_result.is_successful is True
    assert result.route_result is None

    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert (project / "app" / "templates" / "landing.html").exists()
    assert not (project / "app" / "templates" / "mains" / "landing.html").exists()
    assert "app/templates/landing.html" in observed_messages
    assert "url_for('mains.landing')" in observed_messages

def test_generate_wiring_result_get_with_existing_controller_and_route(project):
    post_controller_file = project / "app" / "controllers" / "post_controller.py"
    post_routes_file = project / "app" / "routes" / "posts" / "routes.py"
    controllers_init_file = project / "app" / "controllers" / "__init__.py"

    result = wiring_generate_wiring_result(
        relative_path="posts",
        action="show",
        controller_name="PostController",
        route_name="/posts/<int:post_id>",
    )

    observed_messages = "\n".join(result.success_messages + result.warning_messages)

    observed_controller_content = post_controller_file.read_text(encoding="utf-8")
    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def show(post_id: int) -> str:\n"
        "        return render_template('posts/show.html')"
    )

    observed_routes_content = post_routes_file.read_text(encoding="utf-8")
    expected_routes_content = (
        "from app.controllers import PostController\n"
        "from app.routes.posts import bp\n"
        "\n"
        "@bp.route('/posts', methods=['GET'])\n"
        "def index():\n"
        "    return PostController.index()\n"
        "\n"
        "@bp.route('/posts/<int:post_id>', methods=['GET'])\n"
        "def show(post_id: int):\n"
        "    return PostController.show(post_id)\n"
    )

    observed_controllers_init_content = controllers_init_file.read_text(encoding="utf-8")
    expected_controllers_init_content = (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
    )

    assert result.action_result.is_successful is True
    assert result.action_result.view_status == ScaffoldStatus.ADDED
    assert result.action_result.route_status == ScaffoldStatus.ADDED
    assert result.action_result.view_file_path == "app/templates/posts/show.html"
    assert result.controller_result is not None
    assert result.controller_result.is_successful is True
    assert result.controller_result.methods_added == ["show"]
    assert result.route_result is None

    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert observed_controllers_init_content == expected_controllers_init_content
    assert (project / "app" / "templates" / "posts" / "show.html").exists()
    assert "app/templates/posts/show.html" in observed_messages
    assert "url_for('posts.show', post_id=1)" in observed_messages


def test_generate_wiring_result_post_skips_view(project):
    post_controller_file = project / "app" / "controllers" / "post_controller.py"
    post_routes_file = project / "app" / "routes" / "posts" / "routes.py"
    controllers_init_file = project / "app" / "controllers" / "__init__.py"

    result = wiring_generate_wiring_result(
        relative_path="posts",
        action="store",
        controller_name="PostController",
        route_name="/posts",
    )

    observed_messages = "\n".join(result.success_messages + result.warning_messages)

    observed_controller_content = post_controller_file.read_text(encoding="utf-8")
    expected_controller_content = (
        "from flask import render_template\n"
        "from flask import redirect, url_for\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def store() -> str:\n"
        "        return redirect(url_for('posts.index'))"
    )

    observed_routes_content = post_routes_file.read_text(encoding="utf-8")
    expected_routes_content = (
        "from app.controllers import PostController\n"
        "from app.routes.posts import bp\n"
        "\n"
        "@bp.route('/posts', methods=['GET'])\n"
        "def index():\n"
        "    return PostController.index()\n"
        "\n"
        "@bp.route('/posts', methods=['POST'])\n"
        "def store():\n"
        "    return PostController.store()\n"
    )

    observed_controllers_init_content = controllers_init_file.read_text(encoding="utf-8")
    expected_controllers_init_content = (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
    )

    assert result.action_result.is_successful is True
    assert result.action_result.view_status == ScaffoldStatus.SKIPPED
    assert result.action_result.route_status == ScaffoldStatus.ADDED
    assert result.action_result.view_file_path is None
    assert result.controller_result is not None
    assert result.controller_result.is_successful is True
    assert result.controller_result.methods_added == ["store"]
    assert result.route_result is None

    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert observed_controllers_init_content == expected_controllers_init_content
    assert not (project / "app" / "templates" / "posts" / "store.html").exists()
    assert "app/templates/posts/store.html" not in observed_messages
    assert "url_for('posts.store')" in observed_messages


def test_generate_wiring_result_uses_make_file_when_controller_missing(project):
    comments_routes_file = project / "app" / "routes" / "comments" / "routes.py"
    comment_controller_file = project / "app" / "controllers" / "comment_controller.py"
    controllers_init_file = project / "app" / "controllers" / "__init__.py"

    result = wiring_generate_wiring_result(
        relative_path="comments",
        action="index",
        controller_name="CommentController",
        route_name="/comments",
    )

    observed_messages = "\n".join(result.success_messages + result.warning_messages)

    observed_controller_content = comment_controller_file.read_text(encoding="utf-8")
    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class CommentController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('comments/index.html')\n"
    )

    observed_routes_content = comments_routes_file.read_text(encoding="utf-8")
    expected_routes_content = (
        "from app.controllers import CommentController\n"
        "from app.routes.comments import bp\n"
        "\n"
        "@bp.route('/comments', methods=['GET'])\n"
        "def index():\n"
        "    return CommentController.index()\n"
    )

    observed_controllers_init_content = controllers_init_file.read_text(encoding="utf-8")
    expected_controllers_init_content = (
        "from .main_controller import MainController\n"
        "from .post_controller import PostController\n"
        "from .comment_controller import CommentController\n"
    )

    assert result.action_result.is_successful is True
    assert result.action_result.view_status == ScaffoldStatus.ADDED
    assert result.action_result.route_status == ScaffoldStatus.ADDED
    assert result.action_result.view_file_path == "app/templates/comments/index.html"
    assert result.controller_result is not None
    assert result.controller_result.is_successful is True
    assert result.controller_result.methods_added == ["index"]
    assert result.route_result is None

    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert observed_controllers_init_content == expected_controllers_init_content
    assert (project / "app" / "templates" / "comments" / "index.html").exists()
    assert "app/templates/comments/index.html" in observed_messages
    assert "url_for('comments.index')" in observed_messages

def test_generate_wiring_result_route_exception_sets_failure(project, monkeypatch):
    post_controller_file = project / "app" / "controllers" / "post_controller.py"
    post_routes_file = project / "app" / "routes" / "posts" / "routes.py"

    def boom(*_args, **_kwargs):
        raise RuntimeError("kaboom")

    monkeypatch.setattr("flask_commands.utils.wirings.route_add_method", boom)

    result = wiring_generate_wiring_result(
        relative_path="posts",
        action="show",
        controller_name="PostController",
        route_name="/posts/<int:post_id>",
    )

    observed_messages = "\n".join(result.success_messages + result.warning_messages)

    observed_controller_content = post_controller_file.read_text(encoding="utf-8")
    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')\n"
        "\n"
        "    @staticmethod\n"
        "    def show(post_id: int) -> str:\n"
        "        return render_template('posts/show.html')"
    )

    observed_routes_content = post_routes_file.read_text(encoding="utf-8")
    expected_routes_content = (
        "from app.controllers import PostController\n"
        "from app.routes.posts import bp\n"
        "\n"
        "@bp.route('/posts', methods=['GET'])\n"
        "def index():\n"
        "    return PostController.index()\n"
    )

    assert result.action_result.is_successful is False
    assert result.action_result.view_status == ScaffoldStatus.ADDED
    assert result.action_result.route_status == ScaffoldStatus.SKIPPED
    assert result.controller_result is not None
    assert result.controller_result.is_successful is True
    assert result.route_result is None

    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert (project / "app" / "templates" / "posts" / "show.html").exists()
    assert "Error:" in observed_messages
    assert "kaboom" in observed_messages


# def test_wire_creates_route_directory_when_missing(monkeypatch):
#     monkeypatch.setattr(wirings_module, "route_http_method_for_action", lambda *_: "GET")

#     def fake_exists(path):
#         if path.endswith("app/controllers/post_controller.py"):
#             return True  # so controller_add_method is used
#         if path.endswith("app/routes/posts"):
#             return False  # triggers route_write_directory_and_register_blueprint
#         return False

#     monkeypatch.setattr(wirings_module.os.path, "exists", fake_exists)

#     monkeypatch.setattr(
#         wirings_module,
#         "view_make_file",
#         lambda *_: (True, "view successful"),
#     )
#     monkeypatch.setattr(
#         wirings_module,
#         "controller_add_method",
#         lambda *args: (True, "controller successful"),
#     )
#     monkeypatch.setattr(
#         wirings_module,
#         "route_write_directory_and_register_blueprint",
#         lambda *args: (True, "route made"),
#     )

#     is_successful, messages = wire_controller_route_view(
#         relative_path="posts",
#         action="index",
#         controller_name="PostController",
#         route_name="/posts",
#     )

#     assert is_successful is True
#     assert messages == ["view successful", "controller successful", "route made"]
