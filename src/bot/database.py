from src.base.logger import logger
from src.database.base_model import database
from src.database.server_model import ServerList, Whitelist
from src.database.message_model import Message
from src.database.mcsm_model import McsmDaemon, McsmInstance

try:
    logger.debug("Database is initializing...")
    database.create_tables([ServerList, Whitelist, Message, McsmDaemon, McsmInstance])
    logger.success("Database initialized")
except ValueError as e:
    logger.error(e)
    logger.error(f"Database type error, supported type is: sqlite, mysql, postgresql")
    exit(1)
except Exception as e:
    logger.error(e)
    logger.error(f"Database init error")
    exit(1)
