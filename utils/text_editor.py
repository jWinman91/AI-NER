import importlib
import numpy as np
import json
import yaml

from collections import OrderedDict
from nltk import tokenize
from typing import Dict


class Editor:
    def __init__(self, configfile: str):
        """
        Class to edit input text by using a Language Model.
        :param configfile: path to config file that defines location of config files
        """
        config_dict = self.load_yml(configfile)

        self._prompts = self.load_yml(config_dict["config_prompt"])

        model_types = set()
        for prompt_name, prompt_dict in self._prompts.items():
            model_types.add(prompt_dict["model_type"])

        self._model_types = {}
        for model_type in model_types:
            module_name = model_type.split("/")[0]
            model_name = model_type.split("/")[1]
            param_filename = config_dict["config_model"].get(module_name, None)

            params = self.load_yml(param_filename) if param_filename else {}

            module = importlib.import_module("model_type." + module_name)
            self._model_types[model_name] = getattr(module, model_name)(params)

        self._history_dict = OrderedDict()

    @staticmethod
    def load_yml(configfile: str) -> Dict:
        """
        Imports a YAML Configuration file
        :param configfile: Path to the YAML config file.
        :return: A dictionary containing the configuration data.
        """
        with open(configfile, "r") as b:
            try:
                data = yaml.safe_load(b)
            except yaml.YAMLError as err:
                print(err)
        return data

    def save_history(self, file_name: str):
        """
        Saves the history dictionary containing all edits to the input text.
        :param file_name: Name of file where to save the history
        :return: None
        """
        with open(file_name, "w+", encoding="utf8") as f:
            f.write(json.dumps(self._history_dict,
                               indent=4,
                               ensure_ascii=False,
                               default=lambda x: float(x) if isinstance(x, (float, np.float32)) else None
                               ))
        
        self._history_dict = OrderedDict()

    def edit_text(self, input_text: str) -> str:
        """
        Edits the input text based on instructions provided in the configuration file.
        :param input_text: Input text to be edited
        :return: Edited input text
        """
        self._history_dict[f"input_text"] = input_text
        for prompt_name, prompt_instruction in self._prompts.items():
            unique_patterns = set()
            output_text = list(self._history_dict.values())[-1]

            input_sentences = tokenize.sent_tokenize(output_text)
            for input_sentence in list(filter(None, input_sentences)):
                model_name = prompt_instruction["model_type"].split("/")[-1]
                find_name_entity = getattr(self._model_types[model_name], "find_name_entity")
                found_entities = find_name_entity(input_sentence,
                                                   prompt_name,
                                                   prompt_instruction,
                                                   self._history_dict)
                unique_patterns = unique_patterns.union(found_entities)

            self._history_dict[f"{prompt_name}_patterns"] = list(unique_patterns)

            unique_patterns.discard("FAILED")
            for pattern in unique_patterns:
                output_text = output_text.replace(pattern, prompt_instruction["replace_token"])

            self._history_dict[f"{prompt_name}_output_text"] = output_text

        return list(self._history_dict.values())[-1]