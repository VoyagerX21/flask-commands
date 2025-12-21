# import os
# import pytest
# from click.testing import CliRunner
# from unittest.mock import patch, MagicMock

# from flask_commands.commands.view import make_view  # replace with the actual import path


# @pytest.fixture
# def runner():
#     return CliRunner()


# def test_basic_view_creation(runner):
#     """Test creating a view without controller, route, or model."""
#     with patch("flask_commands.commands.view.view_make_file") as mock_view_make:
#         mock_view_make.return_value = None
#         result = runner.invoke(make_view, ["posts.index"])
#         assert result.exit_code == 0
#         mock_view_make.assert_called_once()
#         assert "📄 File created at" in result.output


# def test_view_creation_with_existing_file(runner):
#     """Simulate FileExistsError when view file already exists."""
#     with patch("flask_commands.commands.view.view_make_file", side_effect=FileExistsError):
#         result = runner.invoke(make_view, ["posts.index"])
#         assert result.exit_code == 0
#         assert "⚠️ Warning: A file already exist" in result.output


# @patch("flask_commands.utils.controllers.controller_infer_name_from", return_value="PostController")
# @patch("flask_commands.utils.controllers.controller_make_file", return_value=(True, "Controller created"))
# @patch("flask_commands.commands.view.view_make_file")
# def test_generate_controller(mock_view, mock_controller_make, mock_controller_infer, runner):
#     result = runner.invoke(make_view, ["posts.index", "-c"])
#     assert result.exit_code == 0
#     mock_controller_infer.assert_called_once_with("posts")
#     mock_controller_make.assert_called_once_with(
#         "PostController", "index", os.path.join("posts", "index.html")
#     )
#     assert "Controller created" in result.output


# @patch("flask_commands.utils.routes.route_infer_name_from", return_value="posts")
# @patch("flask_commands.utils.routes.route_make_directory_and_register_blueprint", return_value=(True, "Route created"))
# @patch("flask_commands.commands.view.view_make_file")
# def test_generate_route(mock_view, mock_route_make, mock_route_infer, runner):
#     result = runner.invoke(make_view, ["posts.index", "-r"])
#     assert result.exit_code == 0
#     mock_route_infer.assert_called_once()
#     mock_route_make.assert_called_once()
#     assert "Route created" in result.output


# @patch("flask_commands.utils.models.model_infer_name_from", return_value=("Inferred model as Post", "Post"))
# @patch("flask_commands.utils.models.model_make_file", return_value=(True, "Model created"))
# @patch("flask_commands.commands.view.view_make_file")
# def test_generate_model(mock_view, mock_model_make, mock_model_infer, runner):
#     result = runner.invoke(make_view, ["posts.index", "-m"])
#     assert result.exit_code == 0
#     mock_model_infer.assert_called_once()
#     mock_model_make.assert_called_once()
#     assert "Model created" in result.output


# def test_all_flags_combined(runner):
#     """Test using -c -r -m together, mocking all utility functions."""
#     with patch("flask_commands.commands.view.view_make_file") as mock_view, \
#         patch("flask_commands.utils.controllers.controller_infer_name_from", return_value="PostController") as mock_c_infer, \
#         patch("flask_commands.utils.controllers.controller_make_file", return_value=(True, "Controller created")) as mock_c_make, \
#         patch("flask_commands.utils.routes.route_infer_name_from", return_value="posts") as mock_r_infer, \
#         patch("flask_commands.utils.routes.route_make_directory_and_register_blueprint", return_value=(True, "Route created")) as mock_r_make, \
#         patch("flask_commands.utils.models.model_infer_name_from", return_value=("Inferred model as Post", "Post")) as mock_m_infer, \
#         patch("flask_commands.utils.models.model_make_file", return_value=(True, "Model created")) as mock_m_make:

#         result = runner.invoke(make_view, ["posts.index", "-c", "-r", "-m"])
#         assert result.exit_code == 0
#         assert "Controller created" in result.output
#         assert "Route created" in result.output
#         assert "Model created" in result.output
