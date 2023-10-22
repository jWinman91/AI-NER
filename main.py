import sys
import glob
import subprocess

import utils.file_processing as process
from utils.text_editor import Editor


def main(input_files: List[str], output_dir: str,
         configfile: str = "config_anonymize_email.yaml", modelfile: str = "model/mistral-7b-v0.1.Q4_K_M.gguf"):
    """
    Runs the email editor from the config file.
    :param input_files: List of files of emails
    :param output_dir: Directory where to store edited emails
    :param configfile: config file with prompt instructions
    :param modelfile: path to model to use
    :return:
    """
    for input_file in input_files:
        input_text = process.read_file(input_file)

        text_editor = Editor(configfile, modelfile)
        output_text = text_editor.edit_text(input_text)

        subprocess.call(f"mkdir -p {output_dir}", shell=True)
        file_name = input_file.split("/")[-1]
        process.write_file(f"{output_dir}/{file_name}", output_text)


if __name__ == "__main__":
    if len(sys.argv[1:]) == 0:
        input_files = "data/input/*.txt"
        output_dir = "data/output"
    else:
        input_files = sys.argv[1]
        output_dir = sys.argv[2]

    main(glob.glob(input_files), output_dir)