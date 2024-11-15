from enum import Enum
from typing import Awaitable, Callable, List, Optional, Type, Union

from satori import Element

from src.element.message import Message
from src.element.result import Result

MessageType: Type = Union[str, list[str | Element]]
CommandHandler: Type = Callable[[Message, List[str]], Awaitable[Optional[Result]]]


class ReplyType(Enum):
    ACCEPT = 0
    REJECT = 1
    TIMEOUT = 2


class HttpCode(Enum):
    OK = 200
    ERROR_PARAMS = 400
    FORBIDDEN = 403
    SERVER_ERROR = 500


class VersionType(Enum):
    ALL_MATCH = 0
    PATCH_UNMATCH = 1
    MINOR_UNMATCH = 2
    MAJOR_UNMATCH = 3
