import importlib
import numpy as np
import json
import yaml

from utils.couch_db_handler import CouchDBHandler
from collections import OrderedDict
from typing import Dict, Union


class Editor:
    def __init__(self, config: Union[str, dict], config_model_db: Union[CouchDBHandler, None]):
        """
        Class to edit input text by using a Language Model.
        :param config: path to config file that defines location of config files
        :param config_model_db: db table where model configs are stored.
                                If None, then model_config better be a yaml file.
        """
        if type(config) == str:
            self._prompts = self.load_yml(config)
        else:
            self._prompts = config

        self._model_wrappers = dict()
        for prompt_name, prompt_dict in self._prompts.items():
            model = prompt_dict["model"]
            module_name = model["model_wrapper"].split("/")[0]
            model_name = model["model_wrapper"].split("/")[1]
            param_filename = model.get("model_config", None)
            
            if param_filename and param_filename.endswith(".yaml"):
                params = self.load_yml(param_filename)
            else:
                params = config_model_db.get_config(param_filename) if param_filename else {}

            if model_name in self._model_wrappers.keys():
                continue

            module = importlib.import_module("model_wrapper." + module_name)
            self._model_wrappers[model_name] = getattr(module, model_name)(params)

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

    @staticmethod
    def load_json(configfile: str) -> Dict:
        """
        Imports a JSON Configuration file
        :param configfile: Path to the JSON config file.
        :return: A dictionary containing the configuration data.
        """
        with open(configfile, "r") as b:
            try:
                data = json.load(b)
            except Exception as err:
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

    @staticmethod
    def replace_patterns(unique_patterns: Set[str], text: str, replace_token: str) -> str:
        """
        Replaces all patterns with given replace token.
        :param unique_patterns: patterns to be replaced.
        :param text: text string in which to replace the pattern
        :param replace_token: token which replaces the pattern
        :return: edited text
        """
        unique_patterns.discard("FAILED")
        unique_patterns.discard("")
        output_text = text
        for pattern in unique_patterns:
            output_text = output_text.replace(pattern, replace_token)
        return output_text

    def edit_text(self, input_text: str) -> str:
        """
        Edits the input text based on instructions provided in the configuration file.
        :param input_text: Input text to be edited
        :return: Edited input text
        """
        self._history_dict = OrderedDict()
        self._history_dict["input_text"] = input_text
        for prompt in self._prompts.items():
            output_text = list(self._history_dict.values())[-1]
            model_name = prompt[1]["model"]["model_wrapper"].split("/")[-1]

            run_model_wrapper = getattr(self._model_wrappers[model_name], "run")
            unique_patterns = run_model_wrapper(output_text, prompt, self._history_dict)

            if type(unique_patterns) is dict:
                self._history_dict[f"{prompt[0]}_patterns"] = list(set.union(*list(unique_patterns.values())))
                for entity_type, entities in unique_patterns.items():
                    output_text = self.replace_patterns(entities, output_text, prompt[1]["replace_token"][entity_type])
            else:
                self._history_dict[f"{prompt[0]}_patterns"] = list(unique_patterns)
                output_text = self.replace_patterns(unique_patterns, output_text, prompt[1]["replace_token"])
    
            self._history_dict[f"{prompt[0]}_output_text"] = output_text

        return list(self._history_dict.values())[-1]
