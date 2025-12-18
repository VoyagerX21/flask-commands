from flask_commands.utils.naming import camel_to_snake

def test_camel_to_snake_basic():
    assert camel_to_snake("camelCaseString") == "camel_case_string"

def test_camel_to_snake_leading_capital():
    assert camel_to_snake("PascalCaseString") == "pascal_case_string"

def test_camel_to_snake_multiple_capitals_together():
    assert camel_to_snake("HTTPResponse") == "http_response"
    assert camel_to_snake("MyLastNameIsHARRIOTAndMyFirstNameIsJAMES") == "my_last_name_is_harriot_and_my_first_name_is_james"
