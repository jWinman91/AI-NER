import json


def read_file(file_path: str, field: str = "Nachricht") -> str:
    """
    Read text file.

    :param file_path: path for to the file
    :param field: field name of json file (if json)
    :return: return file as string
    """
    with open(file_path, "r", encoding="utf8") as f:
        if file_path.endswith(".json"):
            input_text = json.load(f)[field]
        else:
            input_text = f.read()
    return input_text


def write_file(file_path: str, edited_text: str):
    """
    Write edited text to file

    :param file_path: where to save the file
    :param edited_text: text to be saved
    :return: None
    """
    with open(file_path, "w", encoding="utf8") as f:
        f.write(edited_text)