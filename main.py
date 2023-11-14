import sys
import glob
import subprocess

import utils.file_processing as process
from utils.text_editor import Editor
from typing import List


def main(input_files: List[str], output_dir: str, configfile: str = "config_prompt/anonymize_emails-NER.yaml"):
    """
    Runs the email editor from the config file.
    :param input_files: List of files of emails
    :param output_dir: Directory where to store edited emails
    :param configfile: config file with prompt instructions
    :return:
    """
    subprocess.call(f"mkdir -p {output_dir}", shell=True)
    subprocess.call(f"mkdir -p data/history", shell=True)
    
    text_editor = Editor(configfile)
    
    for i, input_file in enumerate(input_files):
        input_text = process.read_file(input_file)
        file_name = input_file.split("/")[-1]

        output_text = text_editor.edit_text(input_text)
        text_editor.save_history(f"data/history/{file_name.split('.')[0]}_history.json")
        
        process.write_file(f"{output_dir}/{file_name}", output_text)


if __name__ == "__main__":
    if len(sys.argv[1:]) == 0:
        input_files = "data/input/email_*de.txt"
        output_dir = "data/output"
    else:
        input_files = sys.argv[1]
        output_dir = sys.argv[2]

    main(glob.glob(input_files), output_dir)