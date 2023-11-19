import couchdb
import os
import json

from typing import List

class CouchDBHandler:
    def __init__(self, table_name: str) -> None:
        """
        Builds the CouchDBHandler Object
        :param table_name: Name of the Table
        """
        try:
            user = os.getenv("COUCHDB_USER")
            password = os.getenv("COUCHDB_PASSWORD")
            ip = os.getenv("COUCHDB_IP")
            couch = couchdb.Server(f"http://{user}:{password}@{ip}")
            couch.version()
        except:
            print("Connection error.")
            couch = None

        if table_name in couch:
            self._db_table = couch[table_name]
        else:
            self._db_table = couch.create(table_name)

    def add_config(self, config_dict: dict, config_name: str) -> None:
        """
        Add a config to the DB Table
        :param config_dict: dictionary with the config
        :param config_name:a name for the config
        :return: None
        """
        config_dict["_id"] = config_name
        if config_name in self._db_table:
            raise Exception(f"{config_name} already exists!")
        else:
            self._db_table.save(config_dict)

    def update_config(self, config_dict: dict, config_name: str) -> None:
        """
        Update a config
        :param config_dict: a dictionary with the config
        :param config_name: a config Name
        :return: None
        """
        self.delete_config(config_name)
        config_dict["_id"] = config_name
        self._db_table.save(config_dict)

    def delete_config(self, config_name) -> None:
        """
        Delet a config from the DB
        :param config_name: a config name
        :return: None
        """
        if config_name not in self._db_table:
            raise Exception(f"{config_name} does not exist!")
        config_dict = self.get_config(config_name)
        self._db_table.delete(config_dict)

    def get_config(self, config_name) -> dict:
        """
        Returns a given config
        :param config_name: a config name
        :return: dictionary
        """
        if config_name not in self._db_table:
            raise Exception(f"{config_name} does not exist!")
        return self._db_table[config_name]

    def get_all_config_names(self) -> List[str]:
        """
        Returns all names of configs stored in db
        :return: list of all names
        """
        return [id for id in self._db_table]

    def backup_config(self) -> None:
        """
        Backups the configs saved in the DB
        :return: None
        """
        with open("config_backup.txt", "w") as f:
            for id in self._db_table:
                config = self._db_table[id]
                f.write(json.dumps(config, indent=4))