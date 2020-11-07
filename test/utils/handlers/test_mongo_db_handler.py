import unittest
from unittest.mock import Mock, MagicMock, patch, call

from app.utils.handlers.mongo_db_handler import MongoDBHandler


class TestMongoDBHandler(unittest.TestCase):
    @patch('app.utils.handlers.mongo_db_handler.MongoClient')
    def test_init_no_path(self, patched_mongo_client):
        db_path = None
        MongoDBHandler(db_path=db_path, db_name='test')

        calls = [call('mongodb://localhost:27017')]
        patched_mongo_client.assert_has_calls(calls)

    @patch('app.utils.handlers.mongo_db_handler.MongoClient')
    def test_init_with_path(self, patched_mongo_client):
        db_path = 'test://path'
        MongoDBHandler(db_path=db_path, db_name='test')

        calls = [call(db_path)]
        patched_mongo_client.assert_has_calls(calls)

    @patch('app.utils.handlers.mongo_db_handler.MongoClient')
    def test_insert_record_by_creating_existing_db(self, patched_mongo_client):
        patched_mongo_client.insert_record = MongoDBHandler.insert_record
        patched_mongo_client.client.list_database_names = ('test',)

        fake_payload = {}
        client = MongoDBHandler(db_name='test')
        result = client.insert_record(fake_payload)
        self.assertTrue(result)

    @patch('app.utils.handlers.mongo_db_handler.MongoClient')
    def test_insert_record_by_creating_new_db(self, patched_mongo_client):
        patched_mongo_client.insert_record = MongoDBHandler.insert_record
        patched_mongo_client.client.list_database_names = ()

        fake_payload = {}
        client = MongoDBHandler(db_name='test')
        result = client.insert_record(fake_payload)
        self.assertTrue(result)

    @patch('app.utils.handlers.mongo_db_handler.MongoClient')
    @patch('app.utils.handlers.mongo_db_handler.MongoDBHandler._get_database_or_create_new')
    def test_insert_record_by_creating_new_collection(self, patched_get_database_or_create_new, patched_mongo_client):
        fake_result = Mock()
        fake_result.inserted_id = True
        fake_db = MagicMock()
        fake_db.list_collection_names.return_value = ()
        fake_db.insert_one.return_value = fake_result

        patched_get_database_or_create_new.return_value = fake_db
        patched_mongo_client.insert_record = MongoDBHandler.insert_record

        fake_payload = {}
        client = MongoDBHandler(db_name='test')
        result = client.insert_record(fake_payload)
        self.assertTrue(result)

    @patch('app.utils.handlers.mongo_db_handler.MongoClient')
    @patch('app.utils.handlers.mongo_db_handler.MongoDBHandler._get_database_or_create_new')
    def test_insert_record_by_creating_use_existing_collection(
            self, patched_get_database_or_create_new, patched_mongo_client
    ):
        fake_result = Mock()
        fake_result.inserted_id = True
        fake_db = MagicMock()
        fake_db.list_collection_names.return_value = ('currencies', )
        fake_db.insert_one.return_value = fake_result

        patched_get_database_or_create_new.return_value = fake_db
        patched_mongo_client.insert_record = MongoDBHandler.insert_record

        fake_payload = {}
        client = MongoDBHandler(db_name='test')
        result = client.insert_record(fake_payload)
        self.assertTrue(result)

    @patch('app.utils.handlers.mongo_db_handler.MongoClient')
    @patch('app.utils.handlers.mongo_db_handler.MongoDBHandler._get_collection_or_create_new')
    def test_insert_record_returns_false(self, patched_get_collection_or_create_new, patched_mongo_client):
        fake_result = Mock()
        fake_result.inserted_id = None
        fake_collection = Mock()
        fake_collection.insert_one.return_value = fake_result

        patched_get_collection_or_create_new.return_value = fake_collection
        patched_mongo_client.insert_record = MongoDBHandler.insert_record

        fake_payload = {}
        client = MongoDBHandler(db_name='test')
        result = client.insert_record(fake_payload)

        self.assertFalse(result)

    @patch('app.utils.handlers.mongo_db_handler.MongoClient')
    @patch('app.utils.handlers.mongo_db_handler.MongoDBHandler._get_collection_or_create_new')
    def test_insert_record_returns_true(self, patched_get_collection_or_create_new, patched_mongo_client):
        fake_result = Mock()
        fake_result.inserted_id = True
        fake_collection = Mock()
        fake_collection.insert_one.return_value = fake_result

        patched_get_collection_or_create_new.return_value = fake_collection
        patched_mongo_client.insert_record = MongoDBHandler.insert_record

        fake_payload = {}
        client = MongoDBHandler(db_name='test')
        result = client.insert_record(fake_payload)

        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
