from asyncio import sleep

from pymysql import Connection, connect
from pymysql.cursors import Cursor

from src.base.logger import logger
from src.type.config import Config


class Database:
    _name: str
    _host: str
    _port: int
    _username: str
    _password: str
    _autocommit: bool
    _connection: Connection
    _cursor: Cursor

    def __init__(self, config: Config.DatabaseConfig, auto_connect: bool = True):
        self._name = config.database_name
        self._host = config.host
        self._port = config.port
        self._username = config.username
        self._password = config.password
        self._autocommit = config.auto_commit
        if auto_connect:
            self.connect()

    def _database_ping_thread_handler(self):
        while True:
            logger.trace("Ping Database")
            self.ping_database()
            sleep(1)

    def ping_database(self) -> None:
        self._connection.ping(True)

    def connect(self) -> None:
        self._connection = connect(
            host=self._host,
            port=self._port,
            user=self._username,
            password=self._password,
            database=self._name,
            autocommit=self._autocommit,
            connect_timeout=5,
            write_timeout=5,
            read_timeout=5,
        )
        try:
            self._cursor = self._connection.cursor()
            self._cursor.execute("SELECT VERSION()")
            data = self._cursor.fetchone()
            logger.success("Connect to database successfully")
            logger.debug(f"Database version: {data}")
            self._connection.commit()
        except Exception as e:
            logger.critical(e)

    def disconnect(self) -> None:
        if self._connection:
            self._connection.commit()
            self._connection.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def run_sql_query(self, query: str) -> tuple:
        self._cursor.execute(query)
        return self._cursor.fetchall()
