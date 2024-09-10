from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

from src.base.logger import logger
from src.type.types import Connection, Cursor, DataEngineType, ReturnType


class DatabaseAdapter(ABC):
    _query_log_limit: int

    def __init__(self, query_log_limit: int = 2) -> None:
        self._query_log_limit = query_log_limit

    @abstractmethod
    def get_connection(self) -> Tuple[Connection, Cursor]:
        raise NotImplementedError

    @abstractmethod
    def database_init(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_database_type(self) -> DataEngineType:
        raise NotImplementedError

    def run_command(self, query: Union[str, list],
                    args: Optional[Union[list, List[list]]] = None,
                    return_type: ReturnType = ReturnType.NONE,
                    ignore_query_limit: bool = False) -> Optional[Union[tuple, int]]:
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
                arg_len = len(args)
                for item, arg in zip(query, args):
                    if ignore_query_limit or arg_len < self._query_log_limit:
                        logger.trace(f"Executing SQL query: {item}")
                    cursor.execute(item, arg)
            connection.commit()
            match return_type:
                case ReturnType.ALL:
                    return cursor.fetchall()
                case ReturnType.ONE:
                    return cursor.fetchone()
                case ReturnType.CURSOR_ID:
                    return cursor.lastrowid
                case ReturnType.NONE:
                    return None
        except Exception as e:
            logger.error(e)
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
