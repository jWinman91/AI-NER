import os
import uvicorn
import subprocess

from utils.couch_db_handler import CouchDBHandler
from utils.text_editor import Editor

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Body
from typing import List, Annotated


DESCRIPTION = """
AI-NER let's you anonymize your text documents by using a model of your choice from huggingface 🤗.

## Configuration of AI-NER
Before you can anonymize your text documents, you have to add (or update) a configuration for a model and tasks.
* `/insert_model`: Adds or updates a configuration for the models. It automatically downloads new models from huggingface.
* `/insert_tasks`: Adds or updates a configuration for a tasks. You have to choose here which model you want to use for each task.

## Usage of AI-NER
After you have configured models and tasks, you can anonymize your text documents in two steps:
1. Run the `/set_tasks` route to let the text editor know which configs you want to choose.
2. Send your text document via `/anonymize` to the text editor.
"""

class Config(BaseModel):
    config_name: str
    config_dict: dict


class Text(BaseModel):
    input_text: str


class Texts(BaseModel):
    input_text: List[str]


class App:
    def __init__(self, ip: str = "127.0.0.1", port: int = 8000) -> None:
        """
        Builds the App Object for the Server Backend

        :param ip: ip to serve
        :param port: port to serve
        """
        self._ip = ip
        self._port = port
        self._app = FastAPI(
            title="AI-NER: Text editing with Language Models from Huggingface 🤗",
            description=DESCRIPTION
        )
        self._task_db = CouchDBHandler("config_tasks")
        self._model_db = CouchDBHandler("config_models")
        self._text_editor = None #Editor("config_task/default_task.yaml", self._model_db)
        
        self._configure_routes()

    @staticmethod
    def modify_config(configs: List[Config], model_db: CouchDBHandler):
        """
        Helper function to modify configs in the couchDB for either the tasks or the models.
        configs are either updated or added (if they dont exist yet).

        :param configs: List of configurations
        :param model_db: the handler for the DB
        :return: None
        """
        config_dict = {config.config_name: config.config_dict for config in configs}
        all_config_names = model_db.get_all_config_names()
        for key, value in config_dict.items():
            if "link" in value and not os.path.exists(value["model"]):
                model_dir = "/".join(value["model"].split("/")[:-1])
                subprocess.call(f"mkdir -p {model_dir}", shell=True)
                subprocess.call(f"wget {value['link']} -P {model_dir}", shell=True)
                value.pop("link")
            elif "link" in value:
                value.pop("link")

            method = "add_config" if key not in all_config_names else "update_config"
            getattr(model_db, method)(value, key)

    def set_tasks(self, configuration: List[str]) -> bool:
            """
            Updates the text editor with configured tasks (and models) from the couchdb.

            :param configuration: List of configured tasks to be run by the editor \n
            :return: True if successfully set all tasks
            """
            config_dict = dict()
            for config in configuration:
                config_dict[config] = self._task_db.get_config(config)

            self._text_editor = Editor(config_dict, self._model_db)

            return True

    def _configure_routes(self) -> None:
        """
        Creates the route(s)

        :return: None
        """

        @self._app.post("/insert_models")
        async def insert_models(configs: Annotated[List[Config], Body(
            examples=[[
                {
                    "config_name": "Sauerkraut",
                    "config_dict": {
                        "link": "https://huggingface.co/TheBloke/SauerkrautLM-7B-v1-mistral-GGUF/resolve/main/sauerkrautlm-7b-v1-mistral.Q4_0.gguf",
                        "model": "models/sauerkrautlm-7b-v1-mistral.Q4_0.gguf",
                        "max_tokens": 2000,
                        "temperature": 0,
                        "top_p": 0
                    }
                },
                {
                    "config_name": "flair-german",
                    "config_dict": {
                        "link": "https://huggingface.co/flair/ner-german-large/resolve/main/pytorch_model.bin",
                        "model": "models/flair/ner-german-large/pytorch_model.bin"
                    }
                },
            ]]
        )]
        ) -> bool:
            """
            Inserts model configs into the couchdb.
            If a configuration under the name already exists, the configuration will be overwritten.

            :param configs: Object consisting of the config name and config details \n
            :return: True if everything went successful
            """
            self.modify_config(configs, self._model_db)
            return True

        @self._app.post("/delete_models")
        async def delete_models(config_names: List[str]) -> bool:
            """
            Deletes a configuration of a model from the couchdb.
            If the config doesnt exist, an error will be raised.

            :param config_names: List of names of model configs that will be deleted \n
            :return: True if successfully deleted
            """
            for config_name in config_names:
                config = self._model_db.get_config(config_name)
                subprocess.call(f"rm {config['model']}", shell=True)
                self._model_db.delete_config(config_name)

            return True

        @self._app.get("/get_all_models")
        async def get_all_models() -> dict:
            """
            Returns all configured models that are currently stored in the couchdb.

            :return: Dictionary of all model configs
            """
            config = {}
            all_models = self._model_db.get_all_config_names()
            for model_name in all_models:
                config[model_name] = self._model_db.get_config(model_name)

            return config

        @self._app.post("/insert_tasks")
        async def insert_tasks(configs: Annotated[List[Config], Body(
            examples=[[
                {
                    "config_name": "email-address",
                    "config_dict": {
                        "model": {
                            "model_wrapper": "regex_model/Regex"
                        },
                        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                        "replace_token": "EMAIL@EMAIL.DE"
                    }
                },
                {
                    "config_name": "datum",
                    "config_dict": {
                        "model": {
                            "model_wrapper": "regex_model/Regex"
                        },
                    "pattern": r"(?:[0-2][0-9]|[1-9]|30|31)[.\\/,\\s](?:0?[1-9]|10|11|12)(?:(?:[.\\/,\\s](?:[1-2][0-9])?(?:[0-9]{2}))|[.\\/,]|\\b)",
                    "replace_token": ">DATUM<",
                    }
                },
                {
                    "config_name": "persons",
                    "config_dict": {
                        "model": {
                            "model_wrapper": "ner_model/FlairModel",
                            "model_config": "flair-german"
                        },
                        "replace_token": ">NAME<",
                        "entity_type": "PER"
                    }
                }
            ]])]

        ) -> bool:
            """
            Inserts and appends a configuration of a task to the couchdb.
            A task defines what to anonymize (e.g. persons, customer IDs, ...).

            :param configs: Configuration for an anonymization task \n
            :return: True if successfully inserted
            """
            self.modify_config(configs, self._task_db)
            return True

        @self._app.post("/delete_tasks")
        async def delete_tasks(config_names: List[str]) -> bool:
            """
            Deletes a configured task inside the couchDB.

            :param config_names: Name of the config task to be deleted \n
            :return: True if successfully deleted
            """
            for config_name in config_names:
                self._task_db.delete_config(config_name)

            return True

        @self._app.get("/get_all_tasks")
        async def get_all_tasks() -> dict:
            """
            Returns all configured tasks that are currently stored in the couchdb.

            :return: Dictionary of all config tasks
            """
            config = {}
            all_models = self._task_db.get_all_config_names()
            for model_name in all_models:
                config[model_name] = self._task_db.get_config(model_name)

            return config

        @self._app.post("/anonymize_string")
        async def anonymize_string(text: Annotated[Text, Body(
            examples=[{
                "input_text": """
                    Sehr geehrte Damen und Herren,

                    ich würde gerne Ihr neuestes Produkt für 9.99€ kaufen.

                    Wie bereits mit Herrn Peterson am Telefon am 10.11.2023 ausgemacht,
                    überschicke ich Ihnen hiermit meine gesamten Daten:
                    Name: Christian Mayer
                    Adresse: Guststraße 3, 12345 Frankfurt am Main
                    IBAN: DE70500105171174417511
                    Kunden-Nr.: 118255779

                    Sie können mich weiterhin unter meiner Handy-Nr 0172 229 0 229 erreichen.

                    Mit freundlichen Grüße,
                    Christian Mayer
                    christian.mayer@gmx.de
            """
            }]
        )],
                                   configuration: Annotated[List[str], Body(
                                       examples=[[
                                           "email-address",
                                           "datum",
                                           "persons"
                                       ]]
                                   )]
        ) -> str:
            """
            Anonymizes the input text by running the text editor over the configured and set tasks and models.

            :param configuration:
            :param text: Input text to be anonymized \n
            :return: Anonymized text
            """
            input_text = text.input_text
            tasks_set = self.set_tasks(configuration)
            if input_text is None or len(input_text) == 0:
                raise HTTPException(status_code=400, detail="no value provided")
            if not tasks_set:
                raise HTTPException(status_code=400, detail="Tasks configurations were not set correctly")
            output_text = self._text_editor.edit_text(input_text)
            self._text_editor.save_history("data/history/last_anonymize_str.json")
            return output_text

        @self._app.post("/anonymize_bulk")
        async def anonymize_bulk(texts: Annotated[Texts, Body(
            examples=[{
                "input_text": ["""Paul Dirac/Sykes Herne/Team Blue % Kontakt: Kundin % Kundin meldet dass der Techniker informiert ist""",
                               """-Pierre Alphonso Laurent/CNX Bochum/Sales ID: 11211  Kontakt: Kundin % Anliegen: Kundin ist umgezogen""",
                               """Arwah Abadhi/Sykes Bochum/Team Lila % Kontakt: Kundin % Kundin meldet dass der Techniker informiert ist"""]
            }]
        )],
                                 configuration: Annotated[List[str], Body(
                                     examples=[[
                                         "email-address",
                                         "datum",
                                         "persons",
                                         "locations",
                                         "organisations"
                                     ]]
                                 )]
        ) -> List[str]:
            input_texts = texts.input_text
            tasks_set = self.set_tasks(configuration)
            if input_texts is None or len(input_texts) == 0:
                raise HTTPException(status_code=400, detail="no value provided")
            if not tasks_set:
                raise HTTPException(status_code=400, detail="Tasks configurations were not set correctly")

            output_texts = []
            for i, input_text in enumerate(input_texts):
                output_texts.append(self._text_editor.edit_text(input_text))
                self._text_editor.save_history(f"data/history/anonymize_bulk_{i}.json")

            return output_texts

    def run(self) -> None:
        """
        Run the api
        :return: None
        """
        uvicorn.run(self._app, host=self._ip, port=self._port)


if __name__ == '__main__':
    os.environ["COUCHDB_USER"] = "admin"
    os.environ["COUCHDB_PASSWORD"] = "JensIsCool"
    os.environ["COUCHDB_IP"] = "127.0.0.1:5984"
    
    subprocess.call("mkdir -p data/history", shell=True)

    api = App(ip="0.0.0.0", port=8000)
    api.run()
