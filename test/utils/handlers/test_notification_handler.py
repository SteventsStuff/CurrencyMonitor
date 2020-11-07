import unittest
from unittest.mock import patch

from app.utils.handlers.notification_handler import NotificationHandler


class TestNotificationHandler(unittest.TestCase):
    def test_init(self):
        notification_handler = NotificationHandler('title', 'subtitle', 'description')
        self.assertEqual(notification_handler.title, 'title')
        self.assertEqual(notification_handler.subtitle, 'subtitle')
        self.assertEqual(notification_handler.description, 'description')

    @patch('app.utils.handlers.notification_handler.platform')
    def test_send_push_notification_unknown_platform(self, patched_platform):
        patched_platform.system.return_value = 'Fake'
        self.assertRaises(NotImplementedError)

    @patch('app.utils.handlers.notification_handler.platform')
    @patch('app.utils.handlers.notification_handler.NotificationHandler._send_notification_mac_os')
    def test_send_push_notification_max_os_was_called(self, patched_send_notification_mac_os, patched_platform):
        patched_platform.system.return_value = 'Darwin'
        patched_send_notification_mac_os.asserd_called()

    @patch('app.utils.handlers.notification_handler.platform')
    def test_send_push_notification_linux_was_called(self, patched_platform):
        patched_platform.system.return_value = 'Linux'
        self.assertRaises(NotImplementedError)

    @patch('app.utils.handlers.notification_handler.platform')
    def test_send_push_notification_max_windows_called(self, patched_platform):
        patched_platform.system.return_value = 'Windows'
        self.assertRaises(NotImplementedError)


if __name__ == '__main__':
    unittest.main()
