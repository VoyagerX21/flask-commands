from flask_commands.utils.models import (
    generate_table_name_from_model_name,
    model_infer_name_from,
    model_make_file
)

def test_generate_table_name_from_model_name():
    assert generate_table_name_from_model_name('Post') == "posts"
    assert generate_table_name_from_model_name('Category') == "categories"
    assert generate_table_name_from_model_name('Class') == "classes"


def test_model_infer_name_from_reative_path():
    message, model_name = model_infer_name_from("posts", "posts.index")
    assert "Infered the model name" in message
    assert model_name == "Post"

def test_model_infer_name_from_dotted_path_with_name():
    message, model_name = model_infer_name_from("", "posts")
    assert "Infered the model name" in message
    assert model_name == "Post"
