from fastapi import FastAPI, HTTPException, File, UploadFile
import uvicorn


class App:
    def __init__(self, ip: str = "127.0.0.1", port: int = 8000) -> None:
        """
        Builds the App Object to Server the Backend
        :param ip: ip to serve
        :param port: port to serve
        """
        self._ip = ip
        self._port = port
        self._app = FastAPI()
        
        
        self._configure_routes()


    def _configure_routes(self) -> None:
        """
        Creates the route(s)
        :return: None
        """

        @self._app.post("/anonymize")
        async def anonymize(data: dict = {}) -> str:
            """
            Gets the input text that we want to anonymize
            :param data: a dict with input text and entities to anonymize
            :return: anonymized text
            """
            raise HTTPException(status_code=400, detail="no value provided")


        @self._app.post("/insert_config")
        async def insert_config(config: dict) -> dict:
            """
            Inserts and appends a configuration to the couchdb
            :param config: configuration for an anonymization task
            :return: dict
            """
            pass

        @self._app.post("/update_config")
        async def updat_config(config: dict) -> dict:
            """
            Updates an existing config in the couchdb
            :param config: configuration for an anonymization task
            :return: dict
            """
            pass

    def run(self) -> None:
        """
        Run the api
        :return: None
        """
        uvicorn.run(self._app, host=self._ip, port=self._port)


if __name__ == '__main__':
    api = App(ip="127.0.0.1", port=8000)
    api.run()
