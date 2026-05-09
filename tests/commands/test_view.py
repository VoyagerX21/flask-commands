import os
import pytest
from click.testing import CliRunner
from flask_commands.commands.view import make_view

@pytest.fixture
def project(tmp_path, monkeypatch):
    """
    Create the project structure for testing
    app/
      __init__.py
      controllers/
      models/
      routes/
      static/
      templates/
    """
    root = tmp_path
    # Create the project subfolders
    (root / "app" / "controllers").mkdir(parents=True)
    (root / "app" / "models").mkdir()
    (root / "app" / "routes").mkdir()
    (root / "app" / "static").mkdir()
    (root / "app" / "templates").mkdir()

    # Create a minimal app/__init__.py so blueprint registration works
    init_file_path = root / "app" / "__init__.py"
    init_file_path.write_text(
        "from flask import Flask\n"
        "from config import config\n"
        "\n"
        "\n"
        "def create_app(config_name) -> Flask:\n"
        "    app = Flask(__name__)\n"
        "\n"
        "    # apply configuration\n"
        "    app.config.from_object(config[config_name])\n"
        "\n"
        "    from app.routes.mains import bp as mains_blueprint\n"
        "    app.register_blueprint(mains_blueprint)\n"
        "\n"
        "    return app\n"
    )

    main_controller_file_path = root / "app" / "controllers" / "main_controller.py"
    main_controller_file_path.write_text(
        "from flask import render_template\n"
        "\n"
        "class MainController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('mains/index.html')\n"
    )

    mains_routes_dir = root / "app" / "routes" / "mains"
    mains_routes_dir.mkdir(parents=True)

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


    app_run_file_path = root / "run.py"
    app_run_file_path.write_text(
        "import os\n"
        "from app import create_app\n"
        "\n"
        "app = create_app(os.getenv('FLASK_CONFIG') or 'development')\n"
    )

    (root / "app" / "models" / "__init__.py").write_text("", encoding="utf-8")


    monkeypatch.chdir(root)
    return root

def _assert_view_route_contains(project, relative_path: str, route: str) -> None:
    route_file = project / "app" / "routes" / relative_path / "routes.py"
    assert route_file.exists()
    assert route in route_file.read_text(encoding="utf-8")

def _assert_controller_contains(project, controller_file_name: str, snippets: list[str]) -> None:
    controller_file = project / "app" / "controllers" / controller_file_name
    assert controller_file.exists()
    controller_source = controller_file.read_text(encoding="utf-8")
    for snippet in snippets:
        assert snippet in controller_source

def test_make_view_with_invalid_dotted_path(project):
    runner = CliRunner()
    result = runner.invoke(make_view, ["  ..__  "])

    assert result.exit_code == 0, result.output
    assert "Invalid dotted path" in result.output

def test_make_view_not_in_project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(make_view, ["card"])

    assert result.exit_code == 0, result.output
    assert "Warning: You are not currently in a Flask project root directory" in result.output
    assert not (tmp_path / "app" / "templates" / "card.py").exists()

def test_make_view_component_only(project):
    """
    This should:
    1) create app/templates/card.html
    2) Not create any routes, controllers, or models
    3) print the "File Created" message
    """

    runner = CliRunner()
    result = runner.invoke(make_view, ["card"])

    assert result.exit_code == 0, result.output
     # File should exist
    template_file = project / "app" / "templates" / "card.html"
    assert template_file.exists()

    # Output should mention file created
    assert "Created New View" in result.output

def test_make_view_root_action_with_generated_wiring_keeps_root_template(project):
    runner = CliRunner()
    result = runner.invoke(make_view, ["about", "-rc"])

    observed_controller_content = (
        project / "app" / "controllers" / "main_controller.py"
    ).read_text(encoding="utf-8")

    assert result.exit_code == 0, result.output
    assert "return render_template('about.html')" in observed_controller_content
    assert (project / "app" / "templates" / "about.html").exists()
    assert not (project / "app" / "templates" / "mains" / "about.html").exists()
    assert "Added view file at app/templates/about.html" in result.output
    assert "url_for('mains.about')" in result.output

def test_make_view_root_and_explicit_mains_use_different_template_targets(project):
    runner = CliRunner()

    root_result = runner.invoke(make_view, ["about", "-rc"])
    mains_result = runner.invoke(make_view, ["mains.contact", "-rc"])

    assert root_result.exit_code == 0, root_result.output
    assert mains_result.exit_code == 0, mains_result.output

    assert (project / "app" / "templates" / "about.html").exists()
    assert not (project / "app" / "templates" / "mains" / "about.html").exists()

    assert (project / "app" / "templates" / "mains" / "contact.html").exists()
    assert not (project / "app" / "templates" / "contact.html").exists()

def test_make_view_root_component_only_does_not_change_main_wiring(project):
    runner = CliRunner()
    result = runner.invoke(make_view, ["landing"])

    observed_controller_content = (
        project / "app" / "controllers" / "main_controller.py"
    ).read_text(encoding="utf-8")
    expected_controller_content = (
        "from flask import render_template\n"
        "\n"
        "class MainController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('mains/index.html')\n"
    )

    observed_routes_content = (
        project / "app" / "routes" / "mains" / "routes.py"
    ).read_text(encoding="utf-8")
    expected_routes_content = (
        "from app.controllers import MainController\n"
        "from app.routes.mains import bp\n"
        "\n"
        "@bp.route('/', methods=['GET'])\n"
        "def index():\n"
        "    return MainController.index()\n"
    )

    assert result.exit_code == 0, result.output
    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert "Method Added To Controller" not in result.output
    assert "Added Route" not in result.output

def test_make_view_with_generated_controller(project):
    """
    This should
    1) create app/templates/posts/index.html
    2) generate controller name = PostController
    3) create controller file
    4) add the method to the controller file
    """
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.index", "-c"])

    assert result.exit_code == 0, result.output
    template_file = project / "app" / "templates" / "posts" / "index.html"
    assert template_file.exists()

    controller_file = project / "app" / "controllers" / "post_controller.py"
    assert controller_file.exists()

    # Controller contains method
    controller_text = controller_file.read_text()
    assert "class PostController" in controller_text
    assert "def index" in controller_text

def test_make_view_with_generated_controller_and_no_relationship(project):
    runner = CliRunner()
    result = runner.invoke(make_view, ["card", "-c"])

    assert result.exit_code == 0, result.output
    assert "Method Added To Controller" in result.output

def test_make_view_with_generated_route_declines_model_prompt(project):
    """
    This should
    1) create app/templates/posts/index.html
    2) generate route + blueprint for posts
    3) decline model prompt (no model file)
    4) use declined route: /posts/index (not /posts)
    """
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.index", "-r"], input="n\n")

    assert result.exit_code == 0, result.output
    template_file = project / "app" / "templates" / "posts" / "index.html"
    assert template_file.exists()

    # Route folder exists
    route_dir = project / "app" / "routes" / "posts"
    assert route_dir.exists()

    # routes.py should exist
    routes_file = route_dir / "routes.py"
    assert routes_file.exists()

    routes_text = routes_file.read_text(encoding="utf-8")

    expected_source = (
        "from app.controllers import MainController\n"
        "from app.routes.posts import bp\n"
        "\n"
        "@bp.route('/posts/index', methods=['GET'])\n"
        "def index():\n"
        "    return MainController.index()\n"
    )

    assert routes_text == expected_source

    model_file = project / "app" / "models" / "post.py"
    assert not model_file.exists()

def test_make_view_with_generated_route_accepts_model_prompt(project):
    """
    This should
    1) create app/templates/posts/index.html
    2) accept model prompt (model generated)
    3) use accepted route: /posts
    """
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.index", "-r"], input="y\n")

    assert result.exit_code == 0, result.output
    template_file = project / "app" / "templates" / "posts" / "index.html"
    assert template_file.exists()

    route_dir = project / "app" / "routes" / "posts"
    assert route_dir.exists()

    routes_file = route_dir / "routes.py"
    assert routes_file.exists()

    routes_text = routes_file.read_text(encoding="utf-8")
    expected_source = (
        "from app.controllers import MainController\n"
        "from app.routes.posts import bp\n"
        "\n"
        "@bp.route('/posts', methods=['GET'])\n"
        "def index():\n"
        "    return MainController.index()\n"
    )
    assert routes_text == expected_source

    model_file = project / "app" / "models" / "post.py"
    assert model_file.exists()

def test_make_view_with_generated_route_add_method_decline_model_prompt(project):
    routes_file = project / "app" / "routes" / "posts" / "routes.py"
    routes_file.parent.mkdir(parents=True)
    routes_file.write_text(
        "from app.controllers import MainController\n"
        "from app.routes.posts import bp\n"
        "\n"
        "@bp.route('/posts', methods=['GET'])\n"
        "def index():\n"
        "    return PostController.index()"
    )
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.show", "-r"], input="n\n")

    routes_text = routes_file.read_text(encoding="utf-8")

    expected_source = (
        "from app.controllers import MainController\n"
        "from app.routes.posts import bp\n"
        "\n"
        "@bp.route('/posts', methods=['GET'])\n"
        "def index():\n"
        "    return PostController.index()\n"
        "\n"
        "@bp.route('/posts/show', methods=['GET'])\n"
        "def show():\n"
        "    return MainController.show()\n"
    )

    assert routes_text == expected_source
    assert result.exit_code == 0, result.output
    assert "Added Route" in result.output

def test_make_view_with_generated_route_add_method_accept_model_prompt(project):
    routes_file = project / "app" / "routes" / "posts" / "routes.py"
    routes_file.parent.mkdir(parents=True)
    routes_file.write_text(
        "from app.controllers import MainController\n"
        "from app.routes.posts import bp\n"
        "\n"
        "@bp.route('/posts', methods=['GET'])\n"
        "def index():\n"
        "    return PostController.index()"
    )
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.show", "-r"], input="y\n")

    routes_text = routes_file.read_text(encoding="utf-8")

    expected_source = (
        "from app.controllers import MainController\n"
        "from app.routes.posts import bp\n"
        "\n"
        "@bp.route('/posts', methods=['GET'])\n"
        "def index():\n"
        "    return PostController.index()\n"
        "\n"
        "@bp.route('/posts/<int:post_id>', methods=['GET'])\n"
        "def show(post_id: int):\n"
        "    return MainController.show(post_id)\n"
    )

    assert routes_text == expected_source
    assert result.exit_code == 0, result.output
    assert "Added Route" in result.output

def test_make_view_with_generated_route_exception(project, monkeypatch):
    # Keep the real function around
    real_exists = os.path.exists

    def boom(path):
        # Raise only for our route folder lookup
        if "app/routes" in str(path):
            raise RuntimeError("boom boom boom")
        return real_exists(path)

    monkeypatch.setattr("os.path.exists", boom)

    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.index", "-r"], input="n\n")

    assert result.exit_code == 0, result.output
    assert "💣 Error:" in result.output
    assert "boom boom boom" in result.output

def test_make_view_with_generated_model(project):
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.index", "-m"])

    assert result.exit_code == 0, result.output
    model_file = project / "app" / "models" / "post.py"
    assert model_file.exists()

    model_file_content = model_file.read_text()
    assert "class Post(db.Model)" in model_file_content
    assert "__tablename__ = 'posts'" in model_file_content

def test_make_view_file_exists(project):
    # Pre-create
    template_file = project / "app" / "templates" / "card.html"
    template_file.write_text("hi")

    runner = CliRunner()
    result = runner.invoke(make_view, ["card"])

    assert result.exit_code == 0, result.output
    assert "View Already Exist" in result.output
    assert "hi" == template_file.read_text()

def test_make_view_controller_exist(project):
    # Pre-create
    controller_file = project / "app" / "controllers" / "post_controller.py"
    controller_file.write_text(
        "from flask import render_template\n"
        "\n"
        "class PostController:\n"
        "    @staticmethod\n"
        "    def index() -> str:\n"
        "        return render_template('posts/index.html')"
    )
    runner = CliRunner()
    result = runner.invoke(make_view, ["posts.show", '-c'])

    assert result.exit_code == 0, result.output
    assert "Method Added" in result.output
    assert "def show" in controller_file.read_text()

def test_make_view_root_action_with_generated_wiring_without_using_mains_template_namespace(project):

    runner = CliRunner()
    result = runner.invoke(make_view, ["landing", "-rc"])

    observed_controller_content = (
        project / "app" / "controllers" / "main_controller.py"
    ).read_text(encoding="utf-8")
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

    observed_routes_content = (
        project / "app" / "routes" / "mains" / "routes.py"
    ).read_text(encoding="utf-8")
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

    assert result.exit_code == 0, result.output
    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert (project / "app" / "templates" / "landing.html").exists()
    assert not (project / "app" / "templates" / "mains" / "landing.html").exists()
    assert "Added view file at app/templates/landing.html" in result.output
    assert "url_for('mains.landing')" in result.output

def test_make_view_explicit_mains_root_action_keeps_mains_out_of_url_but_in_mains_template(project):
    runner = CliRunner()
    result = runner.invoke(make_view, ["mains.landing", "-rc"])

    observed_controller_content = (
        project / "app" / "controllers" / "main_controller.py"
    ).read_text(encoding="utf-8")
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

    observed_routes_content = (
        project / "app" / "routes" / "mains" / "routes.py"
    ).read_text(encoding="utf-8")
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

    assert result.exit_code == 0, result.output
    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert (project / "app" / "templates" / "mains" / "landing.html").exists()
    assert not (project / "app" / "templates" / "landing.html").exists()
    assert "Generated route /landing" in result.output
    assert "Added view file at app/templates/mains/landing.html" in result.output
    assert "url_for('mains.landing')" in result.output

def test_make_view_root_action_with_explicit_wiring_keeps_root_template(project):

    runner = CliRunner()
    result = runner.invoke(
        make_view,
        ["landing", "--route=/landing", "--controller=MainController"],
    )

    observed_controller_content = (
        project / "app" / "controllers" / "main_controller.py"
    ).read_text(encoding="utf-8")
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

    observed_routes_content = (
        project / "app" / "routes" / "mains" / "routes.py"
    ).read_text(encoding="utf-8")
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

    assert result.exit_code == 0, result.output
    assert observed_controller_content == expected_controller_content
    assert observed_routes_content == expected_routes_content
    assert (project / "app" / "templates" / "landing.html").exists()
    assert not (project / "app" / "templates" / "mains" / "landing.html").exists()
    assert "Added view file at app/templates/landing.html" in result.output
    assert "url_for('mains.landing')" in result.output

def test_make_view_plain_view_only_has_no_message_updates(project):
    runner = CliRunner()

    result = runner.invoke(make_view, ["card"])
    template_file = project / "app" / "templates" / "card.html"

    assert result.exit_code == 0, result.output
    assert template_file.exists()
    assert template_file.read_text(encoding="utf-8").strip() != ""

    assert "Method Added To Controller" not in result.output
    assert "Created Controller Class" not in result.output
    assert "Added Route" not in result.output
    assert "Created New Model" not in result.output

def test_docs_make_view_the_basics_create_simple_template_about(project):
    result = CliRunner().invoke(make_view, ["about"])

    assert result.exit_code == 0, result.output
    assert (project / "app/templates/about.html").exists()


def test_docs_make_view_the_basics_wire_page_explicitly_about(project):
    result = CliRunner().invoke(
        make_view,
        ["about", "--route", "/about", "--controller", "MainController"],
    )

    assert result.exit_code == 0, result.output
    assert (project / "app/templates/about.html").exists()
    _assert_view_route_contains(project, "mains", "@bp.route('/about', methods=['GET'])")
    assert "def about" in (project / "app/controllers/main_controller.py").read_text(encoding="utf-8")


def test_docs_make_view_the_basics_use_generator_flags_about_rc(project):
    result = CliRunner().invoke(make_view, ["about", "-rc"])

    assert result.exit_code == 0, result.output
    assert (project / "app/templates/about.html").exists()
    _assert_view_route_contains(project, "mains", "@bp.route('/about', methods=['GET'])")
    _assert_controller_contains(
        project,
        "main_controller.py",
        [
            "def about() -> str:",
            "return render_template('about.html')"
        ]
    )



def test_docs_make_view_the_basics_use_mains_intentionally_explicit_route(project):
    result = CliRunner().invoke(make_view, ["mains.about", "--route", "/about", "-c"])

    assert result.exit_code == 0, result.output
    assert (project / "app/templates/mains/about.html").exists()
    _assert_view_route_contains(project, "mains", "@bp.route('/about', methods=['GET'])")
    _assert_controller_contains(
        project,
        "main_controller.py",
        [
            "def about() -> str:",
            "return render_template('mains/about.html')"
        ]
    )

def test_docs_make_view_the_basics_use_mains_intentionally_generated_route(project):
    result = CliRunner().invoke(make_view, ["mains.about", "-rc"])

    assert result.exit_code == 0, result.output
    assert (project / "app/templates/mains/about.html").exists()
    _assert_view_route_contains(project, "mains", "@bp.route('/about', methods=['GET'])")
    _assert_controller_contains(
        project,
        "main_controller.py",
        [
            "def about() -> str:",
            "return render_template('mains/about.html')"
        ]
    )


def test_docs_make_view_the_basics_quick_peek_nested_templates_components(project):
    runner = CliRunner()

    assert runner.invoke(make_view, ["components.accordions"]).exit_code == 0
    assert runner.invoke(make_view, ["components.checkboxes"]).exit_code == 0
    assert runner.invoke(make_view, ["components.selects"]).exit_code == 0

    assert (project / "app/templates/components/accordions.html").exists()
    assert (project / "app/templates/components/checkboxes.html").exists()
    assert (project / "app/templates/components/selects.html").exists()

def test_docs_make_view_model_prompt_missing_model_accepts_restful_route(project):
    result = CliRunner().invoke(make_view, ["recipes.index", "-rc"], input="y\n")

    assert result.exit_code == 0, result.output
    assert (project / "app/models/recipe.py").exists()
    _assert_view_route_contains(project, "recipes", "@bp.route('/recipes', methods=['GET'])")
    _assert_controller_contains(
        project,
        "recipe_controller.py",
        [
            "class RecipeController:",
            "def index() -> str:",
            "return render_template('recipes/index.html')"
        ]
    )


def test_docs_make_view_model_prompt_missing_model_declines_literal_route(project):
    result = CliRunner().invoke(make_view, ["recipes.index", "-rc"], input="n\n")

    assert result.exit_code == 0, result.output
    assert not (project / "app/models/recipe.py").exists()
    _assert_view_route_contains(project, "recipes", "@bp.route('/recipes/index', methods=['GET'])")
    _assert_controller_contains(
        project,
        "recipe_controller.py",
        [
            "class RecipeController:",
            "def index() -> str:",
            "return render_template('recipes/index.html')"
        ]
    )


def test_docs_make_view_model_prompt_explicit_literal_route_avoids_prompt(project):
    result = CliRunner().invoke(make_view, ["recipes.index", "-c", "--route", "/recipes/index"])

    assert result.exit_code == 0, result.output
    assert not (project / "app/models/recipe.py").exists()
    _assert_view_route_contains(project, "recipes", "@bp.route('/recipes/index', methods=['GET'])")
    _assert_controller_contains(
        project,
        "recipe_controller.py",
        [
            "class RecipeController:",
            "def index() -> str:",
            "return render_template('recipes/index.html')"
        ],
    )


def test_docs_make_view_model_prompt_explicit_restful_route_with_model_recipe(project):
    result = CliRunner().invoke(
        make_view,
        ["recipes.index", "-c", "--route", "/recipes", "--model", "Recipe"],
    )

    assert result.exit_code == 0, result.output
    assert (project / "app/models/recipe.py").exists()
    assert (project / "app/templates/recipes/index.html").exists()
    _assert_view_route_contains(project, "recipes", "@bp.route('/recipes', methods=['GET'])")
    _assert_controller_contains(
        project,
        "recipe_controller.py",
        [
            "class RecipeController:",
            "def index() -> str:",
            "return render_template('recipes/index.html')"
        ]
    )


def test_docs_make_view_model_prompt_generated_route_controller_model_short_flags(project):
    result = CliRunner().invoke(make_view, ["recipes.index", "-rcm"])

    assert result.exit_code == 0, result.output
    assert (project / "app/models/recipe.py").exists()
    _assert_view_route_contains(project, "recipes", "@bp.route('/recipes', methods=['GET'])")

def test_docs_make_view_building_first_resource_recipes_index_and_show(project):
    runner = CliRunner()

    assert runner.invoke(make_view, ["recipes.index", "-rcm"]).exit_code == 0
    assert runner.invoke(make_view, ["recipes.show", "-rc"]).exit_code == 0

    assert (project / "app/models/recipe.py").exists()
    assert (project / "app/templates/recipes/index.html").exists()
    assert (project / "app/templates/recipes/show.html").exists()
    _assert_view_route_contains(project, "recipes", "@bp.route('/recipes', methods=['GET'])")
    _assert_view_route_contains(project, "recipes", "@bp.route('/recipes/<int:recipe_id>', methods=['GET'])")
    _assert_controller_contains(
        project,
        "recipe_controller.py",
        [
            "def index() -> str:",
            "return render_template('recipes/index.html')",
            "def show(recipe_id: int) -> str:",
            "return render_template('recipes/show.html')"
        ]
    )


def test_docs_make_view_get_vs_post_create_generates_template_store_does_not(project):
    runner = CliRunner()

    assert runner.invoke(make_view, ["recipes.create", "-rcm"]).exit_code == 0
    assert runner.invoke(make_view, ["recipes.store", "-rcm"]).exit_code == 0

    assert (project / "app/templates/recipes/create.html").exists()
    assert not (project / "app/templates/recipes/store.html").exists()
    _assert_view_route_contains(project, "recipes", "@bp.route('/recipes/create', methods=['GET'])")
    _assert_view_route_contains(project, "recipes", "@bp.route('/recipes', methods=['POST'])")
    _assert_controller_contains(
        project,
        "recipe_controller.py",
        [
            "def create() -> str:",
            "return render_template('recipes/create.html')",
            "def store() -> ResponseReturnValue:",
            "return redirect(url_for('recipes.index'))"
        ]
    )


def test_docs_make_view_nested_resources_recipes_comments_index_and_show(project):
    runner = CliRunner()

    assert runner.invoke(make_view, ["recipes.index", "-rcm"]).exit_code == 0
    assert runner.invoke(make_view, ["recipes.comments.index", "-rcm"]).exit_code == 0
    assert runner.invoke(make_view, ["recipes.comments.show", "-rc"]).exit_code == 0

    assert (project / "app/models/comment.py").exists()
    assert (project / "app/templates/recipes/comments/index.html").exists()
    assert (project / "app/templates/recipes/comments/show.html").exists()
    _assert_view_route_contains(project, "recipes/comments", "@bp.route('/recipes/<int:recipe_id>/comments', methods=['GET'])")
    _assert_view_route_contains(project, "recipes/comments", "@bp.route('/recipes/<int:recipe_id>/comments/<int:comment_id>', methods=['GET'])")
    _assert_controller_contains(
        project,
        "recipe_comment_controller.py",
        [
            "def index(recipe_id: int) -> str:",
            "return render_template('recipes/comments/index.html')",
            "def show(recipe_id: int, comment_id: int) -> str:",
            "return render_template('recipes/comments/show.html')"
        ]
    )


def test_docs_make_view_nested_resources_three_levels_deep_images(project):
    runner = CliRunner()

    assert runner.invoke(make_view, ["recipes.index", "-rcm"]).exit_code == 0
    assert runner.invoke(make_view, ["recipes.comments.index", "-rcm"]).exit_code == 0
    assert runner.invoke(make_view, ["recipes.comments.images.index", "-rcm"]).exit_code == 0

    assert (project / "app/models/image.py").exists()
    assert (project / "app/templates/recipes/comments/images/index.html").exists()
    _assert_view_route_contains(
        project,
        "recipes/comments/images",
        "@bp.route('/recipes/<int:recipe_id>/comments/<int:comment_id>/images', methods=['GET'])",
    )
    _assert_controller_contains(
        project,
        "recipe_comment_image_controller.py",
        [
            "def index(recipe_id: int, comment_id: int) -> str:",
            "return render_template('recipes/comments/images/index.html')"
        ]
    )
