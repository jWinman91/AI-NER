import importlib
import json
import yaml

from collections import OrderedDict
from llama_cpp import Llama
from multipledispatch import dispatch
from typing import List, Optional, Tuple, Dict


class Editor:
    OUTPUT = "Antwort:"
    
    def __init__(self, configfile: str):
        """
        Class to edit input text by using an LLM.
        :param configfile: path to config file that defines location of config files
        """
        config_dict = self.load_yml(configfile)

        self._prompts = self.load_yml(config_dict["prompt_config"])

        params = self.load_yml(config_dict["llm_config"])
        if params is None or len(params) == 0:
            self._params = {
                "model": "ChatGPT",
                "engine": "generation-davinci-003",
                "temperature": 0.,
                "max_tokens": 100,
                "top_p": 0.5,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "best_of": 1,
                "stop": None
            }
        else:
            self._params = params

        self._history_dict = OrderedDict()

        if "ChatGPT" in self._params["model"]:
            import openai
            self._params["engine"] = self._params["model"]["engine"]
        else:
            self._model = Llama(model_path=self._params["model"], verbose=True, n_ctx=2048)
        del self._params["model"]

    @staticmethod
    def load_yml(configfile: str) -> Dict:
        """
        Imports the yml Configuration file
        :param configfile: path to the config file
        :return: a Dictionary
        """
        with open(configfile, "r") as b:
            try:
                data = yaml.safe_load(b)
            except yaml.YAMLError as err:
                print(err)
        return data

    def static_prompt(self) -> str:
        """
        Adds a static statement to the prompt.
        :return:
        """
        return f"""Gib die Antwort im validen json-Format {{"{self.OUTPUT[:-1]}": [{self.OUTPUT[:-1]}]}} aus:"""

    def build_prompt(self, input_text: str, prompt_instruction: dict) -> str:
        """
        Defines prompt statement based on prompts defined in the config file.
        :param input_text: input text
        :param prompt_instruction: instruction of the prompt
        :return: prompt statement including input text
        """
        context = prompt_instruction["Context"]

        if "Examples" in prompt_instruction.keys():
            prompt_str = ""
            for example in prompt_instruction["Examples"].values():
                output = f"{example['Output']}".replace("'", "\"")
                prompt_str += f"""
                {context} {example["Input"]}
                {self.OUTPUT} {{"{self.OUTPUT[:-1]}": {output}}}
                """
        else:
            prompt_str = ""

        prompt = f"""
          {prompt_str}
          {context} {input_text}
          {self.OUTPUT}
        """

        return prompt

    def get_response(self, prompt_name: str, prompt_instruction: str) -> str:
        """
        Send the prompt with edit instructions and the input text to the LLM and return the edited text.
        :param prompt_name: name of the prompt instruction
        :param prompt_instruction: instruction of the prompt
        :return: edited text
        """
        self._params["prompt"] = prompt_instruction

        if "engine" in self._params:
            response = openai.Completion.create(
                **self._params
            )
        else:
            response = self._model(**self._params)
            
            print("####################### OUTPUT ###############################")
            print(response["choices"][0]["text"])
            print("##############################################################")
        
        response_text = response["choices"][0]["text"].split(self.OUTPUT)[-1].encode("utf-8").decode()
        self._history_dict[prompt_name] = response_text
        try:
            found_values = json.loads(response_text, strict=False)
        except Exception as e:
            print(f"FAILED because of {e}")
            found_values = {self.OUTPUT[:-1]: "FAILED"}

        return found_values[self.OUTPUT[:-1]]

    def save_history(self, file_name: str):
        """
        Saves the history dictionary that contains all edits to the input text.
        :param file_name: Name of file where to save history
        :return:
        """
        with open(file_name, "w+", encoding="utf8") as f:
            f.write(json.dumps(self._history_dict, indent=1, ensure_ascii=False))
        
        self._history_dict = OrderedDict()

    @staticmethod
    def find_and_replace(self, input_text: str, chars: str):
        return input_text.replace(chars)

    def edit_text(self, input_text: str) -> str:
        """
        Edits input text based on prompt instruction given in config file.
        :param input_text: Input text
        :return: edited input text
        """
        self._history_dict[f"input_text"] = input_text
        for prompt_name, prompt_instruction in self._prompts.items():
            prompt = self.build_prompt(list(self._history_dict.values())[-1], prompt_instruction)
            
            print("############################ PROMPT ##############################")
            print(prompt)
            print("##################################################################")
            
            found_values = self.get_response(f"{prompt_name}", prompt)

            self._history_dict[f"{prompt_name}_found_values"] = found_values

            output_text = input_text
            for found_value in found_values:
                output_text = output_text.replace(found_value, prompt_instruction["replace_token"])

            self._history_dict[f"{prompt_name}_output_text"] = output_text

        return list(self._history_dict.values())[-1]