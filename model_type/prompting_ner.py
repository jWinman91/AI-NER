import json
from llama_cpp import Llama
from typing import Set, List, Tuple


class PromptingModel:
    OUTPUT = "Ausgabe:"

    def __init__(self, params):
        """

        :param prompts:
        :param params:
        """
        self._model = Llama(model_path=params.get("model", "models/em_german_leo_mistral.Q5_0.gguf"),
                            n_threads=params.get("n_threads", 2),
                            verbose=params.get("verbose", False),
                            n_ctx=params.get("n_ctx", 1024)
                            )

        for param in ["model", "n_threads", "verbose", "n_ctx"]:
            if param in params.keys():
                del params[param]

        self._params = params

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

    def get_response(self, prompt_dict: dict) -> Tuple[Set[str], str]:
        """
        Send the prompt with edit instructions and the input text to the LLM and return the edited text.
        :param prompt_name: name of the prompt instruction
        :param prompt_instruction: instruction of the prompt
        :param history_dict: dictionary to log the history
        :return: edited text and response text
        """
        self._params["prompt"] = prompt_dict

        response = self._model(**self._params)

        response_text = response["choices"][0]["text"].split(self.OUTPUT)[-1].encode("utf-8").decode()
        try:
            found_values = json.loads(response_text, strict=False)
        except Exception as e:
            print(f"FAILED because of {e}")
            found_values = {self.OUTPUT[:-1]: ["FAILED"]}

        return set(found_values[self.OUTPUT[:-1]]), response_text

    def find_name_entity(self, input_sentence: str, prompt_key: str, prompt_dict: dict, history_dict: dict) -> List[str]:
        prompt = self.build_prompt(input_sentence, prompt_dict)

        found_entities, response_text = self.get_response(prompt_dict)
        history_dict[prompt_key] = response_text

        return list(found_entities)



