import nltk

from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from typing import List


class NERModel:
    def __init__(self, params):
        tokenizer = AutoTokenizer.from_pretrained(params["tokenizer"])
        model = AutoModelForTokenClassification.from_pretrained(params["model"])
        self._classifier = pipeline("ner", model=model, tokenizer=tokenizer)

    @staticmethod
    def merge_entities(entities):
        result = [entities[0]]
        for i in range(1, len(entities)):
            if entities[i - 1]["end"] == entities[i]["start"]:
                result[-1]["word"] += entities[i]["word"]
                result[-1]["end"] = entities[i]["end"]
            else:
                result.append(entities[i])
        return result

    def find_name_entity(self, input_sentence: str, prompt_key: str, prompt_dict: dict, history_dict: dict) -> List[str]:
        response = self._classifier(input_sentence)
        print(response)
        response = self.merge_entities(response)
        print(response)

        if prompt_key not in history_dict:
            history_dict[prompt_key] = response
        else:
            history_dict[prompt_key].extend(response)

        found_entities = set()
        for token in nltk.word_tokenize(input_sentence):
            for entity in response:
                if entity["entity"] == prompt_dict["entity_type"] and entity["word"].replace(u"\u2581", "") in token:
                    found_entities.add(token)

        return list(found_entities)
