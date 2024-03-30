import sys
from unittest import TestCase

from satori import Event

from src.module.message import Message


class TestMessage(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.message = Message(Event.parse({
            "id": 1956,
            "type": "message-created",
            "platform": "chronocat",
            "self_id": "3079354079",
            "timestamp": 1711817768000,
            "user": {
                "id": "2054186369",
                "avatar": "http://thirdqq.qlogo.cn/headimg_dl?dst_uin=2054186369&spec=640"
            },
            "channel": {
                "type": 0, "id": "884872470", "name": "Pigeon Server"
            },
            "guild": {
                "id": "884872470",
                "name": "Pigeon Server",
                "avatar": "https://p.qlogo.cn/gh/884872470/884872470/640"
            },
            "member": {
                "nick": "JustMalkuth"
            },
            "message": {
                "id": "7352201330372868920",
                "content": '<chronocat:face name="[睁眼]" /><img src="" />test<file src=""/>'
            }
        }))

    def test_raw_message(self):
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"{self.message.raw_message}\n"
              f"{'-' * 10}")

    def test_message(self):
        expect_result = "[睁眼][图片]test[文件]"
        res = self.message.message
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"Expect result: {expect_result}\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertEqual(expect_result, res)
