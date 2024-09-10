from typing import List, Optional, Tuple, Union

import psycopg2
from psycopg2.extensions import connection as Connection, cursor as Cursor
from dbutils.pooled_db import PooledDB

from src.base.logger import logger
from src.module.database.database_adapter import DatabaseAdapter
from src.type.config import Config
from src.type.types import DataEngineType


class PostgreSQLAdapter(DatabaseAdapter):
    _pool: PooledDB

    def __init__(self, db_config: Config.DatabaseConfig, query_log_limit: int = 2):
        super().__init__(query_log_limit)
        self._pool = PooledDB(
            creator=psycopg2,
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

    def database_init(self) -> None:
        pass

    def get_database_type(self) -> DataEngineType:
        return DataEngineType.POSTGRESQL

    def get_connection(self) -> Tuple[Connection, Cursor]:
        connection = self._pool.connection()
        return connection, connection.cursor()
