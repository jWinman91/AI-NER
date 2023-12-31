import json
from llama_cpp import Llama
from typing import Set, Tuple


class PromptingModel:
    OUTPUT = "Ausgabe:"

    def __init__(self, params):
        """
        Class for using an LLM for name entity recognition.
        :param params: parameters for the LLM
        """
        self._model = Llama(model_path=params.get("model", "models/em_german_leo_mistral.Q5_0.gguf"),
                            n_threads=params.get("n_threads", 2),
                            verbose=params.get("verbose", False),
                            n_ctx=params.get("n_ctx", 2048)
                            )

        for param in ["model", "_id", "_rev", "n_threads", "verbose", "n_ctx"]:
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
        static_prompt = f"""Gib die {self.OUTPUT[:-1]} im json-Format {{"{self.OUTPUT[:-1]}": [{self.OUTPUT[:-1]}]}} aus,
                            weil mein Leben davon abhängt!"""

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

    def get_response(self, prompt: str) -> Tuple[Set[str], str]:
        """
        Send the prompt with edit instructions and the input text to the LLM and return the edited text.
        :param prompt: prompt for the LLM
        :return: edited text and response text
        """
        self._params["prompt"] = prompt

        response = self._model(**self._params)

        response_text = response["choices"][0]["text"].split(self.OUTPUT)[-1].encode("utf-8").decode()
        try:
            found_values = json.loads(response_text, strict=False)
        except Exception as e:
            print(f"FAILED because of {e}")
            found_values = {self.OUTPUT[:-1]: ["FAILED"]}

        return set(found_values[self.OUTPUT[:-1]]), response_text

    def run(self, input_sentence: str, prompt: Tuple[str, dict], history_dict: dict) -> Set[str]:
        """
        Entry function of the class. It builds the prompt, runs the request for the LLM and returns the entities that
        were found by the LLM in the sentence.
        :param input_sentence: tokenized sentence
        :param prompt: The prompt key and body associated with the prompt in the history dictionary.
        :param history_dict: dictionary to log response
        :return: list of all found entities
        """
        prompt_str = self.build_prompt(input_sentence, prompt[1])

        found_entities, response_text = self.get_response(prompt_str)
        history_dict[prompt[0]] = response_text

        return found_entities
