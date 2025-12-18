from flask_commands.utils.files import write_file

def test_write_file(tmp_path):
    file_path = tmp_path / "test.txt"
    write_file(file_path, ["hello", "world"])

    assert file_path.exists()
    assert file_path.read_text() == "hello\nworld\n"
