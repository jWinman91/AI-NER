from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from flair.data import Sentence
from flair.models import SequenceTagger
from typing import List


class RobertaModel:
    def __init__(self, params):
        """
        Class using a pretrained Name-entity recognition model.

        :param params: A dictionary containing the parameters for initializing the NER model.
                       It should include 'tokenizer' and 'model' keys specifying the pre-trained tokenizer
                       and model for token classification.
        """
        tokenizer = AutoTokenizer.from_pretrained(params["tokenizer"])
        model = AutoModelForTokenClassification.from_pretrained(params["model"])
        self._classifier = pipeline("ner", model=model, tokenizer=tokenizer)

    @staticmethod
    def merge_entities(entities):
        """
        Merges consecutive entities with overlapping boundaries.

        :param entities: A list of dictionaries representing entities with 'start', 'end', and 'word' keys.
        :return: A list of merged entities.
        """
        result = [entities[0]]
        for i in range(1, len(entities)):
            if (entities[i - 1]["end"] == entities[i]["start"] or\
                entities[i - 1]["end"] == entities[i]["start"] - 1) and\
                    entities[i - 1]["entity"] == entities[i]["entity"]:
                result[-1]["word"] += entities[i]["word"]
                result[-1]["end"] = entities[i]["end"]
            else:
                result.append(entities[i])
        return result

    def find_name_entity(self, input_sentence: str, prompt_key: str, prompt_dict: dict, history_dict: dict) -> List[str]:
        """
        Finds name entities in the input sentence based on the NER model and updates the history dictionary.

        :param input_sentence: The input sentence to find entities in.
        :param prompt_key: The key associated with the prompt in the history dictionary.
        :param prompt_dict: A dictionary containing prompt information, including 'entity_type'.
        :param history_dict: A dictionary to store the history of found entities.
        :return: A list of found entities in the input sentence.
        """
        response = self._classifier(input_sentence)
        response = self.merge_entities(response)

        if prompt_key not in history_dict:
            history_dict[prompt_key] = response
        else:
            history_dict[prompt_key].extend(response)

        found_entities = set([entity["word"].replace(u"\u2581", " ").strip() \
                              for entity in response
                              if entity["entity"] == prompt_dict["entity_type"]])

        return list(found_entities)


class FlairModel:
    def __init__(self, params):
        self._tagger = SequenceTagger.load(params["model"])

    def find_name_entity(self, input_sentence: str, prompt_key: str, prompt_dict: dict, history_dict: dict) -> List[
        str]:
        """
        Finds name entities in the input sentence based on the NER model and updates the history dictionary.

        :param input_sentence: The input sentence to find entities in.
        :param prompt_key: The key associated with the prompt in the history dictionary.
        :param prompt_dict: A dictionary containing prompt information, including 'entity_type'.
        :param history_dict: A dictionary to store the history of found entities.
        :return: A list of found entities in the input sentence.
        """
        sentence = Sentence(input_sentence)
        self._tagger.predict(sentence)

        spans = list(map(lambda x: x.to_dict(), sentence.get_spans("ner")))

        if prompt_key not in history_dict:
            history_dict[prompt_key] = spans
        else:
            history_dict[prompt_key].extend(spans)

        found_entities = set([span["text"] for span in spans
                              if span["labels"][0]["value"] == prompt_dict["entity_type"]])

        return list(filter(lambda x: len(x) > 1, found_entities))





