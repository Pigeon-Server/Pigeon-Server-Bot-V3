from enum import Enum
from typing import Awaitable, Callable, List, Optional, Type, Union

from satori import Element

from src.element.message import Message
from src.element.result import Result

message_type: Type = Union[str, list[str | Element]]
parser_type: Type = Callable[[Message, List[str]], Awaitable[Optional[Result]]]


class ReplyType(Enum):
    ACCEPT = 0
    REJECT = 1
    TIMEOUT = 2


class HttpCode(Enum):
    OK = 200
    ERROR_PARAMS = 400
    FORBIDDEN = 403
    SERVER_ERROR = 500


class ReturnType(Enum):
    NONE = 0
    ONE = 1
    ALL = 2
