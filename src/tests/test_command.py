from unittest import TestCase

from src.module.command import Command
from src.module.message import Message


class TestCommand(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.message = Message("/ps add 123 222")

    def test_command_split(self):
        res = Command.command_split(self.message)
        print(res)
        self.assertEqual(["ps", "add", "123", "222"], res)

    def test_command_parsing(self):
        pass
