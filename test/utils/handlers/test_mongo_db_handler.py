import unittest
from unittest.mock import Mock, MagicMock, patch, call

from app.utils.handlers.mongo_db_handler import MongoDBHandler


HANDLER_PATH = 'app.utils.handlers.mongo_db_handler'


class TestMongoDBHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.os_env_patched_value = ['MONGO_DB_ADDR', '1234']

    @patch(f'{HANDLER_PATH}.os')
    @patch(f'{HANDLER_PATH}.MongoClient')
    def test_init_no_path(self, patched_mongo_client, patched_os):
        db_path = None
        patched_os.environ.get.side_effect = self.os_env_patched_value

        MongoDBHandler(db_path=db_path, db_name='test')

        calls = [call('MONGO_DB_ADDR', 1234)]
        patched_mongo_client.assert_has_calls(calls)

    @patch(f'{HANDLER_PATH}.MongoClient')
    def test_init_with_path(self, patched_mongo_client):
        db_path = 'test://path'
        MongoDBHandler(db_path=db_path, db_name='test')

        calls = [call(db_path)]
        patched_mongo_client.assert_has_calls(calls)

    @patch(f'{HANDLER_PATH}.os')
    @patch(f'{HANDLER_PATH}.MongoClient')
    def test_insert_record_by_creating_existing_db(self, patched_mongo_client, patched_os):
        patched_os.environ.get.side_effect = self.os_env_patched_value

        patched_mongo_client.insert_record = MongoDBHandler.insert_record
        patched_mongo_client.client.list_database_names = ('test',)

        fake_payload = {}
        client = MongoDBHandler(db_name='test')
        result = client.insert_record(fake_payload)
        self.assertTrue(result)

    @patch(f'{HANDLER_PATH}.os')
    @patch(f'{HANDLER_PATH}.MongoClient')
    def test_insert_record_by_creating_new_db(self, patched_mongo_client, patched_os):
        patched_os.environ.get.side_effect = self.os_env_patched_value

        patched_mongo_client.insert_record = MongoDBHandler.insert_record
        patched_mongo_client.client.list_database_names = ()

        fake_payload = {}
        client = MongoDBHandler(db_name='test')
        result = client.insert_record(fake_payload)
        self.assertTrue(result)

    @patch(f'{HANDLER_PATH}.os')
    @patch(f'{HANDLER_PATH}.MongoClient')
    @patch(f'{HANDLER_PATH}.MongoDBHandler._get_database_or_create_new')
    def test_insert_record_by_creating_new_collection(
            self, patched_get_database_or_create_new, patched_mongo_client, patched_os
    ):
        patched_os.environ.get.side_effect = self.os_env_patched_value

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

    @patch(f'{HANDLER_PATH}.os')
    @patch(f'{HANDLER_PATH}.MongoClient')
    @patch(f'{HANDLER_PATH}.MongoDBHandler._get_database_or_create_new')
    def test_insert_record_by_creating_use_existing_collection(
            self, patched_get_database_or_create_new, patched_mongo_client, patched_os
    ):
        patched_os.environ.get.side_effect = self.os_env_patched_value

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

    @patch(f'{HANDLER_PATH}.os')
    @patch(f'{HANDLER_PATH}.MongoClient')
    @patch(f'{HANDLER_PATH}.MongoDBHandler._get_collection_or_create_new')
    def test_insert_record_returns_false(self, patched_get_collection_or_create_new, patched_mongo_client, patched_os):
        patched_os.environ.get.side_effect = self.os_env_patched_value

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

    @patch(f'{HANDLER_PATH}.os')
    @patch(f'{HANDLER_PATH}.MongoClient')
    @patch(f'{HANDLER_PATH}.MongoDBHandler._get_collection_or_create_new')
    def test_insert_record_returns_true(self, patched_get_collection_or_create_new, patched_mongo_client, patched_os):
        patched_os.environ.get.side_effect = self.os_env_patched_value

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
