from re import Pattern, compile
from typing import Tuple

import pymysql
from pymysql import Connection, OperationalError
from pymysql.constants import CLIENT
from pymysql.cursors import Cursor
from dbutils.pooled_db import PooledDB

from src.base.config import config
from src.base.logger import logger
from src.model.message_model import MessageModel
from src.module.database.database_adapter import DatabaseAdapter
from src.type.config import Config
from src.type.types import DataEngineType, ReturnType

remove_space_pattern: Pattern = compile(r"\s{2,}")


class MysqlAdapter(DatabaseAdapter):
    _pool: PooledDB

    def __init__(self, db_config: Config.DatabaseConfig, query_log_limit: int = 2):
        super().__init__(query_log_limit)
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
            read_timeout=5,
            client_flag=CLIENT.MULTI_STATEMENTS
        )

    def database_init(self) -> None:
        try:
            self.run_command("""CREATE TABLE IF NOT EXISTS `message` (
                                    `id` int NOT NULL AUTO_INCREMENT,
                                    `message_id` char(128) NOT NULL,
                                    `sender_id` char(16) NOT NULL,
                                    `sender_name` varchar(255) NOT NULL,
                                    `group_id` char(16) NOT NULL,
                                    `group_name` varchar(255) NOT NULL,
                                    `is_command` tinyint(1) NOT NULL DEFAULT 0,
                                    `message` text NULL,
                                    `send_time` datetime NOT NULL,
                                    PRIMARY KEY (`id`, `message_id`),
                                    UNIQUE INDEX `index`(`id`, `message_id`) USING BTREE,
                                    INDEX `sender`(`sender_id`, `sender_name`) USING HASH,
                                    INDEX `group`(`group_id`, `group_name`) USING HASH);""")
            self.run_command("""CREATE TABLE IF NOT EXISTS `server_list` (
                                    `id` int NOT NULL AUTO_INCREMENT,
                                    `server_name` varchar(80) NOT NULL,
                                    `server_ip` varchar(80) NOT NULL,
                                    `priority` int NOT NULL DEFAULT 0,
                                    `enable` tinyint NOT NULL DEFAULT 1,
                                    PRIMARY KEY (`id`),
                                    UNIQUE INDEX `index`(`id`, `server_name`) USING HASH);""")
            if config.sys_config.mcsm.enable and config.sys_config.mcsm.use_database:
                logger.debug("MCSM module use database, init tables...")
                self.run_command("""CREATE TABLE IF NOT EXISTS `mcsm_daemon`  (
                                        `id` int NOT NULL AUTO_INCREMENT,
                                        `uuid` char(32) NOT NULL,
                                        `name` varchar(64) NOT NULL,
                                        PRIMARY KEY (`id`, `uuid`),
                                        UNIQUE INDEX `index`(`id`) USING HASH);""")
                self.run_command("""CREATE TABLE IF NOT EXISTS `mcsm_instance`  (
                                        `id` int NOT NULL AUTO_INCREMENT,
                                        `uuid` char(32) NOT NULL,
                                        `name` varchar(64) NOT NULL,
                                        `status` int NOT NULL,
                                        `remote_id` int NOT NULL,
                                        PRIMARY KEY (`id`, `uuid`),
                                        UNIQUE INDEX `index`(`id`, `uuid`) USING HASH,
                                        CONSTRAINT `daemon_id` FOREIGN KEY (`remote_id`) 
                                        REFERENCES `mcsm_daemon` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT);""")
            logger.trace("Checking event scheduler...")
            res = self.run_command("""SHOW VARIABLES LIKE 'event_scheduler';""", return_type=ReturnType.ONE)
            if res[1] == "OFF":
                logger.warning("Event scheduler disable, try to enable it.")
                try:
                    self.run_command("""set global event_scheduler = on;""")
                    logger.success("Event scheduler enabled.")
                except OperationalError as e:
                    logger.error(e)
                    logger.error(f"Unable to set global event scheduler on database, please enable event scheduler")
                    exit(1)
            logger.trace("Create event scheduler...")
            self.run_command("""CREATE EVENT IF NOT EXISTS `delete_expired_messages` 
                                    ON SCHEDULE
                                    EVERY '1' DAY
                                    DO DELETE FROM `message` 
                                    WHERE TIMESTAMPDIFF(DAY, send_time, NOW()) > 15;""")
            logger.trace("Event scheduler created.")
        except Exception as e:
            logger.error(e)
            logger.error(f"Database init error")
            exit(1)

    def get_connection(self) -> Tuple[Connection, Cursor]:
        connection = self._pool.connection()
        return connection, connection.cursor()

    def get_database_type(self) -> DataEngineType:
        return DataEngineType.MYSQL

    @logger.catch()
    def insert_message(self, message: MessageModel) -> None:
        sql, args = MessageModel.insert(message)
        self.run_command(sql, args, ReturnType.NONE)
