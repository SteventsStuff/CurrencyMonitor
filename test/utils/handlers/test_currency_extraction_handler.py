import json
import unittest
from unittest.mock import Mock, patch

from app.utils.handlers.currency_extraction_handlers import (
    CurrencyExtractionHandler, CanNotGetCurrenciesFromService, CanNotFindNewBaseCurrency
)


class TestCurrencyExtractionHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.privat_bank_api_response = {
            'exchangeRate': [
                {'currency': 'Stub', 'saleRateNB': 1, 'purchaseRateNB': 1},
                {'currency': 'A', 'saleRateNB': 1, 'purchaseRateNB': 11},
                {'currency': 'B', 'saleRateNB': 2, 'purchaseRateNB': 22},
                {'currency': 'C', 'saleRateNB': 3, 'purchaseRateNB': 33},
            ]
        }
        self.open_exchange_api_response_success = {
            'result': 'success',
            'base_code': 'A',
            'rates': {
                'A': 1,
                'UAH': 2,
                'C': 3
            }
        }
        self.open_exchange_api_response_error = {'result': 'fail'}
        self.currency_api_response_invalid = {'valid': False}
        self.currency_api_response_valid = {
            'valid': True,
            'base': 'A',
            'rates': {
                'A': 1,
                'UAH': 2,
                'C': 3
            }
        }
        self.config_helper_1 = Mock()
        self.config_helper_1.get_resource_url.return_value = 'privat_url'
        self.config_helper_1.get_currencies_of_interest.return_value = ('A', 'D', 'B')
        self.config_helper_2 = Mock()
        self.config_helper_2.get_resource_url.return_value = 'privat_url'
        self.config_helper_2.get_currencies_of_interest.return_value = ('A', 'B', 'C')

    @patch('app.utils.handlers.currency_extraction_handlers.get_with_retry')
    def test_get_currency_from_resource_got_response(self, patched_get_with_retry):
        fake_response = Mock()
        fake_response.json.return_value = {}
        fake_response.text = 'fake response text'
        patched_get_with_retry.return_value = fake_response

        result = CurrencyExtractionHandler.get_currency_from_resource('fake_url')
        expected = {}
        self.assertEqual(result, expected)

    @patch('app.utils.handlers.currency_extraction_handlers.get_with_retry')
    def test_get_currency_from_resource_can_not_parse_response(self, patched_get_with_retry):
        fake_response = Mock()
        fake_response.json.side_effect = json.JSONDecodeError('error', 'blah', 1)
        patched_get_with_retry.return_value = fake_response

        with self.assertRaises(CanNotGetCurrenciesFromService):
            CurrencyExtractionHandler.get_currency_from_resource('fake_url')

    def test_change_currency_base_no_base_value_in_currency_dict(self):
        with self.assertRaises(CanNotFindNewBaseCurrency):
            CurrencyExtractionHandler.change_currency_base('', 'fakeNewBase', {})

    def test_change_currency_base(self):
        exchange_rates = {
            'USD': 1,
            'CAN': 2,
            'USD2': 4
        }
        rates_with_new_base = CurrencyExtractionHandler.change_currency_base('USD', 'CAN', exchange_rates)
        expected = {
            'USD': 2,
            'CAN': 1.0,
            'USD2': 0.5
        }
        self.assertEqual(expected, rates_with_new_base)

    # PrivatBank Tests
    @patch('app.utils.handlers.currency_extraction_handlers.CurrencyExtractionHandler.get_currency_from_resource')
    def test_handle_privat_bank_full_response_parsed(self, patched_get_currency_from_resource):
        patched_get_currency_from_resource.return_value = self.privat_bank_api_response
        result = CurrencyExtractionHandler.handle_privat_bank(self.config_helper_2)
        expected = {
            'A': (1, 11),
            'B': (2, 22),
            'C': (3, 33),
        }
        self.assertEqual(expected, result)

    @patch('app.utils.handlers.currency_extraction_handlers.CurrencyExtractionHandler.get_currency_from_resource')
    def test_handle_privat_bank_not_full_response_parsed(self, patched_get_currency_from_resource):
        patched_get_currency_from_resource.return_value = self.privat_bank_api_response
        result = CurrencyExtractionHandler.handle_privat_bank(self.config_helper_1)
        expected = {
            'A': (1, 11),
            'B': (2, 22),
        }
        self.assertEqual(expected, result)

    # OpenExchangeAPI Tests
    @patch('app.utils.handlers.currency_extraction_handlers.CurrencyExtractionHandler.get_currency_from_resource')
    def test_handle_open_exchange_api_failed_api_response(self, patched_get_currency_from_resource):
        patched_get_currency_from_resource.return_value = self.open_exchange_api_response_error
        result = CurrencyExtractionHandler.handle_open_exchange_api(self.config_helper_1)
        expected = {}
        self.assertEqual(result, expected)

    @patch('app.utils.handlers.currency_extraction_handlers.CurrencyExtractionHandler.change_currency_base')
    @patch('app.utils.handlers.currency_extraction_handlers.CurrencyExtractionHandler.get_currency_from_resource')
    def test_handle_open_exchange_api_success_api_response(
            self, patched_get_currency_from_resource, patched_change_currency_base
    ):
        patched_get_currency_from_resource.return_value = self.open_exchange_api_response_success
        patched_change_currency_base.return_value = {
            'A': 0.5,
            'UAH': 1,
            'C': 1.5
        }
        result = CurrencyExtractionHandler.handle_open_exchange_api(self.config_helper_2)
        expected = {
            'A': (0.5, 0.5),
            'C': (1.5, 1.5),
        }
        self.assertEqual(expected, result)

    # CurrencyAPI Tests
    @patch('app.utils.handlers.currency_extraction_handlers.os')
    @patch('app.utils.handlers.currency_extraction_handlers.CurrencyExtractionHandler.get_currency_from_resource')
    def test_handle_currency_api_invalid_response(self, patched_get_currency_from_resource, patched_os):
        patched_get_currency_from_resource.return_value = self.currency_api_response_invalid
        patched_os.environ.get.return_value = 'API_KEY'
        result = CurrencyExtractionHandler.handle_currency_api(self.config_helper_2)
        expected = {}
        self.assertEqual(expected, result)

    @patch('app.utils.handlers.currency_extraction_handlers.os')
    @patch('app.utils.handlers.currency_extraction_handlers.CurrencyExtractionHandler.change_currency_base')
    @patch('app.utils.handlers.currency_extraction_handlers.CurrencyExtractionHandler.get_currency_from_resource')
    def test_handle_currency_api(self, patched_get_currency_from_resource, patched_change_currency_base, patched_os):
        patched_get_currency_from_resource.return_value = self.currency_api_response_valid
        patched_os.environ.get.return_value = 'API_KEY'
        patched_change_currency_base.return_value = {
            'A': 0.5,
            'UAH': 1,
            'C': 1.5
        }
        result = CurrencyExtractionHandler.handle_currency_api(self.config_helper_2)
        expected = {
            'A': (0.5, 0.5),
            'C': (1.5, 1.5),
        }
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
