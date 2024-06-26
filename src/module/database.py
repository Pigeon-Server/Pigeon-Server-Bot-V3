from re import Pattern, compile
from typing import List, Optional, Tuple, Union, overload

import pymysql
from pymysql import Connection
from pymysql.cursors import Cursor
from dbutils.pooled_db import PooledDB

from src.base.logger import logger
from src.element.message import Message
from src.model.message_model import MessageModel
from src.type.config import Config
from src.type.types import ReturnType

remove_space_pattern: Pattern = compile(r"\s{2,}")


class Database:
    _pool: PooledDB

    def __init__(self, db_config: Config.DatabaseConfig):
        self._pool = PooledDB(
            creator=pymysql,
            mincached=10,
            maxconnections=200,
            blocking=False,
            host=db_config.host,
            port=db_config.port,
            user=db_config.username,
            password=db_config.password,
            database=db_config.database_name,
            autocommit=db_config.auto_commit,
            connect_timeout=5,
            write_timeout=5,
            read_timeout=5
        )

    def get_connection(self) -> Tuple[Connection, Cursor]:
        connection = self._pool.connection()
        return connection, connection.cursor()

    @overload
    def run_command(self, query: str,
                    args: Optional[list] = None,
                    return_type: ReturnType = ReturnType.NONE) -> Optional[tuple]:
        ...

    @overload
    def run_command(self, query: list,
                    args: Optional[List[list]] = None,
                    return_type: ReturnType = ReturnType.NONE) -> Optional[tuple]:
        ...

    def run_command(self, query: Union[str, list],
                    args: Optional[Union[list, List[list]]] = None,
                    return_type: ReturnType = ReturnType.NONE) -> Optional[tuple]:
        connection, cursor = self.get_connection()
        try:
            if isinstance(query, str):
                query = " ".join(list(filter(lambda x: x != '', query.replace('\n', '').split(" "))))
            else:
                query = map(lambda i: " ".join(list(filter(lambda x: x != '', i.replace('\n', '').split(" ")))), query)
            if isinstance(query, str):
                logger.trace(f"Executing SQL query: {query}")
                cursor.execute(query, args)
            else:
                for item, arg in zip(query, args):
                    logger.trace(f"Executing SQL query: {item}")
                    cursor.execute(item, arg)
            connection.commit()
            match return_type:
                case ReturnType.ALL:
                    return cursor.fetchall()
                case ReturnType.ONE:
                    return cursor.fetchone()
                case ReturnType.NONE:
                    return None
        except Exception as e:
            logger.error(e)
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    @logger.catch()
    def insert_message(self, message: MessageModel) -> None:
        sql, args = MessageModel.insert(message)
        self.run_command(sql, args, ReturnType.NONE)

    @logger.catch()
    def select_message(self, message_id: int) -> Message:
        pass

    @logger.catch()
    def delete_message(self, message_id: int) -> None:
        pass

    @logger.catch()
    def update_message(self, message_id: int, message: Message) -> None:
        pass
