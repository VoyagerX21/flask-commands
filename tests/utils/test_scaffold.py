from re import split
import pytest
from flask_commands.utils.scaffold import (
    check_dotted_path_with_name_for_models,
    crud_mapping_route,
    split_dotted_path
)

@pytest.fixture
def model_builder(tmp_path, monkeypatch):
    project_root = tmp_path
    models_directory = project_root / "app" / "models"
    models_directory.mkdir(parents=True)
    models_init_file = models_directory / "__init__.py"
    models_init_file.write_text(
        "from .users import User"
        , encoding="utf-8"
    )
    monkeypatch.chdir(project_root)

    return project_root

def test_check_dotted_path_with_name_for_models_no_models_init():
    models = check_dotted_path_with_name_for_models("posts.index")
    assert models == []

def test_check_dotted_path_with_name_for_models_empty(model_builder):
    models = check_dotted_path_with_name_for_models("posts.index")
    assert models == []

def test_check_dotted_path_with_name_for_models_intersection(model_builder):
    models = check_dotted_path_with_name_for_models("users.index")
    assert models == ['users']

def test_split_dotted_path_with_no_dot():
    relative_path, action = split_dotted_path("index")
    assert relative_path == ""
    assert action == "index"

def test_split_dotted_path_with_one_dot():
    relative_path, action = split_dotted_path("posts.show")
    assert relative_path == "posts"
    assert action == "show"

def test_split_dotted_path_with_two_dot():
    relative_path, action = split_dotted_path("posts.images.index")
    assert relative_path == "posts/images"
    assert action == "index"

def test_split_dotted_path_with_capital_letters():
    relative_path, action = split_dotted_path("Admin.Users.Show")
    assert relative_path == "admin/users"
    assert action == "show"


def test_crud_mapping_route_case_index():
    assert crud_mapping_route('index', 'posts', 'post') == '/posts'

def test_crud_mapping_route_case_create():
    assert crud_mapping_route('create', 'posts', 'post') == '/posts/create'

def test_crud_mapping_route_case_store():
    assert crud_mapping_route('store', 'posts', 'post') == '/posts'

def test_crud_mapping_route_case_show():
    assert crud_mapping_route('show', 'posts', 'post') == '/posts/<int:post_id>'

def test_crud_mapping_route_case_edit():
    assert crud_mapping_route('edit', 'posts', 'post') == '/posts/<int:post_id>/edit'

def test_crud_mapping_route_case_update():
    assert crud_mapping_route('update', 'posts', 'post') == '/posts/<int:post_id>'

def test_crud_mapping_route_case_destroy():
    assert crud_mapping_route('destroy', 'posts', 'post') == '/posts/<int:post_id>/delete'

def test_crud_mapping_route_case_delete():
    assert crud_mapping_route('delete', 'posts', 'post') == '/posts/<int:post_id>/delete'

def test_crud_mapping_route_case_with_path_like_resource():
    'admin.posts.comments.show'
    assert crud_mapping_route('show', 'admin/posts/comments', 'comment') == '/admin/posts/comments/<int:comment_id>'

