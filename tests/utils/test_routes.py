from flask_commands.utils.routes import (
    route_add_method,
    route_make_directory_and_register_blueprint,
    route_infer_name_from,
    generate_route_folder_path_and_blueprint_name)

def test_route_infer_name_from_crud():
    assert route_infer_name_from('posts.index') == '/posts'
    assert route_infer_name_from('posts.create') == '/posts/create'
    assert route_infer_name_from('posts.store') == '/posts'
    assert route_infer_name_from('posts.show') == '/posts/<int:post_id>'
    assert route_infer_name_from('posts.edit') == '/posts/<int:post_id>/edit'
    assert route_infer_name_from('posts.update') == '/posts/<int:post_id>'
    assert route_infer_name_from('posts.destroy') == '/posts/<int:post_id>/delete'
    assert route_infer_name_from('posts.delete') == '/posts/<int:post_id>/delete'
    assert route_infer_name_from('admin.posts.create') == '/admin/posts/create'
    assert route_infer_name_from('admin.posts.comments.show') == '/admin/posts/comments/<int:comment_id>'
    assert route_infer_name_from('admin.posts.comments.index') == '/admin/posts/comments'

def test_route_infer_name_from_non_crud():
    assert route_infer_name_from('posts') == '/posts'
    assert route_infer_name_from('admin.posts') == '/admin/posts'
    assert route_infer_name_from('post') == '/post'
    assert route_infer_name_from('admin.post') == '/admin/post'
    assert route_infer_name_from('admin.posts.comments') == '/admin/posts/comments'

def test_generate_route_folder_path_and_blueprint_name_crud():
    route_folder_path, blueprint_name = \
        generate_route_folder_path_and_blueprint_name(
            "posts.index", 'posts')
    assert route_folder_path == 'app/routes/posts'
    assert blueprint_name == 'posts'

def test_generate_route_folder_path_and_blueprint_name_crud_with_relation():
    route_folder_path, blueprint_name = \
        generate_route_folder_path_and_blueprint_name(
            "posts.comments.index", 'posts/comments')
    assert route_folder_path == 'app/routes/posts/comments'
    assert blueprint_name == 'posts_comments'

def test_generate_route_folder_path_and_blueprint_name_non_crud():
    route_folder_path, blueprint_name = generate_route_folder_path_and_blueprint_name("dashboard", "mains")
    assert route_folder_path == 'app/routes/mains'
    assert blueprint_name == 'mains'

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
    # dotted_path_with_name = users.index
    is_successfull, message = route_make_directory_and_register_blueprint(
        action='index',
        route_folder_path='app/routes/users',
        blueprint_name='users',
        route_name='/users',
        controller_name='UserController')

    assert is_successfull is True
    assert "Created new route directory" in message

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
        , encoding="utf-8")

    route_dir = project_root / "app" / "routes"
    route_dir.mkdir(parents=True)

    monkeypatch.chdir(project_root)
    # dotted_path_with_name = users.index
    is_successfull, message = route_make_directory_and_register_blueprint(
        action='index',
        route_folder_path='app/routes/users',
        blueprint_name='users',
        route_name='/users',
        controller_name='UserController')

    assert is_successfull is False
    assert "Could not register blueprin" in message

def test_route_make_directory_and_register_blueprint_route_already_exists(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)
    monkeypatch.chdir(project_root)

    # dotted_path_with_name = users.index
    is_successfull, message = route_make_directory_and_register_blueprint(
        action='index',
        route_folder_path='app/routes/users',
        blueprint_name='users',
        route_name='/users',
        controller_name='UserController')

    assert is_successfull is False
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
    # dotted_path_with_name = users.index
    is_successfull, message = route_make_directory_and_register_blueprint(
        action='index',
        route_folder_path='app/routes/users',
        blueprint_name='users',
        route_name='/users',
        controller_name='UserController')

    assert is_successfull is False
    assert "Failed to create route" in message

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

    is_successfull, message = route_add_method(
        route_name='users.index',
        action='index',
        route_folder_path='app/routes/users',
        relative_path='users',
        controller_name='UserController')

    assert is_successfull is True
    assert "Added GET route 'index' to 'users'" in message
    assert "To reference path use" in message
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

    is_successfull, message = route_add_method(
        route_name='users.index',
        action='index',
        route_folder_path='app/routes/users',
        relative_path='users',
        controller_name='UserController')

    assert is_successfull is False
    assert f"Route function already exists" in message


def test_route_add_method_route_file_missing(tmp_path, monkeypatch):
    project_root = tmp_path
    route_dir = project_root / "app" / "routes" / "users"
    route_dir.mkdir(parents=True)
    monkeypatch.chdir(project_root)

    is_successfull, message = route_add_method(
        route_name='users.index',
        action='index',
        route_folder_path='app/routes/users',
        relative_path='users',
        controller_name='UserController')

    assert is_successfull is False
    assert f"routes.py Missing" in message

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

    is_successfull, message = route_add_method(
        route_name='users.index',
        action='index',
        route_folder_path='app/routes/users',
        relative_path='users',
        controller_name='UserController')

    assert is_successfull is False
    assert "Failed to add method to route" in message
