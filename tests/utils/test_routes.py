import pytest
from flask_commands.utils.routes import (
    route_add_method,
    route_generate_nested_route,
    route_generate_route_name,
    route_generate_route_spec,
    route_generate_route_folder_path_and_blueprint_name,
    route_make_directory_and_register_blueprint)

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
        route_folder_path='app/routes/users',
        blueprint_name="users",
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

    is_successful, message = route_add_method(
        relative_path='users',
        action='index',
        route_folder_path='app/routes/users',
        blueprint_name='users',
        route_name='users.index',
        controller_name='UserController')

    assert is_successful is False
    assert f"Route Function Exist" in message

def test_route_add_method_route_file_missing(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)
    monkeypatch.chdir(project_root)

    is_successful, message = route_add_method(
        relative_path='users',
        action='index',
        route_folder_path='app/routes/users',
        blueprint_name='users',
        route_name='users.index',
        controller_name='UserController')

    assert is_successful is False
    assert f"Route Directory Missing" in message

def test_route_generate_nested_route_empty_relative_path():
    assert route_generate_nested_route(
        relative_path="",
        action="my_action",
        is_restful=False,
        relative_path_segments=[],
        relative_path_segment_models=[]
    ) == "/my-action"

def test_route_generate_nested_route_non_restful_with_models():
    assert route_generate_nested_route(
        relative_path="posts/comments",
        action="preview_action",
        is_restful=False,
        relative_path_segments=["posts", "comments"],
        relative_path_segment_models=["posts", "comments"]
    ) == "/posts/<int:post_id>/comments/<int:comment_id>/preview-action"

def test_route_generate_nested_route_restful_last_segment_not_model():
    assert route_generate_nested_route(
        relative_path="admin_panel/reports",
        action="index",
        is_restful=True,
        relative_path_segments=["admin_panel", "reports"],
        relative_path_segment_models=[]
    ) == "/admin-panel/reports/index"

def test_route_generate_nested_route_restful_with_models():
    assert route_generate_nested_route(
        relative_path="posts/comments",
        action="show",
        is_restful=True,
        relative_path_segments=["posts", "comments"],
        relative_path_segment_models=["posts", "comments"]
    ) == "/posts/<int:post_id>/comments/<int:comment_id>"

def test_route_generate_route_folder_path_and_blueprint_name_crud():
    route_folder_path, blueprint_name = \
        route_generate_route_folder_path_and_blueprint_name(
            "posts.index", 'posts')
    assert route_folder_path == 'app/routes/posts'
    assert blueprint_name == 'posts'

def test_route_generate_route_folder_path_and_blueprint_name_crud_with_relation():
    route_folder_path, blueprint_name = \
        route_generate_route_folder_path_and_blueprint_name(
            "posts.comments.index", 'posts/comments')
    assert route_folder_path == 'app/routes/posts/comments'
    assert blueprint_name == 'posts'

    route_folder_path, blueprint_name = \
        route_generate_route_folder_path_and_blueprint_name(
            "posts.comments.images.index", 'posts/comments/images')
    assert route_folder_path == 'app/routes/posts/comments/images'
    assert blueprint_name == 'posts'

def test_route_generate_route_folder_path_and_blueprint_name_non_crud():
    route_folder_path, blueprint_name = route_generate_route_folder_path_and_blueprint_name("dashboard", "mains")
    assert route_folder_path == 'app/routes/mains'
    assert blueprint_name == 'mains'

def test_route_generate_route_name_crud(model_builder):
    assert route_generate_route_name('posts.index') == '/posts'
    assert route_generate_route_name('posts.create') == '/posts/create'
    assert route_generate_route_name('posts.store') == '/posts'
    assert route_generate_route_name('posts.show') == '/posts/<int:post_id>'
    assert route_generate_route_name('posts.edit') == '/posts/<int:post_id>/edit'
    assert route_generate_route_name('posts.update') == '/posts/<int:post_id>'
    assert route_generate_route_name('posts.destroy') == '/posts/<int:post_id>/delete'
    assert route_generate_route_name('posts.delete') == '/posts/<int:post_id>/delete'
    assert route_generate_route_name('admin.posts.create') == '/admin/posts/create'
    assert route_generate_route_name('admin.posts.comments.show') == '/admin/posts/<int:post_id>/comments/<int:comment_id>'
    assert route_generate_route_name('admin.posts.comments.index') == '/admin/posts/<int:post_id>/comments'
    assert route_generate_route_name('admin.posts.comments.index') == '/admin/posts/<int:post_id>/comments'
    assert route_generate_route_name('not_a_model.posts.comments.index') == '/not_a_model/posts/<int:post_id>/comments'

def test_route_generate_route_name_non_crud():
    assert route_generate_route_name('posts') == '/posts'
    assert route_generate_route_name('admin.posts') == '/admin/posts'
    assert route_generate_route_name('post') == '/post'
    assert route_generate_route_name('admin.post') == '/admin/post'
    assert route_generate_route_name('admin.posts.comments') == '/admin/posts/comments'

def test_route_generate_route_spec_landing(model_builder):
    spec = route_generate_route_spec("landing")

    assert spec.relative_path == ""
    assert spec.action == "landing"
    assert spec.is_restful is False
    assert spec.flat_route == "/landing"
    assert spec.nested_route == "/landing"
    assert spec.registered_models == ("Comment", "Post", "ShopImage")
    assert "post" in spec.registered_snake_models

def test_route_generate_route_spec_index_empty_relative_path(model_builder):
    spec = route_generate_route_spec("index")

    assert spec.relative_path == ""
    assert spec.action == "index"
    assert spec.is_restful is True
    assert spec.flat_route == "/index"
    assert spec.nested_route == "/index"

def test_route_generate_route_spec_posts_show(model_builder):
    spec = route_generate_route_spec("posts.show")

    assert spec.relative_path == "posts"
    assert spec.action == "show"
    assert spec.is_restful is True
    assert spec.flat_route == "/posts-show"
    assert spec.nested_route == "/posts/<int:post_id>"

def test_route_generate_route_spec_admin_posts_comments_show(model_builder):
    spec = route_generate_route_spec("admin.posts.comments.show")

    assert spec.relative_path == "admin/posts/comments"
    assert spec.action == "show"
    assert spec.is_restful is True
    assert spec.flat_route == "/admin-posts-comments-show"
    assert spec.nested_route == "/admin/posts/<int:post_id>/comments/<int:comment_id>"

#here
def test_route_generate_route_spec_admin_shop_images_show(model_builder):
    spec = route_generate_route_spec("admin.shop_images.show")

    assert spec.relative_path == "admin/shop_images"
    assert spec.action == "show"
    assert spec.is_restful is True
    assert spec.flat_route == "/admin-shop-images-show"
    assert spec.nested_route == "/admin/shop-images/<int:shop_image_id>"


def test_route_generate_route_spec_posts_custom_action(model_builder):
    spec = route_generate_route_spec("posts.custom_action")

    assert spec.relative_path == "posts"
    assert spec.action == "custom_action"
    assert spec.is_restful is False
    assert spec.flat_route == "/posts-custom-action"
    assert spec.nested_route == "/posts/<int:post_id>/custom-action"

def test_route_generate_route_spec_posts_custom_action_again(model_builder):
    spec = route_generate_route_spec("posts.custom-action")

    assert spec.relative_path == "posts"
    assert spec.action == "custom-action"
    assert spec.is_restful is False
    assert spec.flat_route == "/posts-custom-action"
    assert spec.nested_route == "/posts/<int:post_id>/custom-action"

def test_route_generate_route_spec_admin_reports_index_no_models(model_builder):
    spec = route_generate_route_spec("admin.reports.index")

    assert spec.relative_path == "admin/reports"
    assert spec.action == "index"
    assert spec.is_restful is True
    assert spec.flat_route == "/admin-reports-index"
    assert spec.nested_route == "/admin/reports/index"


def test_route_generate_route_spec_admin_posts_show_when_admin_model_exists(model_builder):
    # Override fixture for this one collision-specific case.
    models_init_file = model_builder / "app" / "models" / "__init__.py"
    models_init_file.write_text(
        "from .admin import Admin\n"
        "from .post import Post\n",
        encoding="utf-8",
    )

    spec = route_generate_route_spec("admin.posts.show")

    assert spec.relative_path == "admin/posts"
    assert spec.action == "show"
    assert spec.is_restful is True
    assert spec.flat_route == "/admin-posts-show"
    assert spec.nested_route == "/admin/<int:admin_id>/posts/<int:post_id>"


def test_route_make_directory_and_register_blueprint_success(tmp_path, monkeypatch):
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
    is_successful, message = route_make_directory_and_register_blueprint(
        relative_path='users',
        action='index',
        route_folder_path='app/routes/users',
        blueprint_name='users',
        route_name='/users',
        controller_name='UserController')

    assert is_successful is True
    assert "Created New Route Directory" in message

def test_route_make_directory_and_register_blueprint_success_nested_routes(tmp_path, monkeypatch):
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
    is_successful, message = route_make_directory_and_register_blueprint(
        relative_path='recipes/comments',
        action='index',
        route_folder_path='app/routes/recipes/comments',
        blueprint_name='recipes',
        route_name='/recipes/<int:recipe_id>/comments',
        controller_name='RecipeCommentController')

    assert is_successful is True
    assert "Created New Route Directory" in message

def test_route_make_directory_and_register_blueprint_app_init_missing_return(tmp_path, monkeypatch):
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
    is_successful, message = route_make_directory_and_register_blueprint(
        relative_path='users',
        action='index',
        route_folder_path='app/routes/users',
        blueprint_name='users',
        route_name='/users',
        controller_name='UserController')

    assert is_successful is False
    assert "Could not register blueprint" in message

def test_route_make_directory_and_register_blueprint_route_already_exists(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)
    monkeypatch.chdir(project_root)

    # dotted_path_with_action = users.index
    is_successful, message = route_make_directory_and_register_blueprint(
        relative_path='users',
        action='index',
        route_folder_path='app/routes/users',
        blueprint_name='users',
        route_name='/users',
        controller_name='UserController')

    assert is_successful is False
    assert "Route Already Exists" in message

def test_route_make_directory_and_register_blueprint_exception(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("motherboard failure")

    monkeypatch.setattr(
        "flask_commands.utils.routes.write_file",
        boom
    )

    project_root = tmp_path
    monkeypatch.chdir(project_root)
    # dotted_path_with_action = users.index
    is_successful, message = route_make_directory_and_register_blueprint(
        relative_path='users',
        action='index',
        route_folder_path='app/routes/users',
        blueprint_name='users',
        route_name='/users',
        controller_name='UserController')

    assert is_successful is False
    assert "Failed to create route" in message

def test_route_method_exception(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("internal server error")

    monkeypatch.setattr(
        "flask_commands.utils.routes.append_file",
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

    is_successful, message = route_add_method(
        relative_path='users',
        action='index',
        route_folder_path='app/routes/users',
        blueprint_name='users',
        route_name='users.index',
        controller_name='UserController')

    assert is_successful is False
    assert "Failed to add method to route" in message
