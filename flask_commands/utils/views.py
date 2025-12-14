from .files import write_file

def view_make_file(destination_file_path: str, filename: str) -> None:
    content = []
    write_file(destination_file_path, content)
