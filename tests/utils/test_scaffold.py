from re import split
import pytest
from flask_commands.utils.scaffold import (
    filter_falsy,
    normalize_dotted_path_with_action,
    split_dotted_path_with_action_into_relative_path_and_action,
    split_pascal_case,
)

@pytest.mark.parametrize(
    "raw, expected",
    [
        (['a', 'b', 'c'], ['a', 'b', 'c']),
        (['0', '1', '2'], ['0', '1', '2']),
        ([0, 1, 2], [1, 2]),
        ([None, 1, 2], [1, 2]),
        (['', '1', '2'], ['1', '2'])
    ]
)
def test_filter_falsy(raw, expected):
    assert filter_falsy(raw) == expected

# TODO: put in test for generate_restful_route and have chat write a doc string for generate_restful_route

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Admin.Posts-Index", "admin.posts_index"),
        ("  admin..posts__show  ", "admin.posts_show"),
        ("___Posts...", "posts"),
        (".-Admin-.-", "admin"),
        ("posts.index", "posts.index"),
        ("posts--index", "posts_index"),
        ("posts..index", "posts.index"),
        ("posts__index", "posts_index"),
        ("posts.-.index", "posts.index"),
        ("admin/users.index", "admin.users.index"),
        ("admin/.users//index", "admin.users.index"),
        ("/.index", "index"),
    ]
)
def test_normalize_dotted_path_with_action_success(raw, expected):
    is_successful, value = normalize_dotted_path_with_action(raw)
    assert is_successful is True
    assert value == expected

@pytest.mark.parametrize(
        "raw", ["", "   ", ".", "..", "_", "__", "-", "--", "._-", "  ..__  "]
)
def test_normalize_dotted_path_with_action_empty_raises(raw):
    is_successful, value = normalize_dotted_path_with_action(raw)
    assert is_successful is False
    assert "Error" in value

def test_normalize_dotted_path_with_action_invalid_characters():
    is_successful, value = normalize_dotted_path_with_action("posts.$index")
    assert is_successful is False
    assert "allowed: letters, numbers, underscore" in value

def test_split_dotted_path_with_action_into_relative_path_and_action_with_no_dot():
    relative_path, action = split_dotted_path_with_action_into_relative_path_and_action("index")
    assert relative_path == ""
    assert action == "index"

def test_split_dotted_path_with_action_into_relative_path_and_action_with_one_dot():
    relative_path, action = split_dotted_path_with_action_into_relative_path_and_action("posts.show")
    assert relative_path == "posts"
    assert action == "show"

def test_split_dotted_path_with_action_into_relative_path_and_action_with_two_dot():
    relative_path, action = split_dotted_path_with_action_into_relative_path_and_action("posts.images.index")
    assert relative_path == "posts/images"
    assert action == "index"

def test_split_dotted_path_with_action_into_relative_path_and_action_with_capital_letters():
    relative_path, action = split_dotted_path_with_action_into_relative_path_and_action("admin.users.show")
    assert relative_path == "admin/users"
    assert action == "show"

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("AdminUserProfileImage", ["Admin", "User", "Profile", "Image"]),
        ("HTTPResponse", ["HTTP", "Response"]),
        ("XCoordinate", ["X", "Coordinate"]),
        ("UserAPI", ["User", "API"]),
        ("JSONToXML", ["JSON", "To", "XML"]),
        ("OAuthToken", ["O", "Auth", "Token"]),
        ("A", ["A"]),
        ("ABC", ["ABC"]),
        ("", []),
    ],
)
def test_split_pascal_case(raw, expected):
    assert split_pascal_case(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("recipes/comments/index", "recipes.comments.index"),
        ("shopping-list.index", "shopping_list.index"),
        ("recipes..comments...index", "recipes.comments.index"),
        ("Recipes.Comments.Index", "recipes.comments.index"),
    ],
)
def test_docs_core_ideas_view_input_normalization_examples(raw, expected):
    is_successful, value = normalize_dotted_path_with_action(raw)

    assert is_successful is True
    assert value == expected
