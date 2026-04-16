import os
import pytest
import flask_commands.utils.files as files_module
from flask_commands.utils.files import (
    file_append_file,
    file_copy_templates,
    file_insert_import_into_lines,
    file_insert_flask_import_name_into_lines,
    file_is_project_root,
    file_write_file,
    _read_template)

def test_file_append_file_success(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("I'm all alone please join me.", encoding="utf-8")
    file_append_file(str(file_path), ["I'm here!"])
    assert file_path.read_text(encoding="utf-8") == "I'm all alone please join me.\nI'm here!\n"

def test_file_append_file_fails_if_file_does_not_exists(tmp_path):
    file_path = tmp_path / "test.txt"
    with pytest.raises(FileNotFoundError):
        file_append_file(str(file_path), ["I'm here!"])

def test_file_copy_templates_skips_ds_store_and_pyc(tmp_path, monkeypatch):
    calls = []
    project_root_directory_path = os.path.join(
        os.path.dirname(os.path.dirname(files_module.__file__)),
        "project",
    )

    def fake_walk(_):
        yield (project_root_directory_path, [], [".DS_Store", "compiled.pyc", "keep.txt"])

    monkeypatch.setattr(files_module.os, "walk", fake_walk)
    monkeypatch.setattr(files_module, "_read_template", lambda _: "content")


    def fake_file_write_file(path, contents):
        calls.append((path, contents))

    monkeypatch.setattr(files_module, "file_write_file", fake_file_write_file)

    file_copy_templates(str(tmp_path), include_db=True, replacements=None)

    assert len(calls) == 1
    assert calls[0][0].endswith("keep.txt")

def test_file_copy_templates_skips_models_when_db_disabled(tmp_path, monkeypatch):
    calls = []
    project_root_directory_path = os.path.join(
        os.path.dirname(os.path.dirname(files_module.__file__)),
        "project",
    )

    def fake_walk(_):
        yield (project_root_directory_path, [], ["keep.txt"])
        yield (
            os.path.join(project_root_directory_path, "app", "models"),
            [],
            ["user.py"],
        )

    monkeypatch.setattr(files_module.os, "walk", fake_walk)
    monkeypatch.setattr(files_module, "_read_template", lambda _: "content")

    def fake_file_write_file(path, contents):
        calls.append(path)

    monkeypatch.setattr(files_module, "file_write_file", fake_file_write_file)

    file_copy_templates(str(tmp_path), include_db=False, replacements=None)

    assert len(calls) == 1
    assert calls[0].endswith("keep.txt")
    assert any(path.endswith("keep.txt") for path in calls)
    assert not any(path.endswith("user.py") for path in calls)
    assert not any(os.path.join("app", "models") in path for path in calls)

def test_file_copy_templates_uses_no_db_override_for_app_init(tmp_path):
    file_copy_templates(
        str(tmp_path),
        include_db=False,
        replacements=None,
    )

    package_root = os.path.dirname(os.path.dirname(files_module.__file__))
    no_db_app_init = os.path.join(package_root, "project_no_db", "app", "__init__.py")
    db_app_init = os.path.join(package_root, "project", "app", "__init__.py")

    copied_app_init = tmp_path / "app" / "__init__.py"
    copied_contents = copied_app_init.read_text(encoding="utf-8")

    assert copied_app_init.exists()
    assert copied_contents == _read_template(no_db_app_init)
    assert copied_contents != _read_template(db_app_init)

def test_file_copy_templates_applies_replacements(tmp_path, monkeypatch):
    calls = []
    project_root_directory_path = os.path.join(
        os.path.dirname(os.path.dirname(files_module.__file__)),
        "project",
    )

    def fake_walk(_):
        yield (project_root_directory_path, [], ["keep.txt"])

    monkeypatch.setattr(files_module.os, "walk", fake_walk)
    monkeypatch.setattr(files_module, "_read_template", lambda _: "Hello {{name}}")

    def fake_file_write_file(path, contents):
        calls.append((path, contents))

    monkeypatch.setattr(files_module, "file_write_file", fake_file_write_file)

    file_copy_templates(
        str(tmp_path),
        include_db=True,
        replacements={"{{name}}": "World"},
    )

    assert len(calls) == 1
    _, contents = calls[0]
    assert contents == ["Hello World"]

def test_file_insert_import_into_lines_with_blank_at_the_start():
    lines = ["", "from flask import redirect, url_for", "", "print('hello')"]
    import_statement = 'from flask import render_template'
    new_lines = file_insert_import_into_lines(lines=lines, import_statement=import_statement)
    expected_outcome = [
        '',
        'from flask import redirect, url_for',
        'from flask import render_template',
        '',
        "print('hello')"
    ]
    assert new_lines == expected_outcome

def test_file_insert_import_into_lines_with_leading_blank_lines_and_no_existing_imports():
    lines = ["import os", "", "", "print('hello')", "", "print('bye')", ""]
    import_statement = "from flask import render_template"

    new_lines = file_insert_import_into_lines(
        lines=lines,
        import_statement=import_statement,
    )

    expected_outcome = [
        "import os",
        "from flask import render_template",
        "",
        "",
        "print('hello')",
        "",
        "print('bye')",
        ""
    ]
    assert new_lines == expected_outcome

def test_file_insert_import_into_lines_with_empty_lines_list():
    new_lines = file_insert_import_into_lines(
        lines=[],
        import_statement="from flask import render_template",
    )

    assert new_lines == ["from flask import render_template"]

def test_file_insert_flask_import_name_into_lines_appends_missing_method():
    lines = ["from flask import render_template", "", "print('hello')"]

    new_lines = file_insert_flask_import_name_into_lines(
        lines=lines,
        missing_method="redirect",
    )

    expected_outcome = [
        "from flask import render_template, redirect",
        "",
        "print('hello')",
    ]
    assert new_lines == expected_outcome

def test_file_insert_flask_import_name_into_lines_does_not_duplicate_existing_method():
    lines = ["from flask import render_template, redirect", "", "print('hello')"]

    new_lines = file_insert_flask_import_name_into_lines(
        lines=lines,
        missing_method="redirect",
    )

    expected_outcome = [
        "from flask import render_template, redirect",
        "",
        "print('hello')",
    ]
    assert new_lines == expected_outcome


def test_file_insert_flask_import_name_into_lines_inserts_full_import_when_no_flask_import_exists():
    lines = ["import os", "", "print('hello')"]

    new_lines = file_insert_flask_import_name_into_lines(
        lines=lines,
        missing_method="redirect",
    )

    expected_outcome = [
        "import os",
        "from flask import redirect",
        "",
        "print('hello')",
    ]
    assert new_lines == expected_outcome

def test_file_is_project_root_true(tmp_path, monkeypatch):
    app_directory = tmp_path / "app"
    app_directory.mkdir()
    (tmp_path / "run.py").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    is_successful = file_is_project_root()
    assert is_successful is True

def test_file_is_project_root_false(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    is_successful = file_is_project_root()
    captured = capsys.readouterr()

    assert is_successful is False
    assert "Warning: You are not currently in a Flask project root directory" in captured.out

def test_file_write_file_success(tmp_path):
    file_path = tmp_path / "test.txt"
    file_write_file(file_path, ["hello", "world"])

    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == "hello\nworld\n"

def test_file_write_file_fails_if_file_exists(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text(
        "I already exist don't write over me",
        encoding="utf-8")

    # Expect a FileExistsError
    with pytest.raises(FileExistsError):
        file_write_file(file_path, ["hello", "world"])

    # Ensure the original content is still intact
    assert file_path.read_text(encoding="utf-8") == "I already exist don't write over me"

def test_file_write_file_nested(tmp_path):
    file_path = tmp_path / 'nested' / "template.txt"
    file_write_file(file_path, ["hello", "world"])

    assert (tmp_path / 'nested').is_dir()
    assert file_path.read_text(encoding="utf-8") == "hello\nworld\n"

def test_file_write_file_creates_missing_parent_directories_for_nested_path(tmp_path):
    file_path = tmp_path / "deep" / "nested" / "template.txt"

    file_write_file(str(file_path), ["hello", "world"])

    assert (tmp_path / "deep").is_dir()
    assert (tmp_path / "deep" / "nested").is_dir()
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == "hello\nworld\n"

def test_file_write_file_without_directory_component(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    file_write_file("test.txt", ["hello", "world"])

    file_path = tmp_path / "test.txt"
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == "hello\nworld\n"

def test__read_template_reads_contents(tmp_path):
    file_path = tmp_path / "template.txt"
    file_path.write_text("hello\nworld\n", encoding="utf-8")

    contents = _read_template(str(file_path))

    assert contents == "hello\nworld\n"
