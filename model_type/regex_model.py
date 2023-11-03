import re

from typing import List

class Regex:
    def __init__(self, params=None):
        """

        """
        ...

    def find_name_entity(self, input_sentence: str, prompt_key: str, prompt_dict: dict, history_dict: dict) -> List[str]:
        """

        :param input_sentence:
        :param prompt_key:
        :param prompt_dict:
        :param history_dict:
        :return:
        """
        return list(set(re.findall(prompt_dict["pattern"], input_sentence)))
