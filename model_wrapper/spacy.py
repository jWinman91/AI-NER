from model_wrapper.abstract_model_wrapper import AbstractNERModel
from types import Tuple, Set
from spacy_llm.util import assemble

class SpacyWrapper(AbstractNERModel):
    def __init__(self, config_path: str):
        """

        :param params: A dictionary containing the parameters for initializing the spacy model.
                       See https://spacy.io/usage/large-language-models for more infos on what the parameters are.
        """
        self._model = assemble(config_path)

    def find_name_entities(self, input_sentence: str, prompt: Tuple[str, dict], history_dict: dict) -> Set[str]:
        """
        Extracts and returns unique named entities from an input sentence based on the provided prompt.

        This method processes the input sentence using the internal model, historizes the response using the
        `historize_response` method, and filters the named entities based on the specified entity type in the prompt.

        :param input_sentence: The input sentence to analyze for named entities.
        :param prompt: A tuple containing a string prompt and a dictionary of prompt details.
        :param history_dict: A dictionary containing the history of responses for different prompts.
        :return: A set of unique named entities extracted from the input sentence.
        """
        doc = self._model(input_sentence)

        self.historize_response(prompt, doc, history_dict)

        found_entities = set([ent.text for ent in doc.ents
                              if ent.label_ == prompt[1]["entity_type"]])

        return set(filter(lambda x: len(x) > 1, found_entities))


