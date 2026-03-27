from flask_commands.utils.data_types import (
    ActionResult, 
    ControllerResult,
    CrudResult,
    ModelResult, 
    RouteResult, 
    ScaffoldStatus
)
from flask_commands.utils.presents import (
    _controller_crud_summary, 
    _crud_route_summary,
    _crud_wiring,
    _generated_from_flags,
    present_output_blocks
)


def test__generated_from_flags_renders_each_update():
    message = _generated_from_flags([
        "Using --flat. Generated model(s): Comment",
        "Generated controller: CommentController",
    ])

    assert "Generated From Flags" in message
    assert "Using --flat. Generated model(s): Comment" in message
    assert "Generated controller: CommentController" in message

def test__controller_crud_summary_existing_controller_lists_added_and_existing_methods():
    controller_result = ControllerResult(
        controller_name="CommentController",
        controller_file_path="app/controllers/comment_controller.py",
        status=ScaffoldStatus.EXISTS,
        is_successful=True,
        registration_file_path="app/controllers/__init__.py",
        methods_added=["index", "store"],
        methods_existing=["show"],
    )

    message = _controller_crud_summary(controller_result)

    assert "Reused Existing Controller Class" in message
    assert "CommentController already existed" in message
    assert "app/controllers/comment_controller.py" in message
    assert "Added controller methods: index, store" in message
    assert "Controller methods already present: show" in message
    assert "Registered CommentController" not in message

def test__controller_crud_summary_added_controller_includes_registration():
    controller_result = ControllerResult(
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
        status=ScaffoldStatus.ADDED,
        is_successful=True,
        registration_file_path="app/controllers/__init__.py",
        methods_added=["index"],
        methods_existing=[],
    )

    message = _controller_crud_summary(controller_result)

    assert "Created Controller Class" in message
    assert "Created a new controller called PostController" in message
    assert "app/controllers/post_controller.py" in message
    assert "Registered PostController at app/controllers/__init__.py" in message
    assert "Added controller methods: index" in message

def test__controller_crud_summary_existing_methods_without_added_methods():
    controller_result = ControllerResult(
        controller_name="CommentController",
        controller_file_path="app/controllers/comment_controller.py",
        status=ScaffoldStatus.EXISTS,
        is_successful=True,
        methods_added=[],
        methods_existing=["show", "edit"],
    )

    message = _controller_crud_summary(controller_result)

    assert "Reused Existing Controller Class" in message
    assert "Added controller methods" not in message
    assert "Controller methods already present: show, edit" in message

def test__crud_route_summary_created_directory_includes_files_blueprint_and_added_routes():
    route_result = RouteResult(
        directory_status=ScaffoldStatus.ADDED,
        is_successful=True,
        route_init_path="app/routes/posts/__init__.py",
        route_file_path="app/routes/posts/routes.py",
        blueprint_name="posts",
        blueprint_registration_file_path="app/__init__.py",
    )
    action_results = [
        ActionResult(
            action="index",
            http_method="GET",
            route_name="/posts",
            url_for_example="Reference this route with url_for('posts.index')",
            is_successful=True,
            route_status=ScaffoldStatus.ADDED,
        ),
        ActionResult(
            action="show",
            http_method="GET",
            route_name="/posts/<int:post_id>",
            url_for_example="Reference this route with url_for('posts.show', post_id=1)",
            is_successful=True,
            route_status=ScaffoldStatus.ADDED,
        ),
        ActionResult(
            action="edit",
            http_method="GET",
            route_name="/posts/<int:post_id>/edit",
            url_for_example="Reference this route with url_for('posts.edit', post_id=1)",
            is_successful=True,
            route_status=ScaffoldStatus.EXISTS,
        ),
    ]

    message = _crud_route_summary(route_result, action_results)

    assert "Created New Route Directory" in message
    assert "Created __init__.py at app/routes/posts/__init__.py" in message
    assert "Created routes.py at app/routes/posts/routes.py" in message
    assert "Registered the new route directory as posts at app/__init__.py" in message
    assert "Added route functions: index, show" in message

def test__crud_route_summary_existing_directory_skips_creation_lines():
    route_result = RouteResult(
        directory_status=ScaffoldStatus.EXISTS,
        is_successful=True,
        route_init_path="app/routes/posts/__init__.py",
        route_file_path="app/routes/posts/routes.py",
        blueprint_name="posts",
        blueprint_registration_file_path="app/__init__.py",
    )
    action_results = [
        ActionResult(
            action="update",
            http_method="POST",
            route_name="/posts/<int:post_id>/update",
            url_for_example="Reference this route with url_for('posts.update', post_id=1)",
            is_successful=True,
            route_status=ScaffoldStatus.ADDED,
        )
    ]

    message = _crud_route_summary(route_result, action_results)

    assert "Updated Existing Route Directory" in message
    assert "Created __init__.py" not in message
    assert "Created routes.py" not in message
    assert "Registered the new route directory" not in message
    assert "Added route functions: update" in message

def test__crud_route_summary_created_directory_without_init_file_line():
    '''
    This test intentionally exercise defensive formatter branches that do not
    normally occur in the real scaffold flow, but I keep them for full 
    coverage.
    '''
    route_result = RouteResult(
        directory_status=ScaffoldStatus.ADDED,
        is_successful=True,
        route_init_path=None,
        route_file_path="app/routes/posts/routes.py",
        blueprint_name="posts",
        blueprint_registration_file_path="app/__init__.py",
    )
    action_results = [
        ActionResult(
            action="index",
            http_method="GET",
            route_name="/posts",
            url_for_example="Reference this route with url_for('posts.index')",
            is_successful=True,
            route_status=ScaffoldStatus.ADDED,
        ),
    ]

    message = _crud_route_summary(route_result, action_results)

    assert "Created New Route Directory" in message
    assert "Created __init__.py" not in message
    assert "Created routes.py at app/routes/posts/routes.py" in message
    assert "Registered the new route directory as posts at app/__init__.py" in message
    assert "Added route functions: index" in message

def test__crud_route_summary_created_directory_without_routes_file_line():
    '''
    This test intentionally exercise defensive formatter branches that do not
    normally occur in the real scaffold flow, but I keep them for full 
    coverage.
    '''
    route_result = RouteResult(
        directory_status=ScaffoldStatus.ADDED,
        is_successful=True,
        route_init_path="app/routes/posts/__init__.py",
        route_file_path=None,
        blueprint_name="posts",
        blueprint_registration_file_path="app/__init__.py",
    )
    action_results = [
        ActionResult(
            action="index",
            http_method="GET",
            route_name="/posts",
            url_for_example="Reference this route with url_for('posts.index')",
            is_successful=True,
            route_status=ScaffoldStatus.ADDED,
        ),
    ]

    message = _crud_route_summary(route_result, action_results)

    assert "Created New Route Directory" in message
    assert "Created __init__.py at app/routes/posts/__init__.py" in message
    assert "Created routes.py" not in message
    assert "Registered the new route directory as posts at app/__init__.py" in message
    assert "Added route functions: index" in message

def test__crud_route_summary_created_directory_without_blueprint_registration_line():
    '''
    This test intentionally exercise defensive formatter branches that do not
    normally occur in the real scaffold flow, but I keep them for full 
    coverage.
    '''
    route_result = RouteResult(
        directory_status=ScaffoldStatus.ADDED,
        is_successful=True,
        route_init_path="app/routes/posts/__init__.py",
        route_file_path="app/routes/posts/routes.py",
        blueprint_name=None,
        blueprint_registration_file_path=None,
    )
    action_results = [
        ActionResult(
            action="index",
            http_method="GET",
            route_name="/posts",
            url_for_example="Reference this route with url_for('posts.index')",
            is_successful=True,
            route_status=ScaffoldStatus.ADDED,
        ),
    ]

    message = _crud_route_summary(route_result, action_results)

    assert "Created New Route Directory" in message
    assert "Created __init__.py at app/routes/posts/__init__.py" in message
    assert "Created routes.py at app/routes/posts/routes.py" in message
    assert "Registered the new route directory" not in message
    assert "Added route functions: index" in message

def test__crud_route_summary_created_directory_without_added_route_functions_line():
    '''
    This test intentionally exercise defensive formatter branches that do not
    normally occur in the real scaffold flow, but I keep them for full 
    coverage.
    '''
    route_result = RouteResult(
        directory_status=ScaffoldStatus.ADDED,
        is_successful=True,
        route_init_path="app/routes/posts/__init__.py",
        route_file_path="app/routes/posts/routes.py",
        blueprint_name="posts",
        blueprint_registration_file_path="app/__init__.py",
    )
    action_results = [
        ActionResult(
            action="index",
            http_method="GET",
            route_name="/posts",
            url_for_example="Reference this route with url_for('posts.index')",
            is_successful=True,
            route_status=ScaffoldStatus.EXISTS,
        ),
    ]

    message = _crud_route_summary(route_result, action_results)

    assert "Created New Route Directory" in message
    assert "Created __init__.py at app/routes/posts/__init__.py" in message
    assert "Created routes.py at app/routes/posts/routes.py" in message
    assert "Registered the new route directory as posts at app/__init__.py" in message
    assert "Added route functions" not in message

def test__crud_wiring_renders_get_and_post_details():
    action_results = [
        ActionResult(
            action="index",
            http_method="GET",
            route_name="/posts",
            url_for_example="Reference this route with url_for('posts.index')",
            is_successful=True,
            visit_example="Visit the new route at /posts",
            view_file_path="app/templates/posts/index.html",
            view_status=ScaffoldStatus.ADDED,
            route_status=ScaffoldStatus.ADDED,
        ),
        ActionResult(
            action="store",
            http_method="POST",
            route_name="/posts",
            url_for_example="Reference this route with url_for('posts.store')",
            is_successful=True,
            view_status=ScaffoldStatus.SKIPPED,
            route_status=ScaffoldStatus.ADDED,
        ),
    ]

    message = _crud_wiring(action_results)

    assert "Generated CRUD Wiring" in message
    assert "index (GET)" in message
    assert "Added view file at app/templates/posts/index.html" in message
    assert "Visit the new route at /posts" in message
    assert "Reference this route with url_for('posts.index')" in message
    assert "store (POST)" in message
    assert "Reference this route with url_for('posts.store')" in message

def test__crud_wiring_existing_get_route_skips_visit_and_url_lines():
    action_results = [
        ActionResult(
            action="show",
            http_method="GET",
            route_name="/posts/<int:post_id>",
            url_for_example="Reference this route with url_for('posts.show', post_id=1)",
            is_successful=True,
            visit_example="Visit the new route at /posts/1",
            view_file_path="app/templates/posts/show.html",
            view_status=ScaffoldStatus.ADDED,
            route_status=ScaffoldStatus.EXISTS,
        ),
        ActionResult(
            action="store",
            http_method="POST",
            route_name="/posts",
            url_for_example="Reference this route with url_for('posts.store')",
            is_successful=True,
            view_status=ScaffoldStatus.SKIPPED,
            route_status=ScaffoldStatus.ADDED,
        ),
    ]

    message = _crud_wiring(action_results)

    print()
    print(message)

    assert "show (GET)" in message
    assert "Added view file at app/templates/posts/show.html" in message
    assert "Visit the new route at /posts/1" not in message
    assert "Reference this route with url_for('posts.show', post_id=1)" not in message
    assert "store (POST)" in message
    assert "Reference this route with url_for('posts.store')" in message

def test__crud_wiring_added_route_without_url_for_example():
    '''
    This test intentionally exercise defensive formatter branches that do not
    normally occur in the real scaffold flow, but I keep them for full 
    coverage.
    '''
    action_results = [
        ActionResult(
            action="store",
            http_method="POST",
            route_name="/posts",
            url_for_example="",
            is_successful=True,
            view_status=ScaffoldStatus.SKIPPED,
            route_status=ScaffoldStatus.ADDED,
        ),
    ]

    message = _crud_wiring(action_results)

    assert "Generated CRUD Wiring" in message
    assert "store (POST)" in message
    assert "Reference this route with url_for" not in message

def test_present_output_blocks_non_crud_returns_info_then_messages():
    blocks = present_output_blocks(
        info_updates=["Using --flat. Generated model(s): Comment"],
        message_updates=["Created model message"],
        crud_result=None,
    )

    assert len(blocks) == 2
    assert "Generated From Flags" in blocks[0]
    assert "Using --flat. Generated model(s): Comment" in blocks[0]
    assert blocks[1] == "Created model message"

def test_present_output_blocks_crud_orders_controller_messages_route_wiring_and_warnings():
    controller_result = ControllerResult(
        controller_name="CommentController",
        controller_file_path="app/controllers/comment_controller.py",
        status=ScaffoldStatus.EXISTS,
        is_successful=True,
        methods_added=["index"],
        methods_existing=["show"],
    )
    model_result = ModelResult(is_successful=True)
    route_result = RouteResult(
        directory_status=ScaffoldStatus.ADDED,
        is_successful=True,
        route_init_path="app/routes/comments/__init__.py",
        route_file_path="app/routes/comments/routes.py",
        blueprint_name="comments",
        blueprint_registration_file_path="app/__init__.py",
    )
    action_results = [
        ActionResult(
            action="index",
            http_method="GET",
            route_name="/comments",
            url_for_example="Reference this route with url_for('comments.index')",
            is_successful=True,
            visit_example="Visit the new route at /comments",
            view_file_path="app/templates/comments/index.html",
            view_status=ScaffoldStatus.ADDED,
            route_status=ScaffoldStatus.ADDED,
        )
    ]
    crud_result = CrudResult(
        controller_result=controller_result,
        model_result=model_result,
        is_successful=True,
        route_result=route_result,
        action_results=action_results,
        message_updates=["Created fallback model message"],
        warning_updates=["Warning block"],
    )

    blocks = present_output_blocks(
        info_updates=["Using --nest. Generated model(s): Post, Comment"],
        message_updates=["Created requested model message"],
        crud_result=crud_result,
    )

    print()
    print(blocks)

    assert len(blocks) == 7
    assert "Generated From Flags" in blocks[0]
    assert "Reused Existing Controller Class" in blocks[1]
    assert blocks[2] == "Created requested model message"
    assert blocks[3] == "Created fallback model message"
    assert "Created New Route Directory" in blocks[4]
    assert "Generated CRUD Wiring" in blocks[5]
    assert blocks[6] == "Warning block"

def test_present_output_blocks_crud_without_route_result_skips_route_summary():
    controller_result = ControllerResult(
        controller_name="PostController",
        controller_file_path="app/controllers/post_controller.py",
        status=ScaffoldStatus.ADDED,
        is_successful=True,
        methods_added=["index"],
        methods_existing=[],
    )
    crud_result = CrudResult(
        controller_result=controller_result,
        model_result=ModelResult(is_successful=True),
        is_successful=True,
        route_result=None,
        action_results=[
            ActionResult(
                action="index",
                http_method="GET",
                route_name="/posts",
                url_for_example="Reference this route with url_for('posts.index')",
                is_successful=True,
                visit_example="Visit the new route at /posts",
                view_file_path="app/templates/posts/index.html",
                view_status=ScaffoldStatus.ADDED,
                route_status=ScaffoldStatus.ADDED,
            )
        ],
        message_updates=[],
        warning_updates=[],
    )

    blocks = present_output_blocks(
        info_updates=[],
        message_updates=["Created model message"],
        crud_result=crud_result,
    )

    assert len(blocks) == 3
    assert "Created Controller Class" in blocks[0]
    assert blocks[1] == "Created model message"
    assert "Generated CRUD Wiring" in blocks[2]
    assert all("Route Directory" not in block for block in blocks)
