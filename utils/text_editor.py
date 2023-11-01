import json
import re
import yaml

from collections import OrderedDict
from nltk import tokenize
from llama_cpp import Llama
from typing import Set, Dict


class Editor:
    OUTPUT = "Ausgabe:"
    
    def __init__(self, configfile: str):
        """
        Class to edit input text by using an LLM.
        :param configfile: path to config file that defines location of config files
        """
        config_dict = self.load_yml(configfile)

        self._prompts = self.load_yml(config_dict["prompt_config"])
        self._params = self.load_yml(config_dict["llm_config"])

        self._history_dict = OrderedDict()

        self._model = Llama(model_path=self._params["model"], n_threads=4, verbose=True, n_ctx=2048)
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

    def build_prompt(self, input_text: str, prompt_instruction: dict) -> str:
        """
        Defines prompt statement based on prompts defined in the config file.
        :param input_text: input text
        :param prompt_instruction: instruction of the prompt
        :return: prompt statement including input text
        """
        context = prompt_instruction["Context"]
        static_prompt = f"""Gib die {self.OUTPUT[:-1]} im validen json-Format {{"{self.OUTPUT[:-1]}": [{self.OUTPUT[:-1]}]}} aus:"""

        if "Examples" in prompt_instruction.keys():
            prompt_str = ""
            for example in prompt_instruction["Examples"].values():
                output = f"{example['Output']}".replace("'", "\"")
                prompt_str += f"""
                {context} {static_prompt} {example["Input"]}
                {self.OUTPUT} {{"{self.OUTPUT[:-1]}": {output}}}
                """
        else:
            prompt_str = ""

        prompt = f"""
          {prompt_str}
          {context} {static_prompt} {input_text}
          {self.OUTPUT}
        """

        return prompt

    def get_response(self, prompt_name: str, prompt_instruction: str) -> Set[str]:
        """
        Send the prompt with edit instructions and the input text to the LLM and return the edited text.
        :param prompt_name: name of the prompt instruction
        :param prompt_instruction: instruction of the prompt
        :return: edited text
        """
        self._params["prompt"] = prompt_instruction

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
            found_values = {self.OUTPUT[:-1]: ["FAILED"]}

        return set(found_values[self.OUTPUT[:-1]])

    def save_history(self, file_name: str):
        """
        Saves the history dictionary that contains all edits to the input text.
        :param file_name: Name of file where to save history
        :return:
        """
        with open(file_name, "w+", encoding="utf8") as f:
            f.write(json.dumps(self._history_dict, indent=1, ensure_ascii=False))
        
        self._history_dict = OrderedDict()

    def edit_text(self, input_text: str) -> str:
        """
        Edits input text based on prompt instruction given in config file.
        :param input_text: Input text
        :return: edited input text
        """
        self._history_dict[f"input_text"] = input_text
        for prompt_name, prompt_instruction in self._prompts.items():
            unique_patterns = set()
            input_sentences = tokenize.sent_tokenize(list(self._history_dict.values())[-1])
            print(input_sentences)
            for input_sentence in list(filter(None, input_sentences)):
                prompt = self.build_prompt(input_sentence, prompt_instruction)
            
                print("############################ PROMPT ##############################")
                print(prompt)
                print("##################################################################")
            
                unique_patterns = unique_patterns.union(self.get_response(f"{prompt_name}", prompt))

            self._history_dict[f"{prompt_name}_patterns"] = list(unique_patterns)

            output_text = input_text
            unique_patterns.discard("FAILED")
            for pattern in unique_patterns:
                output_text = output_text.replace(pattern, prompt_instruction["replace_token"])

            self._history_dict[f"{prompt_name}_output_text"] = output_text

        return list(self._history_dict.values())[-1]