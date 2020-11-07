import unittest
from unittest.mock import patch, mock_open

from app.utils.handlers.config_handler import ConfigHandler
from app.utils.custom_exceptions import ConfigFileDoesNotFound, ConfigMandatoryFieldDoesNotFound


class TestConfigHandler(unittest.TestCase):
    @patch('app.utils.handlers.config_handler.ConfigHandler._read_config_file_yaml')
    def setUp(self, patched_read_config_file_yaml) -> None:
        fake_configs = {
            'base_currency': 'D',
            'main_currencies': 'A B C C',
            'resources': {
                'fake_resource_name': {
                    'url': 'fake_URL',
                    'do_notifications': True
                },
                'fake_resource_name_2': {
                    'url': 'fake_URL',
                    'do_notifications': False
                }
            },
            'mongodb': {
                'db_name': 'DBName'
            },
            'notifications': {
                'resource_limit': 3
            }
        }
        self.config_handler_with_configs = ConfigHandler('fake/path/to/config/file')
        self.config_handler_with_configs.service_configs = fake_configs
        self.config_handler_empty_configs = ConfigHandler('fake/path/to/config/file')
        self.config_handler_empty_configs.service_configs = {}

    @patch('app.utils.handlers.config_handler.ConfigHandler._read_config_file_yaml')
    def test_init(self, patched_read_config_file_yaml):
        patched_read_config_file_yaml.return_value = {'k': 'v'}
        config_handler = ConfigHandler('fake_path_to_config_file')

        self.assertEqual(config_handler.service_configs, {'k': 'v'})

    @patch('builtins.open', new_callable=mock_open)
    @patch('app.utils.handlers.config_handler.yaml')
    def test_read_config_file_yaml_file_exists(self, patched_yaml_lib, patched_open):
        patched_yaml_lib.load.return_value = {}
        result = ConfigHandler._read_config_file_yaml('path/to/file')
        self.assertEqual(result, {})

    @patch('app.utils.handlers.config_handler.logging')
    @patch('app.utils.handlers.config_handler.yaml')
    def test_read_config_file_yaml_file_not_found_error(self, patched_yaml_lib, patched_logging_lib):
        patched_logging_lib.error.return_value = None  # omit error logs, since we do not need it in tests
        patched_yaml_lib.load.return_value = {}
        with self.assertRaises(ConfigFileDoesNotFound):
            ConfigHandler._read_config_file_yaml('')

    def test_get_resource_url_config_exists(self):
        result = self.config_handler_with_configs.get_resource_url('fake_resource_name')
        self.assertEqual(result, 'fake_URL')

    @patch('app.utils.handlers.config_handler.logging')
    def test_get_resource_url_config_does_not_exists(self, patched_logging_lib):
        patched_logging_lib.error.return_value = None  # omit error logs, since we do not need it in tests
        with self.assertRaises(ConfigMandatoryFieldDoesNotFound):
            self.config_handler_with_configs.get_resource_url('fake_resource_name_3')

    def test_get_all_resources_names_resources_exists(self):
        result = self.config_handler_with_configs.get_all_resources_names()
        self.assertEqual(result, ('fake_resource_name', 'fake_resource_name_2'))

    @patch('app.utils.handlers.config_handler.logging')
    def test_get_all_resources_names_resources_does_not_exists(self, patched_logging_lib):
        patched_logging_lib.error.return_value = None  # omit error logs, since we do not need it in tests
        with self.assertRaises(ConfigMandatoryFieldDoesNotFound):
            self.config_handler_empty_configs.get_all_resources_names()

    def test_get_currencies_of_interest_resources_exists(self):
        result = self.config_handler_with_configs.get_currencies_of_interest()
        self.assertTupleEqual(tuple(sorted(result)), ('A', 'B', 'C'))

    @patch('app.utils.handlers.config_handler.logging')
    def test_get_currencies_of_interest_currencies_do_not_exist(self, patched_logging_lib):
        patched_logging_lib.error.return_value = None  # omit error logs, since we do not need it in tests
        with self.assertRaises(ConfigMandatoryFieldDoesNotFound):
            self.config_handler_empty_configs.get_currencies_of_interest()

    def test_get_notifications_config_exists(self):
        result = self.config_handler_with_configs.get_notifications_config()
        expected = {'resource_limit': 3}
        self.assertDictEqual(result, expected)

    @patch('app.utils.handlers.config_handler.logging')
    def test_get_notifications_config_does_not_exist(self, patched_logging_lib):
        patched_logging_lib.error.return_value = None  # omit error logs, since we do not need it in tests
        with self.assertRaises(ConfigMandatoryFieldDoesNotFound):
            self.config_handler_empty_configs.get_notifications_config()

    def test_get_notifications_config_by_resource_config_exists(self):
        result_1 = self.config_handler_with_configs.get_notifications_config_by_resource('fake_resource_name')
        result_2 = self.config_handler_with_configs.get_notifications_config_by_resource('fake_resource_name_2')
        self.assertTrue(result_1)
        self.assertFalse(result_2)

    @patch('app.utils.handlers.config_handler.logging')
    def test_get_notifications_config_by_resource_config_does_not_exist(self, patched_logging_lib):
        patched_logging_lib.error.return_value = None  # omit error logs, since we do not need it in tests
        result = self.config_handler_empty_configs.get_notifications_config_by_resource('fake_resource_name_3')
        self.assertFalse(result)

    def test_get_base_currency_config_exists(self):
        result = self.config_handler_with_configs.get_base_currency()
        self.assertEqual(result, 'D')

    @patch('app.utils.handlers.config_handler.logging')
    def test_get_base_currency_config_does_not_exist(self, patched_logging_lib):
        patched_logging_lib.error.return_value = None  # omit error logs, since we do not need it in tests
        with self.assertRaises(ConfigMandatoryFieldDoesNotFound):
            self.config_handler_empty_configs.get_base_currency()
    
    def test_get_mongodb_config_exists(self):
        result = self.config_handler_with_configs.get_mongodb_config()
        expected = {'db_name': 'DBName'}
        self.assertDictEqual(result, expected)

    @patch('app.utils.handlers.config_handler.logging')
    def test_get_mongodb_config_does_not_exist(self, patched_logging_lib):
        patched_logging_lib.error.return_value = None  # omit error logs, since we do not need it in tests
        with self.assertRaises(ConfigMandatoryFieldDoesNotFound):
            self.config_handler_empty_configs.get_mongodb_config()


if __name__ == '__main__':
    unittest.main()
