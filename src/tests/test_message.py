from unittest import TestCase

from src.module.message import Message


class TestMessage(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.message = Message('<chronocat:face name="[睁眼]" /><img "/>test<file "/>')

    def test_raw_message(self):
        print(self.message.raw_message)

    def test_message(self):
        print(self.message.message)
        self.assertEqual("[睁眼][图片]test[文件]", self.message.message)
