import argparse
import unittest

from app.utils.handlers.argumets_handler import ArgumentsParser


class TestArgumentsParser(unittest.TestCase):

    def setUp(self) -> None:
        self.argument_parser = ArgumentsParser()

    def test_init(self):
        self.assertIsInstance(self.argument_parser.parser, argparse.ArgumentParser)

    def test_get_args(self):
        """
        Context: for current tests there is no actual program args past,
        just checking default value of "config_path" argument
        """
        args = self.argument_parser.get_args()

        self.assertIsInstance(args, argparse.Namespace)
        self.assertEqual(args.config_path, '')


if __name__ == '__main__':
    unittest.main()
