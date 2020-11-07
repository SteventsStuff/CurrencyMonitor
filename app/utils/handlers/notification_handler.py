import os
import logging
import platform


class NotificationHandler:
    def __init__(self, title: str = None, subtitle: str = None, description: str = None):
        self.title = title
        self.description = description
        self.subtitle = subtitle

    def _send_notification_windows(self):
        pass

    def _send_notification_linux(self):
        pass

    def _send_notification_mac_os(self, group_id: int = 1, sound_type: str = 'default') -> None:
        """
        Using "terminal-notifier" util and sends push-notification in macOS with currency information

        :param group_id: int value for "terminal-notifier" util to determine, should old notification wil be deleted
        :param sound_type: type of sound for notification
        :return: None
        """
        command = (
            f'terminal-notifier -title {self.title} '
            f'-subtitle "{self.subtitle}" '
            f'-message "{self.description}" '
            f'-group {group_id} '
            f'-sound {sound_type}'
        )
        command_status = os.system(command)
        logging.info(f'macOS Notifier command: {command}\nReturned status: {command_status}')

    def send_push_notification(self, *args, **kwargs) -> None:
        """
        Send push notification with currency information, depending on OS type

        :param args: any positional arguments
        :param kwargs: any keyword arguments
        :return: None
        """
        if platform.system() == 'Linux':
            raise NotImplementedError
        elif platform.system() == 'Darwin':
            self._send_notification_mac_os(*args, **kwargs)
        elif platform.system() == 'Windows':
            raise NotImplementedError
        else:
            raise NotImplementedError
