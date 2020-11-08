import unittest
from unittest.mock import Mock, MagicMock, patch, call

from main import (
    prepare_db_payload, process_services, process, get_config_path, ConfigFileDoesNotFound,
    CanNotFindNewBaseCurrency, CanNotGetCurrenciesFromService, main
)


class TestMain(unittest.TestCase):
    def setUp(self) -> None:
        self.fake_args = Mock()
        self.fake_args.config_path = ''

        fake_parent_with_div = MagicMock()
        fake_parent_with_div.__truediv__.return_value = 'new_path'
        self.fake_parent = Mock()
        self.fake_parent.parent.parent = fake_parent_with_div

    @patch('main.time')
    def test_prepare_db_payload(self, patched_time):
        patched_time.time.return_value = 123456.7
        patched_time.timezone = 1234

        result = prepare_db_payload('fake_resource_name', {'k': 'v'})
        expected = {
            'utc_time': 123456.7,
            'utc_offset': 1234,
            'resource_name': 'fake_resource_name',
            'currencies': {'k': 'v'}
        }
        self.assertEqual(result, expected)

    @patch('main.NOTIFICATION_LIMIT', 3)
    @patch('main.prepare_db_payload')
    @patch('main.RESOURCE_HANDLERS_MAPPING')
    def test_process_services(self, patched_resource_handler_mapping, patched_prepare_db_payload):
        fake_handler = Mock()
        fake_handler.side_effect = [{'k': (1, 2)}, {}, TypeError, {'k': (1, 2)}]
        patched_resource_handler_mapping.get.return_value = fake_handler

        patched_prepare_db_payload.return_value = {'k': 'v'}

        fake_db_client = Mock()
        fake_db_client.insert_record.side_effect = [True, False]

        fake_config_helper = Mock()
        fake_config_helper.get_notifications_config_by_resource.side_effect = [True, False, True, False]

        fake_notify_manager = Mock()
        fake_notify_manager.title = ''
        fake_notify_manager.subtitle = ''
        fake_notify_manager.description = ''
        fake_notify_manager.send_push_notification.return_value = None
        fake_resources = ('resource1', 'resource2', 'resource3', 'resource4')

        result = process_services(fake_resources, fake_db_client, fake_config_helper, fake_notify_manager)
        expected = 4

        self.assertEqual(result, expected)

    @patch('main.os')
    @patch('main.Path')
    def test_get_config_path_no_path_no_config_file(self, patched_path, patched_os):
        fake_argument_parser = Mock()
        fake_argument_parser.get_args.return_value = self.fake_args

        patched_path.return_value = self.fake_parent
        patched_os.path.exists.return_value = False

        with self.assertRaises(ConfigFileDoesNotFound):
            get_config_path(fake_argument_parser)

    @patch('main.os')
    @patch('main.Path')
    def test_get_config_path_no_path_config_file_exists(self, patched_path, patched_os):
        fake_argument_parser = Mock()
        fake_argument_parser.get_args.return_value = self.fake_args

        patched_path.return_value = self.fake_parent
        patched_os.path.exists.return_value = True

        result = get_config_path(fake_argument_parser)
        expected = 'new_path'
        self.assertEqual(result, expected)

    def test_get_config_path_path_exists(self):
        fake_args = Mock()
        fake_args.config_path = 'fake_conf_path'
        fake_argument_parser = Mock()
        fake_argument_parser.get_args.return_value = fake_args

        result = get_config_path(fake_argument_parser)

        self.assertEqual(result, 'fake_conf_path')

    @patch('main.process_services')
    @patch('main.NotificationHandler')
    @patch('main.MongoDBHandler')
    @patch('main.ConfigHandler')
    @patch('main.get_config_path')
    @patch('main.ArgumentsParser')
    def test_process(
            self, patched_argument_parser, patched_get_config_path, patched_config_handler, patched_mongo_db_handler,
            patched_notification_handler, patched_process_services
    ):
        patched_config_handler.get_notifications_config.return_value = {'resource_limit': None}
        patched_process_services.return_value = 3
        patched_notification_handler.send_push_notification.return_value = None

        process()

        calls = [
            call().send_push_notification(group_id=4)
        ]

        patched_notification_handler.assert_has_calls(calls)

    @patch('main.process')
    def test_main_errors(self, patched_process):
        patched_process.side_effect = [
            CanNotFindNewBaseCurrency, ConfigFileDoesNotFound, CanNotGetCurrenciesFromService
        ]
        with self.assertRaises(CanNotFindNewBaseCurrency):
            main()
        with self.assertRaises(ConfigFileDoesNotFound):
            main()
        with self.assertRaises(CanNotGetCurrenciesFromService):
            main()


if __name__ == '__main__':
    unittest.main()
