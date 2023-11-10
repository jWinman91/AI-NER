import re

from typing import Set, Tuple

class Regex:
    def __init__(self, params=None):
        """

        """
        ...

    @staticmethod
    def run(input_sentence: str, prompt: Tuple[str, dict], history_dict: dict) -> Set[str]:
        """

        :param input_sentence: The input sentence to find entities in.
        :param prompt: The prompt key and body associated with the prompt in the history dictionary.
        :param history_dict: A dictionary to store the history of found entities.
        :return: A list of found regular expressions in the input sentence.
        """
        return set(re.findall(prompt[1]["pattern"], input_sentence))
