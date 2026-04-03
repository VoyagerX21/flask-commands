import os
import pytest
from flask_commands.utils.data_types import ScaffoldStatus
import flask_commands.utils.routes as routes_module
from flask_commands.utils.routes import (
    route_add_method,
    route_generate_parameter_reference,
    route_generate_route_name,
    route_generate_route_name_with_model_prompt,
    route_http_method_for_action,
    route_write_directory_and_register_blueprint,
    route_parse_route_name_for_params_and_types,
    _generate_minimal_route_routes,
    _generate_prompt_plan,
    _generate_route_spec,
    _register_blueprint_in_parent,
    _register_top_level_blueprint_in_app,
    _write_parent_route_directory,
    _write_parent_routes,
    _write_routes_file)

@pytest.fixture
def model_builder(tmp_path, monkeypatch):
    project_root = tmp_path
    models_directory = project_root / "app" / "models"
    models_directory.mkdir(parents=True)
    models_init_file = models_directory / "__init__.py"
    models_init_file.write_text(
        "from .posts import Post\n"
        "from .comment import Comment\n"
        "from .shop_image import ShopImage\n",
        encoding="utf-8"
    )
    monkeypatch.chdir(project_root)

    return project_root

@pytest.fixture
def project(tmp_path, monkeypatch):
    project_root = tmp_path

    app_dir = project_root / "app"
    controllers_dir = app_dir / "controllers"
    routes_dir = app_dir / "routes"
    mains_routes_dir = routes_dir / "mains"
    templates_dir = app_dir / "templates" / "mains"

    controllers_dir.mkdir(parents=True)
    mains_routes_dir.mkdir(parents=True)
    templates_dir.mkdir(parents=True)

    (app_dir / "__init__.py").write_text(
        "from flask import Flask\n"
        "from config import config\n"
        "\n"
        "def create_app(config_name) -> Flask:\n"
        '    """Creates a Flask application Instance."""\n'
        "    app = Flask(__name__)\n"
        "\n"
        "    # apply configuration\n"
        "    app.config.from_object(config[config_name])\n"
        "\n"
        "    from app.routes.mains import bp as mains_blueprint\n"
        "    app.register_blueprint(mains_blueprint)\n"
        "\n"
        "    return app",
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

    (mains_routes_dir / "__init__.py").write_text(
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('mains', __name__)\n"
        "\n"
        "from app.routes.mains import routes\n",
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

    (templates_dir / "index.html").write_text(
        "<h1>Index</h1>\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(project_root)
    return project_root

def test_route_add_method_success(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)

    route_file = route_dir / "routes.py"
    
    route_file.write_text(
        "from app.controllers import UserController\n"
        "from app.routes.users import bp\n"
        "\n"
        "@bp.route('/users/<int:user_id>', methods=['GET'])\n"
        "def show(user_id: int):\n"
        "    return UserController.show(user_id)\n"
        , encoding="utf-8")

    monkeypatch.chdir(project_root)

    action_result, message = route_add_method(
        relative_path='users',
        action='index',
        route_directory_path='app/routes/users',
        route_name='/users',
        controller_name='UserController')
    
    observed_content = route_file.read_text(encoding="utf-8")
    expected_content = (
        "from app.controllers import UserController\n"
        "from app.routes.users import bp\n"
        "\n"
        "@bp.route('/users/<int:user_id>', methods=['GET'])\n"
        "def show(user_id: int):\n"
        "    return UserController.show(user_id)\n"
        "\n"
        "@bp.route('/users', methods=['GET'])\n"
        "def index():\n"
        "    return UserController.index()\n"
    )

    assert action_result.is_successful is True
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/users"
    assert action_result.route_status == ScaffoldStatus.ADDED
    assert "url_for('users.index')" in action_result.url_for_example
    assert "/users" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED
   
    assert observed_content == expected_content
    assert "Added Route To Existing Directory" in message
    assert "index" in message
    assert "app/routes/users/routes.py" in message
    assert "/users" in message
    assert "url_for('users.index')" in message

def test_route_add_method_function_already_exists(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)

    route_file = route_dir / "routes.py"
    route_file.write_text(
        "from app.controllers import UserController\n"
        "from app.routes.users import bp\n"
        "\n"
        "@bp.route('/users', methods=['GET'])\n"
        "def index():\n"
        "    return UserController.index()\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(project_root)

    observed_content_before = route_file.read_text(encoding="utf-8")

    action_result, message = route_add_method(
        relative_path="users",
        action="index",
        route_directory_path="app/routes/users",
        route_name="/users",
        controller_name="UserController",
    )

    observed_content_after = route_file.read_text(encoding="utf-8")
    expected_content = (
        "from app.controllers import UserController\n"
        "from app.routes.users import bp\n"
        "\n"
        "@bp.route('/users', methods=['GET'])\n"
        "def index():\n"
        "    return UserController.index()\n"
    )

    assert action_result.is_successful is False
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/users"
    assert action_result.route_status == ScaffoldStatus.WARNING
    assert "url_for('users.index')" in action_result.url_for_example
    assert "/users" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert observed_content_before == expected_content
    assert observed_content_after == expected_content

    assert "Could not update route file" in message
    assert "index" in message
    assert "already exists" in message
    assert "app/routes/users/routes.py" in message

def test_route_add_method_route_file_missing(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)

    route_file = route_dir / "routes.py"
    monkeypatch.chdir(project_root)

    action_result, message = route_add_method(
        relative_path="users",
        action="index",
        route_directory_path="app/routes/users",
        route_name="/users",
        controller_name="UserController",
    )

    assert route_file.exists() is False

    assert action_result.is_successful is False
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/users"
    assert action_result.route_status == ScaffoldStatus.WARNING
    assert "url_for('users.index')" in action_result.url_for_example
    assert "/users" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert "Could not update route file" in message
    assert "Could not find file" in message
    assert "app/routes/users/routes.py" in message

def test_route_add_method_exception(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("internal server error")

    monkeypatch.setattr(
        "flask_commands.utils.routes.file_append_file",
        boom,
    )

    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)

    route_file = route_dir / "routes.py"
    route_file.write_text(
        "from app.controllers import UserController\n"
        "from app.routes.users import bp\n"
        "\n"
        "@bp.route('/users/<int:user_id>', methods=['GET'])\n"
        "def show(user_id: int):\n"
        "    return UserController.show(user_id)\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(project_root)

    observed_content_before = route_file.read_text(encoding="utf-8")

    action_result, message = route_add_method(
        relative_path="users",
        action="index",
        route_directory_path="app/routes/users",
        route_name="/users",
        controller_name="UserController",
    )

    observed_content_after = route_file.read_text(encoding="utf-8")
    expected_content = (
        "from app.controllers import UserController\n"
        "from app.routes.users import bp\n"
        "\n"
        "@bp.route('/users/<int:user_id>', methods=['GET'])\n"
        "def show(user_id: int):\n"
        "    return UserController.show(user_id)\n"
    )

    assert action_result.is_successful is False
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/users"
    assert action_result.route_status == ScaffoldStatus.WARNING
    assert "url_for('users.index')" in action_result.url_for_example
    assert "/users" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert observed_content_before == expected_content
    assert observed_content_after == expected_content

    assert "Could not add route method" in message
    assert "index" in message
    assert "app/routes/users/routes.py" in message
    assert "internal server error" in message

def test_route_add_method_unexpected_exception_path(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(
        "flask_commands.utils.routes._generate_route_content",
        boom,
    )

    action_result, message = route_add_method(
        relative_path="users",
        action="index",
        route_directory_path="app/routes/users",
        route_name="/users",
        controller_name="UserController",
    )

    assert action_result.is_successful is False
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/users"
    assert action_result.route_status == ScaffoldStatus.ERROR
    assert "url_for('users.index')" in action_result.url_for_example
    assert "/users" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert "Failed to add method to route" in message
    assert "kaboom" in message

def test_route_add_method_root_relative_path_updates_mains_routes_file(project):
    route_file = project / "app" / "routes" / "mains" / "routes.py"

    action_result, message = route_add_method(
        relative_path="",
        action="landing",
        route_directory_path="app/routes/mains",
        route_name="/landing",
        controller_name="MainController",
    )

    observed_content = route_file.read_text(encoding="utf-8")
    expected_content = (
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

    assert action_result.is_successful is True
    assert action_result.action == "landing"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/landing"
    assert action_result.route_status == ScaffoldStatus.ADDED
    assert "url_for('mains.landing')" in action_result.url_for_example
    assert "/landing" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert observed_content == expected_content
    assert "Added Route To Existing Directory" in message
    assert "landing" in message
    assert "app/routes/mains/routes.py" in message
    assert "/landing" in message
    assert "url_for('mains.landing')" in message

def test_route_write_directory_returns_when_write_routes_step_fails(tmp_path, monkeypatch):
    project_root = tmp_path
    app_dir = project_root / "app"
    app_dir.mkdir(parents=True)
    (app_dir / "__init__.py").write_text(
        "from flask import Flask\n"
        "def create_app(config_name) -> Flask:\n"
        "    app = Flask(__name__)\n"
        "    return app\n",
        encoding="utf-8",
    )

    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)

    route_file = route_dir / "routes.py"
    route_file.write_text("# pre-existing route file\n", encoding="utf-8")
    observed_content_before = route_file.read_text(encoding="utf-8")

    monkeypatch.chdir(project_root)

    monkeypatch.setattr(routes_module.os, "makedirs", lambda *args, **kwargs: None)

    route_result, action_result, message = route_write_directory_and_register_blueprint(
        relative_path="users",
        action="index",
        route_directory_path="app/routes/users",
        route_name="/users",
        controller_name="UserController",
    )

    observed_content_after = route_file.read_text(encoding="utf-8")

    assert route_result.is_successful is False
    assert route_result.directory_status == ScaffoldStatus.WARNING
    assert route_result.route_init_path == "app/routes/users/__init__.py"
    assert route_result.route_file_path is None
    assert route_result.blueprint_name is None
    assert route_result.blueprint_registration_file_path is None

    assert action_result.is_successful is False
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/users"
    assert action_result.route_status == ScaffoldStatus.WARNING
    assert "url_for('users.index')" in action_result.url_for_example
    assert "/users" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert observed_content_before == "# pre-existing route file\n"
    assert observed_content_after == "# pre-existing route file\n"

    assert "Could not create route file" in message
    assert "app/routes/users/routes.py" in message
    assert "already exists" in message

def test_route_generate_parameter_reference_empty():
    assert route_generate_parameter_reference([]) == ""

def test_route_generate_parameter_reference_single_param():
    assert route_generate_parameter_reference(["post_id"]) == ", post_id=post_id"

def test_route_generate_parameter_reference_multiple_params():
    assert route_generate_parameter_reference(["post_id", "comment_id"]) == ", post_id=post_id, comment_id=comment_id"

def test_route_generate_route_name_strips_mains_namespace_from_public_url():
    assert route_generate_route_name(
        relative_path="mains",
        action="about",
        is_restful=False,
        relative_path_segments=["mains"],
        relative_path_segment_models=[]
    ) == "/about"

def test_route_generate_route_name_non_restful_last_segment_not_model():
    assert route_generate_route_name(
        relative_path="posts/reports",
        action="export_csv",
        is_restful=False,
        relative_path_segments=["posts", "reports"],
        relative_path_segment_models=["posts"],
    ) == "/posts/<int:post_id>/reports/export-csv"


def test_route_generate_route_name_empty_relative_path():
    assert route_generate_route_name(
        relative_path="",
        action="my_action",
        is_restful=False,
        relative_path_segments=[],
        relative_path_segment_models=[]
    ) == "/my-action"

def test_route_generate_route_name_non_restful_with_models():
    assert route_generate_route_name(
        relative_path="posts/comments",
        action="preview_action",
        is_restful=False,
        relative_path_segments=["posts", "comments"],
        relative_path_segment_models=["posts", "comments"]
    ) == "/posts/<int:post_id>/comments/<int:comment_id>/preview-action"

def test_route_generate_route_name_restful_last_segment_not_model():
    assert route_generate_route_name(
        relative_path="admin_panel/reports",
        action="index",
        is_restful=True,
        relative_path_segments=["admin_panel", "reports"],
        relative_path_segment_models=[]
    ) == "/admin-panel/reports/index"

def test_route_generate_route_name_restful_with_models():
    assert route_generate_route_name(
        relative_path="posts/comments",
        action="show",
        is_restful=True,
        relative_path_segments=["posts", "comments"],
        relative_path_segment_models=["posts", "comments"]
    ) == "/posts/<int:post_id>/comments/<int:comment_id>"

def test_route_generate_route_name_with_model_prompt_disabled(model_builder):
    route_name, model_name = route_generate_route_name_with_model_prompt(
        "admin.reports.index",
        False
    )

    assert route_name == "/admin/reports/index"
    assert model_name is None

def test_route_generate_route_name_with_model_prompt_accepts_missing_model(model_builder, monkeypatch):
    monkeypatch.setattr(
        "flask_commands.utils.routes.click.confirm",
        lambda *args, **kwargs: True
    )

    route_name, model_name = route_generate_route_name_with_model_prompt(
        "admin.reports.index",
        True
    )

    assert route_name == "/admin/reports"
    assert model_name == "Report"

def test_route_generate_route_name_with_model_prompt_declines_missing_model(model_builder, monkeypatch):
    monkeypatch.setattr(
        "flask_commands.utils.routes.click.confirm",
        lambda *args, **kwargs: False
    )

    route_name, model_name = route_generate_route_name_with_model_prompt(
        "admin.reports.index",
        True
    )

    assert route_name == "/admin/reports/index"
    assert model_name is None

def test_route_http_method_for_action_get_default():
    assert route_http_method_for_action("index") == "GET"

def test_route_http_method_for_action_get_show():
    assert route_http_method_for_action("show") == "GET"

def test_route_http_method_for_action_post_store():
    assert route_http_method_for_action("store") == "POST"

def test_route_http_method_for_action_post_update():
    assert route_http_method_for_action("update") == "POST"

def test_route_http_method_for_action_post_destroy():
    assert route_http_method_for_action("destroy") == "POST"

def test_route_http_method_for_action_post_delete():
    assert route_http_method_for_action("delete") == "POST"

def test_route_http_method_for_action_get_custom():
    assert route_http_method_for_action("custom_action") == "GET"

def test_route_write_directory_and_register_blueprint_success(project):
    app_init_file = project / "app" / "__init__.py"

    route_result, action_result, message = route_write_directory_and_register_blueprint(
        relative_path="users",
        action="index",
        route_directory_path="app/routes/users",
        route_name="/users",
        controller_name="UserController",
    )

    users_init_file = project / "app" / "routes" / "users" / "__init__.py"
    users_routes_file = project / "app" / "routes" / "users" / "routes.py"

    observed_users_init_content = users_init_file.read_text(encoding="utf-8")
    expected_users_init_content = (
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('users', __name__)\n"
        "\n"
        "from app.routes.users import routes\n"
    )

    observed_users_routes_content = users_routes_file.read_text(encoding="utf-8")
    expected_users_routes_content = (
        "from app.controllers import UserController\n"
        "from app.routes.users import bp\n"
        "\n"
        "@bp.route('/users', methods=['GET'])\n"
        "def index():\n"
        "    return UserController.index()\n"
    )

    observed_app_init_content = app_init_file.read_text(encoding="utf-8")
    expected_app_init_content = (
        "from flask import Flask\n"
        "from config import config\n"
        "\n"
        "def create_app(config_name) -> Flask:\n"
        '    """Creates a Flask application Instance."""\n'
        "    app = Flask(__name__)\n"
        "\n"
        "    # apply configuration\n"
        "    app.config.from_object(config[config_name])\n"
        "\n"
        "    from app.routes.mains import bp as mains_blueprint\n"
        "    app.register_blueprint(mains_blueprint)\n"
        "\n"
        "    from app.routes.users import bp as users_blueprint\n"
        "    app.register_blueprint(users_blueprint)\n"
        "\n"
        "    return app"
    )

    assert route_result.is_successful is True
    assert route_result.directory_status == ScaffoldStatus.ADDED
    assert route_result.route_init_path == "app/routes/users/__init__.py"
    assert route_result.route_file_path == "app/routes/users/routes.py"
    assert route_result.blueprint_name == "users_blueprint"
    assert route_result.blueprint_registration_file_path == "app/__init__.py"

    assert action_result.is_successful is True
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/users"
    assert action_result.route_status == ScaffoldStatus.ADDED
    assert "url_for('users.index')" in action_result.url_for_example
    assert "/users" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert observed_users_init_content == expected_users_init_content
    assert observed_users_routes_content == expected_users_routes_content
    assert observed_app_init_content == expected_app_init_content

    assert "Created New Route Directory" in message
    assert "app/routes/users/__init__.py" in message
    assert "app/routes/users/routes.py" in message
    assert "users_blueprint" in message
    assert "url_for('users.index')" in message

def test_route_write_directory_and_register_blueprint_success_nested_routes(project):
    app_init_file = project / "app" / "__init__.py"
    recipes_dir = project / "app" / "routes" / "recipes"
    recipes_dir.mkdir(parents=True)

    recipes_init_file = recipes_dir / "__init__.py"
    recipes_init_file.write_text(
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('recipes', __name__)\n"
        "\n"
        "from app.routes.recipes import routes\n",
        encoding="utf-8",
    )

    recipes_routes_file = recipes_dir / "routes.py"
    recipes_routes_file.write_text(
        "from app.routes.recipes import bp\n",
        encoding="utf-8",
    )

    route_result, action_result, message = route_write_directory_and_register_blueprint(
        relative_path="recipes/comments",
        action="index",
        route_directory_path="app/routes/recipes/comments",
        route_name="/recipes/<int:recipe_id>/comments",
        controller_name="RecipeCommentController",
    )

    comments_init_file = project / "app" / "routes" / "recipes" / "comments" / "__init__.py"
    comments_routes_file = project / "app" / "routes" / "recipes" / "comments" / "routes.py"

    observed_comments_init_content = comments_init_file.read_text(encoding="utf-8")
    expected_comments_init_content = (
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('comments', __name__)\n"
        "\n"
        "from app.routes.recipes.comments import routes\n"
    )

    observed_comments_routes_content = comments_routes_file.read_text(encoding="utf-8")
    expected_comments_routes_content = (
        "from app.controllers import RecipeCommentController\n"
        "from app.routes.recipes.comments import bp\n"
        "\n"
        "@bp.route('/recipes/<int:recipe_id>/comments', methods=['GET'])\n"
        "def index(recipe_id: int):\n"
        "    return RecipeCommentController.index(recipe_id)\n"
    )

    observed_recipes_init_content = recipes_init_file.read_text(encoding="utf-8")
    expected_recipes_init_content = (
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('recipes', __name__)\n"
        "\n"
        "from app.routes.recipes import routes\n"
        "\n"
        "from app.routes.recipes.comments import bp as recipes_comments_blueprint\n"
        "bp.register_blueprint(recipes_comments_blueprint)\n"
    )

    observed_recipes_routes_content = recipes_routes_file.read_text(encoding="utf-8")
    expected_recipes_routes_content = (
        "from app.routes.recipes import bp\n"
    )

    observed_app_init_content = app_init_file.read_text(encoding="utf-8")
    expected_app_init_content = (
        "from flask import Flask\n"
        "from config import config\n"
        "\n"
        "def create_app(config_name) -> Flask:\n"
        '    """Creates a Flask application Instance."""\n'
        "    app = Flask(__name__)\n"
        "\n"
        "    # apply configuration\n"
        "    app.config.from_object(config[config_name])\n"
        "\n"
        "    from app.routes.mains import bp as mains_blueprint\n"
        "    app.register_blueprint(mains_blueprint)\n"
        "\n"
        "    return app"
    )

    assert route_result.is_successful is True
    assert route_result.directory_status == ScaffoldStatus.ADDED
    assert route_result.route_init_path == "app/routes/recipes/comments/__init__.py"
    assert route_result.route_file_path == "app/routes/recipes/comments/routes.py"
    assert route_result.blueprint_name == "recipes_comments_blueprint"
    assert route_result.blueprint_registration_file_path == "app/routes/recipes/__init__.py"

    assert action_result.is_successful is True
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/recipes/<int:recipe_id>/comments"
    assert action_result.route_status == ScaffoldStatus.ADDED
    assert "url_for('recipes.comments.index', recipe_id=1)" in action_result.url_for_example
    assert "/recipes/1/comments" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert observed_comments_init_content == expected_comments_init_content
    assert observed_comments_routes_content == expected_comments_routes_content
    assert observed_recipes_init_content == expected_recipes_init_content
    assert observed_recipes_routes_content == expected_recipes_routes_content
    assert observed_app_init_content == expected_app_init_content

    assert "Created New Route Directory" in message
    assert "app/routes/recipes/comments/__init__.py" in message
    assert "app/routes/recipes/comments/routes.py" in message
    assert "recipes_comments_blueprint" in message
    assert "url_for('recipes.comments.index', recipe_id=1)" in message

def test_route_write_directory_and_register_blueprint_app_init_missing_return(tmp_path, monkeypatch):
    project_root = tmp_path
    app_dir = project_root / "app"
    app_dir.mkdir(parents=True)
    app_init_file = app_dir / "__init__.py"
    app_init_file.write_text(
        "from flask import Flask\n"
        "from config import config\n"
        "\n"
        "def create_app(config_name) -> Flask:\n"
        '    """Creates a Flask application Instance."""\n'
        "    app = Flask(__name__)\n"
        "\n"
        "    # apply configuration\n"
        "    app.config.from_object(config[config_name])\n"
        "\n"
        "    from app.routes.mains import bp as mains_blueprint\n"
        "    app.register_blueprint(mains_blueprint)\n",
        encoding="utf-8",
    )

    route_dir = project_root / "app" / "routes"
    route_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)

    route_result, action_result, message = route_write_directory_and_register_blueprint(
        relative_path="users",
        action="index",
        route_directory_path="app/routes/users",
        route_name="/users",
        controller_name="UserController",
    )

    users_init_file = project_root / "app" / "routes" / "users" / "__init__.py"
    users_routes_file = project_root / "app" / "routes" / "users" / "routes.py"

    observed_users_init_content = users_init_file.read_text(encoding="utf-8")
    expected_users_init_content = (
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('users', __name__)\n"
        "\n"
        "from app.routes.users import routes\n"
    )

    observed_users_routes_content = users_routes_file.read_text(encoding="utf-8")
    expected_users_routes_content = (
        "from app.controllers import UserController\n"
        "from app.routes.users import bp\n"
        "\n"
        "@bp.route('/users', methods=['GET'])\n"
        "def index():\n"
        "    return UserController.index()\n"
    )

    observed_app_init_content = app_init_file.read_text(encoding="utf-8")
    expected_app_init_content = (
        "from flask import Flask\n"
        "from config import config\n"
        "\n"
        "def create_app(config_name) -> Flask:\n"
        '    """Creates a Flask application Instance."""\n'
        "    app = Flask(__name__)\n"
        "\n"
        "    # apply configuration\n"
        "    app.config.from_object(config[config_name])\n"
        "\n"
        "    from app.routes.mains import bp as mains_blueprint\n"
        "    app.register_blueprint(mains_blueprint)\n"
    )

    assert route_result.is_successful is False
    assert route_result.directory_status == ScaffoldStatus.WARNING
    assert route_result.route_init_path == "app/routes/users/__init__.py"
    assert route_result.route_file_path == "app/routes/users/routes.py"
    assert route_result.blueprint_name is None
    assert route_result.blueprint_registration_file_path is None

    assert action_result.is_successful is False
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/users"
    assert action_result.route_status == ScaffoldStatus.WARNING
    assert "url_for('users.index')" in action_result.url_for_example
    assert "/users" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert observed_users_init_content == expected_users_init_content
    assert observed_users_routes_content == expected_users_routes_content
    assert observed_app_init_content == expected_app_init_content

    assert "Could not register blueprint" in message
    assert "return app" in message
    assert "app/__init__.py" in message


def test_route_write_directory_and_register_blueprint_route_already_exists(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)

    route_result, action_result, message = route_write_directory_and_register_blueprint(
        relative_path="users",
        action="index",
        route_directory_path="app/routes/users",
        route_name="/users",
        controller_name="UserController",
    )

    assert route_result.is_successful is False
    assert route_result.directory_status == ScaffoldStatus.ERROR
    assert route_result.route_init_path is None
    assert route_result.route_file_path is None
    assert route_result.blueprint_name is None
    assert route_result.blueprint_registration_file_path is None

    assert action_result.is_successful is False
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/users"
    assert action_result.route_status == ScaffoldStatus.ERROR
    assert "url_for('users.index')" in action_result.url_for_example
    assert "/users" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert "Failed to create route" in message
    assert "File exists" in message


def test_route_write_directory_and_register_blueprint_exception(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("motherboard failure")

    monkeypatch.setattr(
        "flask_commands.utils.routes.file_write_file",
        boom,
    )

    project_root = tmp_path
    monkeypatch.chdir(project_root)

    route_result, action_result, message = route_write_directory_and_register_blueprint(
        relative_path="users",
        action="index",
        route_directory_path="app/routes/users",
        route_name="/users",
        controller_name="UserController",
    )

    assert route_result.is_successful is False
    assert route_result.directory_status == ScaffoldStatus.WARNING
    assert route_result.route_init_path is None
    assert route_result.route_file_path is None
    assert route_result.blueprint_name is None
    assert route_result.blueprint_registration_file_path is None

    assert action_result.is_successful is False
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/users"
    assert action_result.route_status == ScaffoldStatus.WARNING
    assert "url_for('users.index')" in action_result.url_for_example
    assert "/users" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert "Could not create route init file" in message
    assert "app/routes/users/__init__.py" in message
    assert "motherboard failure" in message

def test_route_write_directory_parent_prep_failure_returns_grouped_updates(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    route_result, action_result, message = route_write_directory_and_register_blueprint(
        relative_path="recipes/comments",
        action="index",
        route_directory_path="app/routes/recipes/comments",
        route_name="/recipes/<int:recipe_id>/comments",
        controller_name="RecipeCommentController",
    )

    recipes_dir = tmp_path / "app" / "routes" / "recipes"
    recipes_init_file = recipes_dir / "__init__.py"
    recipes_routes_file = recipes_dir / "routes.py"
    comments_dir = tmp_path / "app" / "routes" / "recipes" / "comments"

    observed_recipes_init_content = recipes_init_file.read_text(encoding="utf-8")
    expected_recipes_init_content = (
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('recipes', __name__)\n"
        "\n"
        "from app.routes.recipes import routes\n"
    )

    observed_recipes_routes_content = recipes_routes_file.read_text(encoding="utf-8")
    expected_recipes_routes_content = (
        "from app.routes.recipes import bp\n"
    )

    assert route_result.is_successful is False
    assert route_result.directory_status == ScaffoldStatus.WARNING
    assert route_result.route_init_path is None
    assert route_result.route_file_path is None
    assert route_result.blueprint_name is None
    assert route_result.blueprint_registration_file_path is None

    assert action_result.is_successful is False
    assert action_result.action == "index"
    assert action_result.http_method == "GET"
    assert action_result.route_name == "/recipes/<int:recipe_id>/comments"
    assert action_result.route_status == ScaffoldStatus.WARNING
    assert "url_for('recipes.comments.index', recipe_id=1)" in action_result.url_for_example
    assert "/recipes/1/comments" in action_result.visit_example
    assert action_result.view_file_path is None
    assert action_result.view_status == ScaffoldStatus.SKIPPED

    assert recipes_dir.is_dir()
    assert observed_recipes_init_content == expected_recipes_init_content
    assert observed_recipes_routes_content == expected_recipes_routes_content
    assert not comments_dir.exists()

    assert "Could not prepare parent routes" in message
    assert "app/routes/recipes" in message
    assert "__init__.py" in message
    assert "routes.py" in message
    assert "app/__init__.py" in message

def test_route_parse_route_name_for_params_and_types_no_params():
    params_with_types, params = route_parse_route_name_for_params_and_types("/posts")
    assert params_with_types == []
    assert params == []

def test_route_parse_route_name_for_params_and_types_single_param():
    params_with_types, params = route_parse_route_name_for_params_and_types("/posts/<int:post_id>")
    assert params_with_types == ["post_id: int"]
    assert params == ["post_id"]

def test_route_parse_route_name_for_params_and_types_multiple_params():
    params_with_types, params = route_parse_route_name_for_params_and_types(
        "/recipes/<int:recipe_id>/comments/<int:comment_id>/images/<int:image_id>"
    )
    assert params_with_types == ["recipe_id: int", "comment_id: int", "image_id: int"]
    assert params == ["recipe_id", "comment_id", "image_id"]

def test_route_parse_route_name_for_params_and_types_ignores_untyped():
    params_with_types, params = route_parse_route_name_for_params_and_types(
        "/posts/<post_id>/comments/<int:comment_id>"
    )
    assert params_with_types == ["comment_id: int"]
    assert params == ["comment_id"]

def test_route_parse_route_name_for_params_and_types_str_param():
    params_with_types, params = route_parse_route_name_for_params_and_types(
        "/posts/<str:post_slug>"
    )
    assert params_with_types == ["post_slug: str"]
    assert params == ["post_slug"]

# Private Function Test
def test__generate_minimal_route_routes():
    assert _generate_minimal_route_routes("app/routes/users") == [
        "from app.routes.users import bp"
    ]
def test__generate_prompt_plan_missing_model_index(model_builder):
    route_spec = _generate_route_spec("admin.reports.index")
    prompt_plan = _generate_prompt_plan(route_spec)

    assert prompt_plan.missing_model is not None
    assert prompt_plan.missing_model.segment == "reports"
    assert prompt_plan.missing_model.model_name == "Report"
    assert prompt_plan.route_structure is not None
    assert prompt_plan.route_structure.accepted_route == "/admin/reports"
    assert prompt_plan.route_structure.declined_route == "/admin/reports/index"

def test__generate_prompt_plan_missing_model_show(model_builder):
    route_spec = _generate_route_spec("admin.reports.show")
    prompt_plan = _generate_prompt_plan(route_spec)

    assert prompt_plan.missing_model is not None
    assert prompt_plan.missing_model.segment == "reports"
    assert prompt_plan.missing_model.model_name == "Report"
    assert prompt_plan.route_structure is not None
    assert prompt_plan.route_structure.accepted_route == "/admin/reports/<int:report_id>"
    assert prompt_plan.route_structure.declined_route == "/admin/reports/show"

def test__generate_prompt_plan_empty_relative_path(model_builder):
    route_spec = _generate_route_spec("index")
    prompt_plan = _generate_prompt_plan(route_spec)

    assert prompt_plan.missing_model is None
    assert prompt_plan.route_structure is None

def test__generate_prompt_plan_non_restful(model_builder):
    route_spec = _generate_route_spec("posts.custom_action")
    prompt_plan = _generate_prompt_plan(route_spec)

    assert prompt_plan.missing_model is None
    assert prompt_plan.route_structure is None

def test__generate_prompt_plan_last_segment_is_model(model_builder):
    route_spec = _generate_route_spec("posts.show")
    prompt_plan = _generate_prompt_plan(route_spec)

    assert prompt_plan.missing_model is None
    assert prompt_plan.route_structure is None

def test__generate_route_spec_landing(model_builder):
    spec = _generate_route_spec("landing")

    assert spec.dotted_path_with_action == 'landing'
    assert spec.relative_path == ""
    assert spec.action == "landing"
    assert spec.is_restful is False
    assert spec.relative_path_segments == ()
    assert spec.relative_path_segment_models == ()
    assert spec.registered_models == ("Comment", "Post", "ShopImage")
    assert spec.registered_snake_models == ("comment", "post", "shop_image")
    assert spec.generated_route_name == "/landing"

def test__generate_route_spec_index_empty_relative_path(model_builder):
    spec = _generate_route_spec("index")

    assert spec.dotted_path_with_action == 'index'
    assert spec.relative_path == ""
    assert spec.action == "index"
    assert spec.is_restful is True
    assert spec.relative_path_segments == ()
    assert spec.relative_path_segment_models == ()
    assert spec.registered_models == ("Comment", "Post", "ShopImage")
    assert spec.registered_snake_models == ("comment", "post", "shop_image")
    assert spec.generated_route_name == "/index"

def test__generate_route_spec_posts_show(model_builder):
    spec = _generate_route_spec("posts.show")

    assert spec.dotted_path_with_action == 'posts.show'
    assert spec.relative_path == "posts"
    assert spec.action == "show"
    assert spec.is_restful is True
    assert spec.relative_path_segments == ('posts',)
    assert spec.relative_path_segment_models == ('posts',)
    assert spec.registered_models == ("Comment", "Post", "ShopImage")
    assert spec.registered_snake_models == ("comment", "post", "shop_image")
    assert spec.generated_route_name == "/posts/<int:post_id>"

def test__generate_route_spec_admin_posts_comments_show(model_builder):
    spec = _generate_route_spec("admin.posts.comments.show")

    assert spec.dotted_path_with_action == "admin.posts.comments.show"
    assert spec.relative_path == "admin/posts/comments"
    assert spec.action == "show"
    assert spec.is_restful is True
    assert spec.relative_path_segments == ("admin", "posts", "comments")
    assert spec.relative_path_segment_models == ('posts',"comments")
    assert spec.registered_models == ("Comment", "Post", "ShopImage")
    assert spec.registered_snake_models == ("comment", "post", "shop_image")
    assert spec.generated_route_name == "/admin/posts/<int:post_id>/comments/<int:comment_id>"

def test__generate_route_spec_admin_shop_images_show(model_builder):
    spec = _generate_route_spec("admin.shop_images.show")

    assert spec.dotted_path_with_action == "admin.shop_images.show"
    assert spec.relative_path == "admin/shop_images"
    assert spec.action == "show"
    assert spec.is_restful is True
    assert spec.relative_path_segments == ("admin", "shop_images")
    assert spec.relative_path_segment_models == ('shop_images',)
    assert spec.registered_models == ("Comment", "Post", "ShopImage")
    assert spec.registered_snake_models == ("comment", "post", "shop_image")
    assert spec.generated_route_name == "/admin/shop-images/<int:shop_image_id>"

def test__generate_route_spec_posts_custom_action(model_builder):
    spec = _generate_route_spec("posts.custom_action")

    assert spec.dotted_path_with_action == "posts.custom_action"
    assert spec.relative_path == "posts"
    assert spec.action == "custom_action"
    assert spec.is_restful is False
    assert spec.relative_path_segments == ("posts", )
    assert spec.relative_path_segment_models == ('posts',)
    assert spec.registered_models == ("Comment", "Post", "ShopImage")
    assert spec.registered_snake_models == ("comment", "post", "shop_image")
    assert spec.generated_route_name == "/posts/<int:post_id>/custom-action"

def test__generate_route_spec_posts_custom_action_again(model_builder):
    spec = _generate_route_spec("posts.custom-action")

    assert spec.dotted_path_with_action == "posts.custom-action"
    assert spec.relative_path == "posts"
    assert spec.action == "custom-action"
    assert spec.is_restful is False
    assert spec.relative_path_segments == ("posts", )
    assert spec.relative_path_segment_models == ('posts',)
    assert spec.registered_models == ("Comment", "Post", "ShopImage")
    assert spec.registered_snake_models == ("comment", "post", "shop_image")
    assert spec.generated_route_name == "/posts/<int:post_id>/custom-action"

def test__generate_route_spec_admin_reports_index_no_models(model_builder):
    spec = _generate_route_spec("admin.reports.index")

    assert spec.dotted_path_with_action == "admin.reports.index"
    assert spec.relative_path == "admin/reports"
    assert spec.action == "index"
    assert spec.is_restful is True
    assert spec.relative_path_segments == ("admin", "reports" )
    assert spec.relative_path_segment_models == ()
    assert spec.registered_models == ("Comment", "Post", "ShopImage")
    assert spec.registered_snake_models == ("comment", "post", "shop_image")
    assert spec.generated_route_name == "/admin/reports/index"

def test__generate_route_spec_admin_posts_show_when_admin_model_exists(model_builder):
    # Override fixture for this one collision-specific case.
    models_init_file = model_builder / "app" / "models" / "__init__.py"
    models_init_file.write_text(
        "from .admin import Admin\n"
        "from .post import Post\n",
        encoding="utf-8",
    )

    spec = _generate_route_spec("admin.posts.show")

    assert spec.dotted_path_with_action == "admin.posts.show"
    assert spec.relative_path == "admin/posts"
    assert spec.action == "show"
    assert spec.is_restful is True
    assert spec.relative_path_segments == ("admin", "posts" )
    assert spec.relative_path_segment_models == ("admin", "posts")
    assert spec.registered_models == ("Admin", "Post")
    assert spec.registered_snake_models == ("admin", "post")
    assert spec.generated_route_name == "/admin/<int:admin_id>/posts/<int:post_id>"

def test__register_top_level_blueprint_in_app_missing_app_init(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    is_successful, message, blueprint_name, app_init_path = (
        routes_module._register_top_level_blueprint_in_app(
            relative_path="users",
            route_directory_path="app/routes/users",
        )
    )

    assert is_successful is False
    assert message == "Failed to locate file `app/__init__.py`"
    assert blueprint_name is None
    assert app_init_path is None

def test__register_top_level_blueprint_in_app_already_registered(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app_dir = tmp_path / "app"
    app_dir.mkdir(parents=True)
    (app_dir / "__init__.py").write_text(
        "from app.routes.users import bp as users_blueprint\n"
        "app.register_blueprint(users_blueprint)\n"
        "return app\n",
        encoding="utf-8",
    )

    is_successful, message, blueprint_name, app_init_path = (
        _register_top_level_blueprint_in_app(
            relative_path="users",
            route_directory_path="app/routes/users",
        )
    )

    assert is_successful is True
    assert message == "Route blueprint already registered in app/__init__.py"
    assert blueprint_name == "users_blueprint"
    assert app_init_path == "app/__init__.py"

def test__register_blueprint_in_parent_missing_parent_init(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    is_successful, message, blueprint_name, parent_init_path = (
        _register_blueprint_in_parent(
            "recipes/comments",
            "app/routes/recipes/comments",
        )
    )

    assert is_successful is False
    assert message == "file __init__.py missing at app/routes/recipes/__init__.py"
    assert blueprint_name is None
    assert parent_init_path is None

def test__register_blueprint_in_parent_already_registered(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    parent_dir = tmp_path / "app" / "routes" / "recipes"
    parent_dir.mkdir(parents=True)
    (parent_dir / "__init__.py").write_text(
        "from app.routes.recipes.comments import bp as recipes_comments_blueprint\n"
        "bp.register_blueprint(recipes_comments_blueprint)\n",
        encoding="utf-8",
    )

    is_successful, message, blueprint_name, parent_init_path = (
        _register_blueprint_in_parent(
            "recipes/comments",
            "app/routes/recipes/comments",
        )
    )

    assert is_successful is True
    assert message == "recipes_comments_blueprint already registered"
    assert blueprint_name == "recipes_comments_blueprint"
    assert parent_init_path == "app/routes/recipes/__init__.py"

def test__write_parent_route_directory_when_exists_returns_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "app" / "routes" / "recipes").mkdir(parents=True)

    updates = _write_parent_route_directory("app/routes/recipes")

    assert updates == []

def test__write_parent_route_directory_creates_scaffold(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    updates = _write_parent_route_directory("app/routes/recipes")

    assert len(updates) == 3
    assert updates[0] == "Created routes directory at app/routes/recipes"
    assert updates[1] == "Created __init__.py in app/routes/recipes"
    assert updates[2] == "Created routes.py with blueprint import only in app/routes/recipes"
    assert (tmp_path / "app" / "routes" / "recipes" / "__init__.py").exists()
    assert (tmp_path / "app" / "routes" / "recipes" / "routes.py").exists()

def test__write_parent_routes_single_segment_returns_empty():
    assert _write_parent_routes("users") == (True, [])


def test__write_parent_routes_creates_each_missing_parent_and_registers(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    app_dir = tmp_path / "app"
    app_dir.mkdir(parents=True)
    (app_dir / "__init__.py").write_text(
        "from flask import Flask\n"
        "def create_app(config_name) -> Flask:\n"
        "    app = Flask(__name__)\n"
        "    return app\n",
        encoding="utf-8",
    )

    is_successful, updates = routes_module._write_parent_routes("recipes/comments/images")
    updates = [routes_module.click.unstyle(message) for message in updates]

    # Parent route directories were created
    assert (tmp_path / "app" / "routes" / "recipes").is_dir()
    assert (tmp_path / "app" / "routes" / "recipes" / "__init__.py").exists()
    assert (tmp_path / "app" / "routes" / "recipes" / "routes.py").exists()

    assert (tmp_path / "app" / "routes" / "recipes" / "comments").is_dir()
    assert (tmp_path / "app" / "routes" / "recipes" / "comments" / "__init__.py").exists()
    assert (tmp_path / "app" / "routes" / "recipes" / "comments" / "routes.py").exists()

    # Top-level registration happened in app/__init__.py
    app_init = (tmp_path / "app" / "__init__.py").read_text(encoding="utf-8")
    assert "from app.routes.recipes import bp as recipes_blueprint" in app_init
    assert "app.register_blueprint(recipes_blueprint)" in app_init

    # Nested registration happened in app/routes/recipes/__init__.py
    recipes_init = (tmp_path / "app" / "routes" / "recipes" / "__init__.py").read_text(encoding="utf-8")
    assert "from app.routes.recipes.comments import bp as recipes_comments_blueprint" in recipes_init
    assert "bp.register_blueprint(recipes_comments_blueprint)" in recipes_init

    # Verify high-level update messages
    assert any("Created routes directory at app/routes/recipes" in m for m in updates)
    assert any("Created routes directory at app/routes/recipes/comments" in m for m in updates)
    assert any("Registered the new route directory as recipes_blueprint" in m for m in updates)
    assert any("Registered the new route as recipes_comments_blueprint in app/routes/recipes/__init__.py" in m for m in updates)

def test__write_routes_file_fails_when_routes_py_already_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    route_dir = tmp_path / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)
    (route_dir / "routes.py").write_text("# exists\n", encoding="utf-8")

    is_successful, message, route_file_path = _write_routes_file(
        route_directory_path="app/routes/users",
        action="index",
        route_name="/users",
        controller_name="UserController",
    )

    assert "Failed to create" in message
    assert "routes.py" in message
    assert "app/routes/users/routes.py" in message
    assert "already exists" in message


