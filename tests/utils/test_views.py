from flask_commands.utils.views import view_make_file

def test_view_make_file_success(tmp_path, monkeypatch):
    # posts.index
    project_root = tmp_path
    post_template_dir = project_root / "app" / "templates"
    post_template_dir.mkdir(parents=True)
    monkeypatch.chdir(project_root)

    success, message = view_make_file("app/templates/posts/index.html")
    assert success is True
    assert "New view created" in message

def test_view_make_file_file_exists(tmp_path, monkeypatch):
    project_root = tmp_path
    post_template_dir = project_root / "app" / "templates" / "posts"
    post_template_dir.mkdir(parents=True)
    index_file = post_template_dir / "index.html"
    index_file.write_text("", encoding="utf-8")

    monkeypatch.chdir(project_root)
    # posts.index
    success, message = view_make_file("app/templates/posts/index.html")

    assert success is False
    assert "View Already Exists" in message

def test_view_make_file_exception(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise Exception("processor overload")

    monkeypatch.setattr(
        "flask_commands.utils.views.write_file",
        boom
    )

    success, message = view_make_file("app/templates/posts/index.html")
    assert success is False
    assert "Failed to create view" in message
