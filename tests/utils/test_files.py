import os
import pytest
from flask_commands.utils.files import (
    append_file,
    insert_import_into_lines,
    is_project_root,
    write_file)

def test_append_file_success(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("I'm all alone please join me.", encoding="utf-8")
    append_file(str(file_path), ["I'm here!"])
    assert file_path.read_text(encoding="utf-8") == "I'm all alone please join me.\nI'm here!\n"

def test_append_file_fails_if_file_does_not_exists(tmp_path):
    file_path = tmp_path / "test.txt"
    with pytest.raises(FileNotFoundError):
        append_file(str(file_path), ["I'm here!"])

def test_is_project_root_true(tmp_path, monkeypatch):
    app_directory = tmp_path / "app"
    app_directory.mkdir()
    (tmp_path / "run.py").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    is_successful = is_project_root()
    assert is_successful is True

def test_is_project_root_false(tmp_path):
    is_successful = is_project_root()
    assert is_successful is False

def test_write_file_success(tmp_path):
    file_path = tmp_path / "test.txt"
    write_file(file_path, ["hello", "world"])

    assert file_path.exists()
    assert file_path.read_text() == "hello\nworld\n"

def test_write_file_fails_if_file_exists(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text(
        "I already exist don't write over me",
        encoding="utf-8")

    # Expect a FileExistsError
    with pytest.raises(FileExistsError):
        write_file(file_path, ["hello", "world"])

    # Ensure the original content is still intact
    assert file_path.read_text(encoding="utf-8") == "I already exist don't write over me"

def test_insert_import_into_lines_with_blank_at_the_start():
    lines = ["", "from flask import redirect, url_for"]
    import_statement = 'from flask import render_template'
    insert_import_into_lines(lines=lines, import_statement=import_statement)
