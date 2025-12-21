import pytest
from flask_commands.utils.files import append_file, write_file

def test_write_file_happy_path(tmp_path):
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


def test_append_file_happy_path(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("I'm all alone please join me.", encoding="utf-8")
    append_file(str(file_path), ["I'm here!"])
    assert file_path.read_text(encoding="utf-8") == "I'm all alone please join me.\nI'm here!\n"

def test_append_file_fails_if_file_does_not_exists(tmp_path):
    file_path = tmp_path / "test.txt"
    with pytest.raises(FileNotFoundError):
        append_file(str(file_path), ["I'm here!"])
