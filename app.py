import os
import uvicorn
import subprocess

from utils.couch_db_handler import CouchDBHandler
from utils.text_editor import Editor

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Body
from typing import List, Annotated


class Config(BaseModel):
    config_name: str
    config_dict: dict


class Text(BaseModel):
    input_text: str

class App:
    def __init__(self, ip: str = "127.0.0.1", port: int = 8000) -> None:
        """
        Builds the App Object to Server the Backend
        :param ip: ip to serve
        :param port: port to serve
        """
        self._ip = ip
        self._port = port
        self._app = FastAPI(
            title="AI-NER",
            description="AI-NER let's you anonymize input data by using a model from huggingface 🤗"
        )
        self._task_db = CouchDBHandler("config_tasks")
        self._model_db = CouchDBHandler("config_models")
 #       self._text_editor = Editor("config_task/default_task.yaml", self._model_db)
        
        self._configure_routes()

    @staticmethod
    def loop_over_config(configs: List[Config], model_db: CouchDBHandler, method: str):
        config_dict = {config.config_name: config.config_dict for config in configs}
        for key, value in config_dict.items():
            if "link" in value:
                if value["link"].endswith(".gguf"):
                    subprocess.call(f"wget {value['link']} -P models/", shell=True)
                else:
                    subprocess.call(f"git clone {value['link']} models/{value['model']}", shell=True)
                value.pop("link")

            getattr(model_db, method)(value, key)

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
                        "link": "https://huggingface.co/flair/ner-german-large",
                        "model": "flair/ner-german-large"
                    }
                },
            ]]
        )]
        ):
            """

            :param configs:
            :return:
            """
            self.loop_over_config(configs, self._model_db, "add_config")

        @self._app.post("/update_models")
        async def update_models(configs: Annotated[List[Config], Body(
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
                        "link": "https://huggingface.co/flair/ner-german-large",
                        "model": "flair/ner-german-large"
                    }
                },
            ]]
        )]
        ):
            """

            :param configs:
            :return:
            """
            self.loop_over_config(configs, self._model_db, "update_config")

        @self._app.post("/delete_models")
        async def delete_models(config_names: List[str]):
            """

            :param config_names:
            :return:
            """
            for config_name in config_names:
                config = self._model_db.get_config(config_name)
                subprocess.call(f"rm {config['model']}", shell=True)
                self._model_db.delete_config(config_name)

        @self._app.get("/get_all_models")
        async def get_all_models() -> dict:
            """

            :return:
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

        ):
            """
            Inserts and appends a configuration to the couchdb
            :param configs: configuration for an anonymization task
            :return: dict
            """
            self.loop_over_config(configs, self._task_db, "add_config")

        @self._app.post("/update_tasks")
        async def update_tasks(configs: Annotated[List[Config], Body(
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

        ):
            """
            Updates an existing config in the couchdb
            :param configs: configuration for an anonymization task
            :return: dict
            """
            self.loop_over_config(configs, self._task_db, "update_config")

        @self._app.post("/delete_tasks")
        async def delete_tasks(config_names: List[str]):
            """

            :param config_names:
            :return:
            """
            for config_name in config_names:
                self._task_db.delete_config(config_name)

        @self._app.get("/get_all_tasks")
        async def get_all_tasks() -> dict:
            """

            :return:
            """
            config = {}
            all_models = self._task_db.get_all_config_names()
            for model_name in all_models:
                config[model_name] = self._task_db.get_config(model_name)

            return config

        @self._app.post("/set_tasks")
        async def set_tasks(configuration: Annotated[List[str], Body(
            examples=[["email-address", "datum", "persons"]])
        ]):
            """
            Updates the text editor with configurations from the couchdb
            :param configuration:
            :return:
            """
            config_dict = dict()
            for config in configuration:
                config_dict[config] = self._task_db.get_config(config)

            self._text_editor = Editor(config_dict, self._model_db)

        @self._app.post("/anonymize")
        async def anonymize_text(text: Annotated[Text, Body(
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
        )]
        ) -> str:
            """
            Gets the input text that we want to anonymize
            :param text: input text to be anonymized
            :return: anonymized text
            """
            input_text = text.input_text
            if input_text is None or len(input_text) == 0:
                raise HTTPException(status_code=400, detail="no value provided")
            return self._text_editor.edit_text(input_text)

    def run(self) -> None:
        """
        Run the api
        :return: None
        """
        uvicorn.run(self._app, host=self._ip, port=self._port)


if __name__ == '__main__':
    os.environ["COUCHDB_USER"] = "admin"
    os.environ["COUCHDB_PASSWORD"] = "JensIsCool"
    os.environ["COUCHDB_IP"] = "127.0.0.1:5894"

    api = App(ip="127.0.0.1", port=8000)
    api.run()
