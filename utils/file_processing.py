def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf8") as f:
        input_text = file_path.read()
    return input_text


def write_file(file_path: str, edited_text: str) -> str:
    with open(file_path, "w", encoding="utf8") as f:
        f.write(edited_text)