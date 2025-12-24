from flask_commands.utils.routes import (
    route_add_method,
    route_make_directory_and_register_blueprint,
    route_infer_name_from,
    generate_route_file_path_and_blueprint_name)

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
