import unittest
from unittest.mock import patch

import requests

from app.utils.handlers import requests_handler


class TestRequestHandler(unittest.TestCase):
    @patch('requests.get')
    def test_get_with_retry_200_OK(self, patched_get_request):
        # mock 'requests' response
        fake_response = requests.Response()
        fake_response.status_code = 200
        patched_get_request.return_value = fake_response
        # run function
        result = requests_handler.get_with_retry('fake_url')
        # check result
        self.assertIsInstance(result, requests.Response)
        self.assertEqual(result.status_code, 200)

    @patch('requests.get')
    def test_get_with_retry_300_OK(self, patched_get_request):
        # mock 'requests' response
        fake_response = requests.Response()
        fake_response.status_code = 300
        patched_get_request.return_value = fake_response
        # run function
        result = requests_handler.get_with_retry('fake_url')
        # check result
        self.assertIsInstance(result, requests.Response)
        self.assertEqual(result.status_code, 300)

    @patch('requests.get')
    def test_get_with_retry_404_Not_Found(self, patched_get_request):
        # mock 'requests' response
        fake_response = requests.Response()
        fake_response.status_code = 404
        patched_get_request.return_value = fake_response
        # run function
        result = requests_handler.get_with_retry('fake_url')
        # check result
        self.assertIsInstance(result, requests.Response)
        self.assertEqual(result.status_code, 404)

    @patch('requests.get')
    def test_get_with_retry_500_Server_internal_error(self, patched_get_request):
        # mock 'requests' response
        fake_response = requests.Response()
        fake_response.status_code = 500
        patched_get_request.return_value = fake_response

        # run function
        result = requests_handler.get_with_retry('fake_url')
        # check result
        self.assertIsInstance(result, requests.Response)
        self.assertEqual(result.status_code, 500)


if __name__ == '__main__':
    unittest.main()
