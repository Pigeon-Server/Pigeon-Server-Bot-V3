from sqlite3 import Connection as SqliteConnection, Cursor as SqliteCursor
from enum import Enum
from typing import Awaitable, Callable, List, Optional, Type, Union

from satori import Element
from psycopg2.extensions import connection as PostgreSQLConnection, cursor as PostgreSQLCursor
from pymysql import Connection as MySQLConnection
from pymysql.cursors import Cursor as MySQLCursor

from src.element.message import Message
from src.element.result import Result

message_type: Type = Union[str, list[str | Element]]
parser_type: Type = Callable[[Message, List[str]], Awaitable[Optional[Result]]]
Connection: Type = Union[SqliteConnection, MySQLConnection, PostgreSQLConnection]
Cursor: Type = Union[SqliteCursor, MySQLCursor, PostgreSQLCursor]


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
