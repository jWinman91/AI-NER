from abc import ABC, abstractmethod
from nltk import tokenize
from typing import Set, Tuple, List

class AbstractNERModel(ABC):
    @abstractmethod
    def find_name_entities(self, input_sentence: str, prompt: Tuple[str, dict], history_dict: dict) -> Set[str]:
        """
        Placeholder function for searching for the name entities
        :return:
        """
        return set()

    def run(self, input_text: str, prompt: Tuple[str, dict], history_dict: dict) -> Set[str]:
        """
        Extract and return unique name entities from the input text based on the provided prompt.

        This method tokenizes the input text into sentences and calls the find_name_entities function
        to identify name entities related to the given prompt. The unique name entities are then collected
        into a set and returned.

        :param input_text: The input text to analyze for name entities.
        :param prompt: A tuple containing a string prompt and a dictionary of prompt details.
        :param history_dict: A dictionary containing the history of responses for different prompts.
        :return: A set of unique name entities extracted from the input text.
        """
        unique_patterns = set()
        input_sentences = tokenize.sent_tokenize(input_text)
        for input_sentence in list(filter(None, input_sentences)):
            name_entities = self.find_name_entities(input_sentence, prompt, history_dict)
            unique_patterns = unique_patterns.union(name_entities)

        return unique_patterns

    @staticmethod
    def historize_response(prompt: Tuple[str, dict], response: List[dict], history_dict: dict):
        """
        Update the history dictionary with the response to a given prompt.

        This function appends the response to the history dictionary under the key corresponding to the prompt.

        :param prompt: A tuple containing a string prompt and a dictionary of prompt details.
        :param response: A list of dictionaries representing the response to the prompt.
        :param history_dict: A dictionary to store the history of responses for different prompts.
        :return: None
        """
        if prompt[0] not in history_dict:
            history_dict[prompt[0]] = response
        else:
            history_dict[prompt[0]].extend(response)