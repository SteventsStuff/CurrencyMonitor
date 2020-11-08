import argparse
import unittest

from app.utils.handlers.arguments_handler import ArgumentsParser


class TestArgumentsParser(unittest.TestCase):

    def setUp(self) -> None:
        self.argument_parser = ArgumentsParser()

    def test_init(self):
        self.assertIsInstance(self.argument_parser.parser, argparse.ArgumentParser)


if __name__ == '__main__':
    unittest.main()
