from enum import Enum
from typing import Type, Union

from satori import Element

message_type: Type = Union[str, list[str | Element]]


class ReplyType(Enum):
    ACCEPT = 0
    REJECT = 1
    TIMEOUT = 2
