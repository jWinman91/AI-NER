from abc import ABC, abstractmethod
from nltk import tokenize
from typing import Set, Tuple

class AbstractNERModel(ABC):
    @abstractmethod
    def find_name_entities(self, input_sentence: str, prompt: Tuple[str, dict], history_dict: dict) -> Set[str]:
        """
        Placeholder function for searching for the name entities
        :return:
        """
        return set()

    def run(self, input_text: str, prompt: Tuple[str, dict], history_dict: dict) -> Set[str]:
        unique_patterns = set()
        input_sentences = tokenize.sent_tokenize(input_text)
        for input_sentence in list(filter(None, input_sentences)):
            name_entities = self.find_name_entities(input_sentence, prompt, history_dict)
            unique_patterns = unique_patterns.union(name_entities)

        return unique_patterns