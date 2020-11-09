import os
import logging

from pymongo import MongoClient


class MongoDBHandler:
    def __init__(self, db_path: str = None, db_name: str = None):
        self.db_name = db_name
        if db_path is None:
            logging.warning('Path to remote MongoDB was not specified. Using local MongoDB')
            self.client = MongoClient(os.environ.get('MONGO_DB_ADDR'), int(os.environ.get('MONGO_DB_PORT')))
        else:
            self.client = MongoClient(db_path)

    def _get_database_or_create_new(self, database_name: str):
        if database_name not in self.client.list_database_names():
            logging.warning(
                f'Database with name {database_name} was not found. New database {database_name} will be created!'
            )
        return self.client[database_name]

    def _get_collection_or_create_new(self, collection_name: str):
        db = self._get_database_or_create_new(self.db_name)
        if collection_name not in db.list_collection_names():
            logging.warning(
                f'Collection with name "{collection_name}" was not found. '
                f'Collection "{collection_name}" will be created'
            )
        return db[collection_name]

    def insert_record(self, payload: dict) -> bool:
        """
        Inserting record into 'currencies' collection in MongoDB

        :param payload: payload to insert into DB
        :return: boolean status of insertion
        """
        currencies_collection = self._get_collection_or_create_new('currencies')
        result = currencies_collection.insert_one(payload)
        if result.inserted_id is not None:
            logging.info(f'Record was successfully created! Record ID: {result.inserted_id}')
            return True
        else:
            logging.error(f'Record was not created...')
            return False
