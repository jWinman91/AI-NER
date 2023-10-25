import importlib
import json
import yaml

from collections import OrderedDict
from llama_cpp import Llama
from multipledispatch import dispatch
from typing import List, Optional, Tuple, Dict


class EmptyRestrictor:
    def run(text: str) -> bool:
        return True


class Editor:
    OUTPUT = "Antwort:"
    
    def __init__(self, configfile: str):
        """
        Class to edit input text by using an LLM.
        :param configfile: path to config file that defines location of config files
        """
        config_dict = self.load_yml(configfile)

        self._prompts = self.load_yml(config_dict["prompt_config"])
        self._restrictor = EmptyRestrictor()
        
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
            self._model = Llama(model_path=self._params["model"], verbose=True, n_ctx=4096)
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

    def build_prompt(self, input_text: str, prompt_name: str, prompt_instruction: str) -> str:
        """
        Defines prompt statement based on prompts defined in the config file.
        :param input_text: input text
        :param prompt_name: name of prompt instruction
        :param prompt_instruction: instruction of the prompt
        :return: prompt statement including input text
        """
        context = prompt_instruction["Context"]

        if "Examples" in prompt_instruction.keys():
            prompt_str = ""
            for example in prompt_instruction["Examples"].values():
                prompt_str += f"""
                {context} {example["Input"]}
                {self.OUTPUT} {example["Output"]}
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
        restricted_response = self._restrictor.run(response_text)
        self._history_dict[f"{prompt_name}_restr"] = str(restricted_response[0])
        return restricted_response[1] if restricted_response[0] else "FAILED"

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
            prompt = self.build_prompt(list(self._history_dict.values())[-1], prompt_name, prompt_instruction)
            
            print("############################ PROMPT ##############################")
            print(prompt)
            print("##################################################################")
            
            self.build_restrictor(prompt_instruction, input_text)
            response = self.get_response(f"{prompt_name}", prompt)

        return list(self._history_dict.values())[-1]
        
    def build_restrictor(self, prompt_instruction: dict, input_text: str):
        if "Restrictor" in prompt_instruction.keys():
            module_name = prompt_instruction['Restrictor']["Name"].split('.')[0]
            restrictor_class = prompt_instruction["Restrictor"]["Name"].split(".")[1]
            params = prompt_instruction["Restrictor"]["Params"]
            
            module = importlib.import_module(f"restrictors.{module_name}")
            
            self._restrictor = getattr(module, restrictor_class)(input_text, **params)