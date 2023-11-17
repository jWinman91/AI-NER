import couchdb
import os
import json


class CouchDBHandler:
    def __init__(self, table_name: str = "config_tasks") -> None:
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

        if table_name in couch:
            self._db_table = couch[table_name]
        else:
            self._db_table = couch.create(table_name)

    def add_task(self, task_dict: dict, task_name: str) -> None:
        """
        Add a task to the DB Table
        :param task_dict: dictionary with the task
        :param task_name:a name for the task
        :return: None
        """
        taks_name = task_name.lower()
        task_dict["_id"] = task_name
        if task_name in self._db_table:
            raise Exception(f"{task_name} already exists!")
        else:
            self._db_table.save(task_dict)

    def update_task(self, task_dict: dict, task_name: str) -> None:
        """
        Update a task
        :param task_dict: a dictionary with the task
        :param task_name: a task Name
        :return: None
        """
        taks_name = task_name.lower()
        task_dict["_id"] = task_name
        if task_name not in self._db_table:
            raise Exception(f"{task_name} does not exist!")
        else:
            self._db_table.save(task_dict)

    def delete_task(self, task_name) -> None:
        """
        Delet a task from the DB
        :param task_name: a task name
        :return: None
        """
        taks_name = task_name.lower()
        if task_name not in self._db_table:
            raise Exception(f"{task_name} does not exist!")
        self._db_table.delete(task_name)

    def get_task(self, task_name) -> dict:
        """
        Returns a given task
        :param task_name: a task name
        :return: dictionary
        """
        taks_name = task_name.lower()
        if task_name not in self._db_table:
            raise Exception(f"{task_name} does not exist!")
        return self._db_table[task_name]

    def backup_tasks(self) -> None:
        """
        Backups the tasks saved in the DB
        :return: None
        """
        with open("task_backup.txt", "w") as f:
            for id in self._db_table:
                task = self._db_table[id]
                f.write(json.dumps(task, indent=4))