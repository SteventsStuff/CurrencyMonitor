import yaml
import logging

from app.utils.custom_exceptions import ConfigFileDoesNotFound, ConfigMandatoryFieldDoesNotFound


class ConfigHandler:
    @staticmethod
    def _read_config_file_yaml(path: str) -> dict:
        """
        Parse YAML config file

        :param path: path to config file
        :return: pythonic dict object with configs from file
        """
        try:
            with open(path, 'r') as file:
                configs = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError as e:
            logging.error(f'Can not find config file from path "{path}"\nError: {e}')
            raise ConfigFileDoesNotFound
        else:
            return configs

    def __init__(self, path: str):
        self.service_configs = self._read_config_file_yaml(path)
        logging.info(f'Got configs: {self.service_configs}')

    def get_resource_url(self, resource_name: str) -> str:
        try:
            return self.service_configs['resources'][resource_name]['url']
        except KeyError as e:
            logging.error(f'Mandatory filed "{e}" was not specified in config file!')
            raise ConfigMandatoryFieldDoesNotFound

    def get_all_resources_names(self) -> tuple:
        try:
            return tuple(self.service_configs['resources'].keys())
        except KeyError as e:
            logging.error(f'Mandatory filed "{e}" was not specified in config file!')
            raise ConfigMandatoryFieldDoesNotFound

    def get_currencies_of_interest(self) -> tuple:
        try:
            main_currencies = self.service_configs['main_currencies'].split()  # list for currencies
            main_currencies = set(main_currencies)  # left only unique currencies
            return tuple(main_currencies)
        except KeyError as e:
            logging.error(f'Mandatory filed "{e}" was not specified in config file!')
            raise ConfigMandatoryFieldDoesNotFound

    def get_notifications_config(self) -> dict:
        try:
            return self.service_configs['notifications']
        except KeyError as e:
            logging.error(f'Mandatory filed "{e}" was not specified in config file!')
            raise ConfigMandatoryFieldDoesNotFound

    def get_notifications_config_by_resource(self, resource_name: str) -> bool:
        try:
            return self.service_configs['resources'][resource_name]['do_notifications']
        except KeyError:
            logging.error(
                f'Can not find notification config by resource: "{resource_name}"! Notification won\'t be set'
            )
            return False

    def get_base_currency(self) -> str:
        try:
            return self.service_configs['base_currency']
        except KeyError as e:
            logging.error(f'Mandatory filed "{e}" was not specified in config file!')
            raise ConfigMandatoryFieldDoesNotFound

    def get_mongodb_config(self) -> dict:
        try:
            return self.service_configs['mongodb']
        except KeyError as e:
            logging.error(f'Mandatory filed "{e}" was not specified in config file!')
            raise ConfigMandatoryFieldDoesNotFound
