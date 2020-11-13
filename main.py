import os
import time
import logging
import datetime
from pathlib import Path

from app.utils.custom_exceptions import *
from app.utils.handlers.config_handler import ConfigHandler
from app.utils.handlers.mongo_db_handler import MongoDBHandler
from app.utils.handlers.arguments_handler import ArgumentsParser
from app.utils.handlers.notification_handler import NotificationHandler
from app.utils.handlers.currency_extraction_handlers import CurrencyExtractionHandler

logger = logging.getLogger('CurrencyMonitor')
# logger consts
LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# notification consts
SUCCESSFULLY_PARSED_RESOURCES_QUANTITY = 0
NOTIFICATION_LIMIT = 3
APP_TITLE = 'CurrencyMonitorApp'
# mapping handlers rules
RESOURCE_HANDLERS_MAPPING = {
    'PrivatBank': CurrencyExtractionHandler.handle_privat_bank,
    'CurrencyAPI': CurrencyExtractionHandler.handle_currency_api,
    'OpenExchangeRateAPI': CurrencyExtractionHandler.handle_open_exchange_api
}


def prepare_db_payload(resource_name: str, data: dict) -> dict:
    """
    Compiling full DB payload by attaching additional metadata about particular currency record

    :param resource_name: name of the resource for currency extraction
    :param data: extracted currencies of interest

    :return: dict with completed DB payload
    """
    payload = {
        'utc_time': time.time(),
        'utc_offset': time.timezone,
        'resource_name': resource_name,
        'currencies': data
    }

    logger.info(f'Completed payload: {payload}')
    return payload


def process_services(
        resources: tuple, db_client: MongoDBHandler, config_helper: ConfigHandler, notify_manager: NotificationHandler
) -> int:
    """
    Process resources services: extract currency from resource -> dump data into DB -> du push notifications

    :param resources: list if resources name
    :param db_client: instance MongoDB client
    :param config_helper: instance of ConfigHandler
    :param notify_manager: instance of NotifyHandler

    :return: index of last resource
    """
    global SUCCESSFULLY_PARSED_RESOURCES_QUANTITY

    last_index = 0

    for index, resource_name in enumerate(resources):
        logger.info(f'Updating currency data fromF resource: {resource_name}')

        do_push_notifications = config_helper.get_notifications_config_by_resource(resource_name)
        # get currencies from resource handler
        try:
            extracted_currencies = RESOURCE_HANDLERS_MAPPING.get(resource_name)(config_helper)
        except TypeError:
            logger.error(f'Can not find handler for "{resource_name}". This resource will be skipped')
            continue

        if not extracted_currencies:
            logger.error(f'Resource: "{resource_name}" will be skipped!')
            continue

        # save data into MongoDB
        logger.info('Preparing DB payload')
        payload = prepare_db_payload(resource_name, extracted_currencies)
        logger.info(f'Inserting data into MongoDB. Payload: {payload}')
        success_status = db_client.insert_record(payload)
        if success_status is True:
            SUCCESSFULLY_PARSED_RESOURCES_QUANTITY += 1

        # do push notification for resource
        if index + 1 <= NOTIFICATION_LIMIT and do_push_notifications:
            logger.info(f'Creating push-notification for resource: "{resource_name}"')
            description = ''
            for currency_name in extracted_currencies:
                description += f'{currency_name}: [Sale: {extracted_currencies[currency_name][0]:.2f},' \
                               f' Purchase: {extracted_currencies[currency_name][1]:.2f}]\n'
            notify_manager.title = APP_TITLE
            notify_manager.subtitle = f'Source: {resource_name}'
            notify_manager.description = description
            try:
                notify_manager.send_push_notification(group_id=index + 1)
            except NotImplementedError:
                logger.warning('Notification for thi system is not supported!')

        # update last index
        last_index = index + 1

    return last_index


def get_config_path(argument_parser: ArgumentsParser) -> str:
    """
    Trying to get config file path from program args, otherwise, searching for default path.

    :return: Path to configuration file
    """
    logger.info('Trying to get configuration file path from program arguments...')
    config_path = argument_parser.get_args().config_path
    if not config_path:
        logger.warning(
            'Can not get configuration file path from program arguments. It was not specified!'
            '\nTrying to use default configuration file path!'
        )
        config_path = Path(__file__).parent / "config.yml"
        if not os.path.exists(config_path):
            logger.error('No configuration files was found! Can not continue work! Terminating program!')
            raise ConfigFileDoesNotFound

    return config_path


def process() -> None:
    """
    Script workflow:
        - set up all handlers
        - loop through specified resources
        - get currency from particular recourse
        - dump data into DB
        - do push notification for recourse (optional)
        - do push notification about script results

    :return: None
    """
    logging.info('Currency Monitor has started.')
    global NOTIFICATION_LIMIT

    argument_parser = ArgumentsParser()

    # get path to config file
    config_path = get_config_path(argument_parser)

    # set up handlers
    config_handler = ConfigHandler(str(config_path))
    db_client = MongoDBHandler(
        db_name=config_handler.get_mongodb_config().get('db_name', 'CurrencyMonitorDB'),
        db_path=config_handler.get_mongodb_config().get('db_path'),
    )
    notify_handler = NotificationHandler()

    # set up notification limit
    new_notification_limit = config_handler.get_notifications_config().get('resource_limit')
    if new_notification_limit is not None:
        NOTIFICATION_LIMIT = new_notification_limit
    logger.info(f'Notification limit set to: {NOTIFICATION_LIMIT}')

    # processing resources
    resources = config_handler.get_all_resources_names()
    logger.info(f'Got {len(resources)} resources to process')
    last_index = process_services(resources, db_client, config_handler, notify_handler)

    # do notification report
    notify_handler.subtitle = 'Service Report'
    notify_handler.description = (
        f'{SUCCESSFULLY_PARSED_RESOURCES_QUANTITY}/{len(resources)} Resources was successfully parsed'
    )
    # increase last_index to have different group id from last notification
    try:
        notify_handler.send_push_notification(group_id=last_index + 1)
    except NotImplementedError:
        logger.warning('Notification for thi system is not supported!')


def main() -> None:
    # setting up logger
    logging.basicConfig(
        format=LOGGER_FORMAT,
        filename=f'currencyMonitor_{datetime.datetime.utcnow().strftime("%d%m%y")}.log',
        level=logging.INFO
    )
    try:
        process()
    except (ConfigFileDoesNotFound, CanNotGetCurrenciesFromService, CanNotFindNewBaseCurrency) as e:
        logger.error(f'Can not continue processing...\nError: {e}')
        raise e
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
