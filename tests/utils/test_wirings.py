import flask_commands.utils.wirings as wirings_module
from flask_commands.utils.wirings import wire_controller_route_view

def test_wire_get_with_existing_controller_and_route(monkeypatch):
    calls = []

    monkeypatch.setattr(wirings_module, "route_http_method_for_action", lambda *_: "GET")
    monkeypatch.setattr(
        wirings_module,
        "route_generate_route_folder_path_and_blueprint_name",
        lambda *_: ("app/routes/posts", "posts"),
    )
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
        dotted_path_with_action="posts.index",
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
    monkeypatch.setattr(
        wirings_module,
        "route_generate_route_folder_path_and_blueprint_name",
        lambda *_: ("app/routes/posts", "posts"),
    )
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
        dotted_path_with_action="posts.store",
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
    monkeypatch.setattr(
        wirings_module,
        "route_generate_route_folder_path_and_blueprint_name",
        lambda *_: ("app/routes/posts", "posts"),
    )

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
        dotted_path_with_action="posts.index",
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
    monkeypatch.setattr(
        wirings_module,
        "route_generate_route_folder_path_and_blueprint_name",
        lambda *_: ("app/routes/posts", "posts"),
    )
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
        dotted_path_with_action="posts.index",
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
    monkeypatch.setattr(
        wirings_module,
        "route_generate_route_folder_path_and_blueprint_name",
        lambda *_: ("app/routes/posts", "posts"),
    )

    def fake_exists(path):
        if path.endswith("app/controllers/post_controller.py"):
            return True  # so controller_add_method is used
        if path.endswith("app/routes/posts"):
            return False  # triggers route_make_directory_and_register_blueprint
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
        "route_make_directory_and_register_blueprint",
        lambda *args: (True, "route made"),
    )

    is_successful, messages = wire_controller_route_view(
        dotted_path_with_action="posts.index",
        relative_path="posts",
        action="index",
        controller_name="PostController",
        route_name="/posts",
    )

    assert is_successful is True
    assert messages == ["view successful", "controller successful", "route made"]
