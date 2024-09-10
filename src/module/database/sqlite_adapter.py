from sqlite3 import connect
from typing import List, Optional, Tuple, Union

from src.base.logger import logger
from src.module.database.database_adapter import DatabaseAdapter
from src.type.config import Config
from src.type.types import Connection, Cursor, DataEngineType, ReturnType


class SQLiteAdapter(DatabaseAdapter):
    _connection: Optional[Connection] = None
    _config: Config.DatabaseConfig

    def __init__(self, db_config: Config.DatabaseConfig, query_log_limit: int = 2):
        super().__init__(query_log_limit)
        self._config = db_config

    def _connect(self):
        self._connection = connect(database=self._config.host)

    def database_init(self) -> None:
        self.run_command(["""CREATE TABLE IF NOT EXISTS "main"."message" (
                              "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                              "message_id" char(128) NOT NULL,
                              "sender_id" char(16) NOT NULL,
                              "sender_name" varchar(255) NOT NULL,
                              "group_id" char(16),
                              "group_name" varchar(255) NOT NULL,
                              "is_command" integer NOT NULL DEFAULT 0,
                              "message" text,
                              "send_time" datetime NOT NULL
                            );""",
                          """CREATE UNIQUE INDEX IF NOT EXISTS "main"."message_index" 
                                ON "message" ("id", "message_id");""",
                          """CREATE INDEX IF NOT EXISTS "main"."message_sender" 
                                ON "message" ("sender_id", "sender_name");""",
                          """CREATE INDEX IF NOT EXISTS "main"."message_group" 
                                ON "message" ("group_id", "group_name");"""])
        self.run_command(["""CREATE TABLE IF NOT EXISTS "main"."server_list" (
                              "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                              "server_name" varchar(80) NOT NULL,
                              "server_ip" varchar(80) NOT NULL,
                              "priority" integer NOT NULL DEFAULT 0,
                              "enable" tinyint NOT NULL DEFAULT 1
                            );""",
                          """CREATE UNIQUE INDEX IF NOT EXISTS "main"."server_list_index" ON "server_list" ("id");"""])
        self.run_command(["""CREATE TABLE IF NOT EXISTS "main"."mcsm_daemon" (
                              "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                              "uuid" char(32) NOT NULL,
                              "name" varchar(64) NOT NULL
                            );""",
                          """CREATE UNIQUE INDEX IF NOT EXISTS "main"."mcsm_daemon_index" 
                                ON "mcsm_daemon" ("id", "uuid");"""])
        self.run_command(["""CREATE TABLE IF NOT EXISTS "main"."mcsm_instance" (
                              "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                              "uuid" char(32) NOT NULL,
                              "name" varchar(64) NOT NULL,
                              "status" tinyint NOT NULL,
                              "remote_id" integer NOT NULL,
                              CONSTRAINT "daemon_id" FOREIGN KEY ("remote_id")
                                REFERENCES "mcsm_daemon" ("id") ON DELETE RESTRICT ON UPDATE RESTRICT
                            );""",
                          """CREATE UNIQUE INDEX IF NOT EXISTS "main"."mcsm_instance_index" 
                                ON "mcsm_instance" ("id",  "uuid");"""])
        self.run_command("""CREATE TRIGGER IF NOT EXISTS "main"."delete_expired_messages"
                                AFTER INSERT ON "message"
                                BEGIN
                                    DELETE FROM message WHERE JULIANDAY(DATE())-JULIANDAY(send_time) > 15;
                                END;""")

    def get_connection(self) -> Tuple[Connection, Cursor]:
        self._connect()
        return self._connection, self._connection.cursor()

    def get_database_type(self) -> DataEngineType:
        return DataEngineType.SQLITE

    def run_command(self, query: Union[str, list],
                    args: Optional[Union[tuple, List[tuple]]] = None,
                    return_type: ReturnType = ReturnType.NONE,
                    ignore_query_limit: bool = False) -> Optional[list]:
        connection, cursor = self.get_connection()
        try:
            if isinstance(query, str):
                query = " ".join(list(filter(lambda x: x != '', query.replace('\n', '').split(" "))))
            else:
                query = map(lambda i: " ".join(list(filter(lambda x: x != '', i.replace('\n', '').split(" ")))), query)
            if isinstance(query, str):
                if args is None:
                    args = tuple()
                logger.trace(f"Executing SQL query: {query}")
                cursor.execute(query, args)
            else:
                if args is None:
                    for item in query:
                        logger.trace(f"Executing SQL query: {item}")
                        cursor.execute(item, tuple())
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
                case ReturnType.CURSOR_ID:
                    return cursor.lastrowid
                case ReturnType.NONE:
                    return None
        except Exception as e:
            logger.error(e)
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()
