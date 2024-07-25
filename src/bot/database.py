from pymysql import OperationalError

from src.base.logger import logger
from src.base.config import config
from src.module.database import Database
from src.type.types import ReturnType

try:
    logger.debug("Database is initializing...")
    database = Database(config.config.database)
    logger.debug("Database connection established.")
    database.run_command("""CREATE TABLE IF NOT EXISTS `message` (
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
    database.run_command("""CREATE TABLE  IF NOT EXISTS `server_list` (
                          `id` int NOT NULL AUTO_INCREMENT,
                          `server_name` varchar(80) NOT NULL,
                          `server_ip` varchar(80) NOT NULL,
                          `enable` tinyint NOT NULL DEFAULT 1,
                          PRIMARY KEY (`id`));""")
    logger.trace("Checking event scheduler...")
    res = database.run_command("""SHOW VARIABLES LIKE 'event_scheduler';""", return_type=ReturnType.ONE)
    if res[1] == "OFF":
        logger.warning("Event scheduler disable, try to enable it.")
        try:
            database.run_command("""set global event_scheduler = on;""")
            logger.success("Event scheduler enabled.")
        except OperationalError as e:
            logger.error(e)
            logger.error(f"Unable to set global event scheduler on database, please enable event scheduler")
            exit(1)
    logger.trace("Create event scheduler...")
    database.run_command("""CREATE EVENT IF NOT EXISTS `delete_expired_messages` 
                        ON SCHEDULE
                        EVERY '1' DAY
                        DO DELETE FROM `message` 
                        WHERE TIMESTAMPDIFF(DAY, send_time, NOW()) > 15;""")
    logger.trace("Event scheduler created.")
    logger.success("Database initialized")
except Exception as e:
    logger.error(e)
    logger.error(f"Database init error")
    exit(1)
