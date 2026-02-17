import os
import pytest
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

def test_route_add_method_success(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)

    route_file = route_dir / "routes.py"
    monkeypatch.chdir(project_root)

    route_file.write_text(
        "from app.controllers import UserController\n"
        "from app.routes.users import bp\n"
        "\n"
        "@bp.route('/', methods=['GET'])\n"
        "def show():\n"
        "    return UserController.show()"
        , encoding="utf-8")

    is_successful, message = route_add_method(
        relative_path='users',
        action='index',
        route_directory_path='app/routes/users',
        route_name='users.index',
        controller_name='UserController')

    assert is_successful is True
    assert "Added Route To Existing Directory" in message
    assert "Reference route with" in message
    assert "url_for('users.index')" in message

def test_route_add_method_function_already_exists(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)

    route_file = route_dir / "routes.py"
    monkeypatch.chdir(project_root)

    route_file.write_text(
        "from app.controllers import UserController\n"
        "from app.routes.users import bp\n"
        "\n"
        "@bp.route('/', methods=['GET'])\n"
        "def index():\n"
        "    return UserController.index()"
        , encoding="utf-8")

    before_content = route_file.read_text(encoding='utf-8')

    is_successful, message = route_add_method(
        relative_path='users',
        action='index',
        route_directory_path='app/routes/users',
        route_name='users.index',
        controller_name='UserController')

    after_content = route_file.read_text(encoding='utf-8')

    assert is_successful is False
    assert before_content == after_content
    assert f"Route function index already exist" in message

def test_route_add_method_route_file_missing(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)
    monkeypatch.chdir(project_root)

    is_successful, message = route_add_method(
        relative_path='users',
        action='index',
        route_directory_path='app/routes/users',
        route_name='users.index',
        controller_name='UserController')

    assert (route_dir / "routes.py").exists() is False
    assert is_successful is False
    assert f"Could not find file at app/routes/users/routes.py" in message

def test_route_add_method_exception(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("internal server error")

    monkeypatch.setattr(
        "flask_commands.utils.routes.file_append_file",
        boom
    )

    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)

    route_file = route_dir / "routes.py"
    monkeypatch.chdir(project_root)

    route_file.write_text(
        "from app.controllers import UserController\n"
        "from app.routes.users import bp\n"
        "\n"
        "@bp.route('/', methods=['GET'])\n"
        "def show():\n"
        "    return UserController.show()"
        , encoding="utf-8")

    before_content = route_file.read_text(encoding='utf-8')


    is_successful, message = route_add_method(
        relative_path='users',
        action='index',
        route_directory_path='app/routes/users',
        route_name='users.index',
        controller_name='UserController')

    after_content = route_file.read_text(encoding='utf-8')


    assert is_successful is False
    assert before_content == after_content
    assert "Failed to append index to app/routes/users/routes.py" in message

def test_route_add_method_unexpected_exception_path(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(
        "flask_commands.utils.routes._generate_route_method",
        boom
    )

    is_successful, message = route_add_method(
        relative_path="users",
        action="index",
        route_directory_path="app/routes/users",
        route_name="/users",
        controller_name="UserController",
    )

    assert is_successful is False
    assert "Failed to add method to route" in message
    assert "kaboom" in message

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
    before = route_file.read_text(encoding="utf-8")

    monkeypatch.chdir(project_root)

    # Keep route_write_directory_and_register_blueprint running even though route_dir already exists.
    # _write_routes_file itself is NOT patched.
    monkeypatch.setattr(routes_module.os, "makedirs", lambda *args, **kwargs: None)

    is_successful, message = route_write_directory_and_register_blueprint(
        relative_path="users",
        action="index",
        route_directory_path="app/routes/users",
        route_name="/users",
        controller_name="UserController",
    )

    after = route_file.read_text(encoding="utf-8")

    assert is_successful is False
    assert "Could not create route file" in message
    assert "Failed to create routes.py at app/routes/users/routes.py" in message
    assert "already exists" in message
    assert after == before

def test_route_generate_parameter_reference_empty():
    assert route_generate_parameter_reference([]) == ""

def test_route_generate_parameter_reference_single_param():
    assert route_generate_parameter_reference(["post_id"]) == ", post_id=post_id"

def test_route_generate_parameter_reference_multiple_params():
    assert route_generate_parameter_reference(["post_id", "comment_id"]) == ", post_id=post_id, comment_id=comment_id"

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

def test_route_http_method_for_action_post_delete():
    assert route_http_method_for_action("custom_action") == "GET"

def test_route_write_directory_and_register_blueprint_success(tmp_path, monkeypatch):
    project_root = tmp_path
    app_dir = project_root / "app"
    app_dir.mkdir(parents=True)
    app_init_file = app_dir / "__init__.py"
    app_init_file.write_text(
        'from flask import Flask\n'
        'from config import config\n'
        '\n'
        'def create_app(config_name) -> Flask:\n'
        '    """Creates a Flask application Instance."""\n'
        '    app = Flask(__name__)\n'
        '\n'
        '    # apply configuration\n'
        '    app.config.from_object(config[config_name])\n'
        '\n'
        '    from app.routes.mains import bp as mains_blueprint\n'
        '    app.register_blueprint(mains_blueprint)\n'
        '\n'
        '    return app'
        , encoding="utf-8")

    route_dir = project_root / "app" / "routes"
    route_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)
    # dotted_path_with_action = users.index
    is_successful, message = route_write_directory_and_register_blueprint(
        relative_path='users',
        action='index',
        route_directory_path='app/routes/users',
        route_name='/users',
        controller_name='UserController')

    assert is_successful is True
    assert "Created New Route Directory" in message

def test_route_write_directory_and_register_blueprint_success_nested_routes(tmp_path, monkeypatch):
    project_root = tmp_path
    app_dir = project_root / "app"
    app_dir.mkdir(parents=True)
    app_init_file = app_dir / "__init__.py"
    app_init_file.write_text(
        'from flask import Flask\n'
        'from config import config\n'
        '\n'
        'def create_app(config_name) -> Flask:\n'
        '    """Creates a Flask application Instance."""\n'
        '    app = Flask(__name__)\n'
        '\n'
        '    # apply configuration\n'
        '    app.config.from_object(config[config_name])\n'
        '\n'
        '    from app.routes.mains import bp as mains_blueprint\n'
        '    app.register_blueprint(mains_blueprint)\n'
        '\n'
        '    return app'
        , encoding="utf-8")

    recipes_dir = project_root / "app" / "routes" / "recipes"
    recipes_dir.mkdir(parents=True)

    recipes_init_file = recipes_dir / "__init__.py"
    recipes_init_file.write_text(
        "from flask import Blueprint\n"
        "\n"
        "bp = Blueprint('recipe', __name__)\n"
        "\n"
        "from app.routes.recipe import routes\n"
    )

    monkeypatch.chdir(project_root)
    # dotted_path_with_action = recipes.comments.index
    is_successful, message = route_write_directory_and_register_blueprint(
        relative_path='recipes/comments',
        action='index',
        route_directory_path='app/routes/recipes/comments',
        route_name='/recipes/<int:recipe_id>/comments',
        controller_name='RecipeCommentController')

    assert is_successful is True
    assert "Created New Route Directory" in message

def test_route_write_directory_and_register_blueprint_app_init_missing_return(tmp_path, monkeypatch):
    project_root = tmp_path
    app_dir = project_root / "app"
    app_dir.mkdir(parents=True)
    app_init_file = app_dir / "__init__.py"
    app_init_file.write_text(
        'from flask import Flask\n'
        'from config import config\n'
        '\n'
        'def create_app(config_name) -> Flask:\n'
        '    """Creates a Flask application Instance."""\n'
        '    app = Flask(__name__)\n'
        '\n'
        '    # apply configuration\n'
        '    app.config.from_object(config[config_name])\n'
        '\n'
        '    from app.routes.mains import bp as mains_blueprint\n'
        '    app.register_blueprint(mains_blueprint)\n'
        , encoding="utf-8")

    route_dir = project_root / "app" / "routes"
    route_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)
    # dotted_path_with_action = users.index
    is_successful, message = route_write_directory_and_register_blueprint(
        relative_path='users',
        action='index',
        route_directory_path='app/routes/users',
        route_name='/users',
        controller_name='UserController')

    assert is_successful is False
    assert "Could not register blueprint" in message

def test_route_write_directory_and_register_blueprint_route_already_exists(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)
    monkeypatch.chdir(project_root)

    # dotted_path_with_action = users.index
    is_successful, message = route_write_directory_and_register_blueprint(
        relative_path='users',
        action='index',
        route_directory_path='app/routes/users',
        route_name='/users',
        controller_name='UserController')

    assert is_successful is False
    assert "File exists" in message

def test_route_write_directory_and_register_blueprint_exception(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("motherboard failure")

    monkeypatch.setattr(
        "flask_commands.utils.routes.file_write_file",
        boom
    )

    project_root = tmp_path
    monkeypatch.chdir(project_root)
    # dotted_path_with_action = users.index
    is_successful, message = route_write_directory_and_register_blueprint(
        relative_path='users',
        action='index',
        route_directory_path='app/routes/users',
        route_name='/users',
        controller_name='UserController')

    assert is_successful is False
    assert "Could not create route" in message

def test_route_write_directory_parent_prep_failure_returns_grouped_updates(tmp_path):
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        is_successful, message = route_write_directory_and_register_blueprint(
            relative_path="recipes/comments",  # nested path triggers _write_parent_routes
            action="index",
            route_directory_path="app/routes/recipes/comments",
            route_name="/recipes/<int:recipe_id>/comments",
            controller_name="RecipeCommentController",
        )
    finally:
        os.chdir(original_cwd)

    assert is_successful is False
    assert "Warning: Could not prepare parent routes" in message
    assert "Created routes directory at app/routes/recipes" in message
    assert "Created __init__.py in app/routes/recipes" in message
    assert "Created routes.py with blueprint import only in app/routes/recipes" in message
    assert "Failed to locate file `app/__init__.py`" in message

    # Early return happened before creating the final child route directory.
    assert (tmp_path / "app" / "routes" / "recipes").is_dir()
    assert not (tmp_path / "app" / "routes" / "recipes" / "comments").exists()


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

    is_successful, message = routes_module._register_top_level_blueprint_in_app(
        "app/routes/users"
    )

    assert is_successful is False
    assert message == "Failed to locate file `app/__init__.py`"

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

    is_successful, message = _register_top_level_blueprint_in_app(
        "app/routes/users"
    )

    assert is_successful is True
    assert message == "Route blueprint already registered in app/__init__.py"

def test__register_blueprint_in_parent_missing_parent_init(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    is_successful, message = _register_blueprint_in_parent(
        "recipes/comments",
        "app/routes/recipes/comments",
    )

    assert is_successful is False
    assert message == "file __init__.py missing at app/routes/recipes/__init__.py"

def test__register_blueprint_in_parent_already_registered(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    parent_dir = tmp_path / "app" / "routes" / "recipes"
    parent_dir.mkdir(parents=True)
    (parent_dir / "__init__.py").write_text(
        "from app.routes.recipes.comments import bp as recipes_comments_blueprint\n"
        "bp.register_blueprint(recipes_comments_blueprint)\n",
        encoding="utf-8",
    )

    is_successful, message = routes_module._register_blueprint_in_parent(
        "recipes/comments",
        "app/routes/recipes/comments",
    )

    assert is_successful is True
    assert message == "recipes_comments_blueprint already registered"

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

    is_successful, message = _write_routes_file(
        route_directory_path="app/routes/users",
        action="index",
        route_name="/users",
        controller_name="UserController",
    )

    assert is_successful is False
    assert "Failed to create routes.py at app/routes/users/routes.py" in message
    assert "already exists" in message
