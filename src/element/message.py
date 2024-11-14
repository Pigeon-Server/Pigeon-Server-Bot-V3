from datetime import datetime
from typing import List
from typing import Type, Union

from satori import Element, Event, MessageObject
from satori.element import At, Audio, Custom, File, Image, Quote, Text, Video


event_type: Type = Union[At, Text, Image, Audio, Video, File, Quote, Custom]


class Message:
    _event: Event
    _raw_message: MessageObject
    _elements: List[Element]
    _message: str = ""
    _has_quote: bool = False
    _quote_id: str = ""
    _send_time: datetime

    def __init__(self, event: Event):
        self._event = event
        self._send_time = event.timestamp
        self._raw_message = event.message
        self._elements = self._raw_message.message
        for element in self._elements:
            if isinstance(element, At):
                self._message += f"@{element.name}({element.id})"
                continue
            if isinstance(element, Text):
                self._message += element.text
                continue
            if isinstance(element, Image):
                self._message += "[图片]"
                continue
            if isinstance(element, Audio):
                self._message += "[语音]"
                continue
            if isinstance(element, Video):
                self._message += "[视频]"
                continue
            if isinstance(element, File):
                self._message += "[文件]"
                continue
            if isinstance(element, Quote):
                self._has_quote = True
                self._message += f"[回复({element._children[0]._attrs['id']})]"
                continue
            if isinstance(element, Custom):
                match element.tag:
                    case "chronocat:face":
                        self._message += f"{element._attrs['name']}"
                continue

    def find(self, obj_type: type) -> List[event_type]:
        return list(filter(lambda x: isinstance(x, obj_type), self._elements))

    def find_first(self, obj_type: type) -> event_type:
        for i in self._elements:
            if isinstance(i, obj_type):
                return i

    @property
    def message(self) -> str:
        return self._message

    @property
    def raw_message(self) -> str:
        return self._raw_message.content

    @property
    def group_id(self) -> str:
        return self._event.guild.id

    @property
    def group_name(self) -> str:
        return self._event.guild.name

    @property
    def group_info(self) -> str:
        return f"{self.group_name}({self.group_id})"

    @property
    def sender_id(self) -> str:
        return self._event.user.id

    @property
    def sender_name(self) -> str:
        if self._event.member.nick:
            return self._event.member.nick
        return self._event.user.name

    @property
    def sender_info(self) -> str:
        return f"{self.sender_name}({self.sender_id})"

    @property
    def message_id(self) -> str:
        return self._event.message.id

    @staticmethod
    def parse(elements: Union[List[Union[str, Element]], str]) -> str:
        if isinstance(elements, str):
            return elements.replace("\n", "|")
        res = ""
        for element in elements:
            if isinstance(element, str):
                res += element
            if isinstance(element, Element):
                if isinstance(element, At):
                    res += f"@{element.id}"
                    continue
                if isinstance(element, Text):
                    res += element.text
                    continue
                if isinstance(element, Image):
                    res += "[图片]"
                    continue
                if isinstance(element, Quote):
                    res += f"[回复({element.id})]"
        return res.replace("\n", "|")

    @property
    def is_command(self) -> bool:
        return self._message.startswith("/") or self._message.startswith("!")

    @property
    def send_time(self) -> datetime:
        return self._send_time
