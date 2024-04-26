from src.base.config import config
from src.module.database import Database
from src.type.types import ReturnType

database = Database(config.config.database)

database.run_command("""CREATE TABLE IF NOT EXISTS `message`  (
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

database.run_command("""set global event_scheduler = on;""")

database.run_command("""CREATE EVENT IF NOT EXISTS `delete_expired_messages` 
                        ON SCHEDULE
                        EVERY '1' DAY
                        DO DELETE FROM `message` 
                        WHERE TIMESTAMPDIFF(DAY, send_time, NOW()) > 15;""")
