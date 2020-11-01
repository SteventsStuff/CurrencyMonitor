import os
import json
import logging
import datetime
from typing import Optional

from app.utils.handlers.requests_handler import get_with_retry
from app.utils.handlers.config_handler import ConfigHandler
from app.utils.custom_exceptions import CanNotGetCurrenciesFromService, CanNotFindNewBaseCurrency


class CurrencyExtractionHandler:
    @staticmethod
    def get_currency_from_resource(url: str, *args, **kwargs) -> Optional[dict]:
        """
        Executes GET request to specified URL to get currency exchange rate

        :param url: request URL
        :return: dict of JSON response from service
        """
        logging.info(f'Trying to get currencies from:\nURL: {url}')
        response = get_with_retry(url, *args, **kwargs)
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            logging.error(f'Error during response parsing.\nURL: {url}\nResponse: {response.text}\nError: {e}')
            raise CanNotGetCurrenciesFromService
        else:
            logging.info(f'Got response from {url}\nResponse: {response_data}')
            return response_data

    @staticmethod
    def change_currency_base(current_base: str, new_base: str, exchange_rates: dict) -> dict:
        """
        Changes currency base in cases when API returns currencies with base different from "UAH"

        :param current_base: current currency base
        :param new_base: new currency base
        :param exchange_rates: data from API response
        :return: recalculated dict of currencies
        """
        new_base_currencies = {}
        new_base_value = exchange_rates.get(new_base)
        if new_base_value is None:
            logging.error(f'Can not find "{new_base}" in {exchange_rates}')
            raise CanNotFindNewBaseCurrency

        for currency in exchange_rates:
            if currency == current_base:
                new_base_currencies[currency] = new_base_value
            else:
                new_base_currencies[currency] = round(new_base_value / exchange_rates[currency], 4)

        return new_base_currencies

    @classmethod
    def handle_privat_bank(cls, config_helper: ConfigHandler) -> dict:
        """
        PrivatBank currency extraction handler

        :param config_helper: instance of ConfigHelper to get information about currencies of interest
        :return: exchange rate of currencies of interest
        """
        params = {
            'date': datetime.datetime.now().strftime('%d.%m.%Y'),
            'json': ''
        }
        resource_url = config_helper.get_resource_url('PrivatBank')
        response_data = cls.get_currency_from_resource(resource_url, params)
        currencies_of_interest = config_helper.get_currencies_of_interest()
        extracted_currencies = dict()
        for currency in response_data['exchangeRate'][1:]:  # skip first record, because it is UAH
            try:
                if currency['currency'] in currencies_of_interest:
                    extracted_currencies[currency['currency']] = (
                        currency.get('saleRateNB'),
                        currency.get('purchaseRateNB')
                    )
            except KeyError as e:
                logging.warning(
                    f'Can not extract key "currency" from payload: {currency}. This payload will be passed!\n'
                    f'Error description: {e}'
                )
                continue

        return extracted_currencies

    @classmethod
    def handle_open_exchange_api(cls, config_helper: ConfigHandler) -> dict:
        """
        OpenExchangeRateAPI currency extraction handler.
        Additionally, changing currency base to UAH

        :param config_helper: instance of ConfigHelper to get information about currencies of interest
        :return: exchange rate of currencies of interest
        """
        resource_url = config_helper.get_resource_url('OpenExchangeRateAPI')
        response_data = cls.get_currency_from_resource(resource_url)

        if response_data['result'] == 'success':
            usd_base_currencies = response_data['rates']
        else:
            logging.error('Can not get correct response from OpenExchangeRateAPI!')
            return {}

        # changing base currency from USD to UAH
        uah_base_currencies = cls.change_currency_base(response_data['base_code'], 'UAH', usd_base_currencies)

        currencies_of_interest = config_helper.get_currencies_of_interest()
        extracted_currencies = dict()
        for currency in uah_base_currencies:
            if currency in currencies_of_interest:
                extracted_currencies[currency] = (uah_base_currencies[currency], uah_base_currencies[currency])
        return extracted_currencies

    @classmethod
    def handle_currency_api(cls, config_helper: ConfigHandler) -> dict:
        """
        CurrencyAPI currency extraction handler.
        Additionally, changing currency base to UAH

        :param config_helper: instance of ConfigHelper to get information about currencies of interest
        :return: exchange rate of currencies of interest
        """
        resource_url = config_helper.get_resource_url('CurrencyAPI')
        params = {
            'key': os.environ.get('CURRENCY_API_KEY')
        }
        response_data = cls.get_currency_from_resource(resource_url, params=params)

        # checking status
        if response_data.get('valid', False) is not True:
            logging.error('Got incorrect response from CurrencyAPI! Empty data will be returned!')
            return {}

        currencies = response_data['rates']
        # changing base currency from USD to UAH
        uah_base_currencies = cls.change_currency_base(response_data['base'], 'UAH', currencies)

        currencies_of_interest = config_helper.get_currencies_of_interest()
        extracted_currencies = dict()
        for currency in uah_base_currencies:
            if currency in currencies_of_interest:
                extracted_currencies[currency] = (uah_base_currencies[currency], uah_base_currencies[currency])
        return extracted_currencies
