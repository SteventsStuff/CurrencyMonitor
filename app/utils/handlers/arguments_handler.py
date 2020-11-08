import argparse


class ArgumentsParser:
    def __init__(self):
        self.parser = self._set_up_parser()

    def get_args(self):
        return self.parser.parse_args()

    @staticmethod
    def _set_up_parser():
        parser = argparse.ArgumentParser(description='Extracts currency exchange rate from different sources')
        parser.add_argument(
            '--config_path', type=str, help='Path to config file', default='',
        )
        return parser
