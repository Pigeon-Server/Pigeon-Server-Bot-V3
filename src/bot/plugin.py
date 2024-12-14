from peewee import OperationalError

from src.base.config import main_config, sys_config
from src.base.event_bus import event_bus
from src.base.logger import logger
from src.bus.event.event import ServerEvent
from src.database.base_model import database
from src.database.mcsm_model import McsmDaemon, McsmInstance
from src.database.message_model import BlockWord, Message
from src.database.server_model import ServerList, Whitelist
from src.module.mcsm.mcsm_class import McsmManager
from src.module.permission_manager import PermissionManager
from src.utils.permission_helper import PermissionHelper

event_bus.publish_sync(ServerEvent.INITIAL)

logger.debug("Initializing permission manager...")
PermissionHelper.init_permission_helper(PermissionManager())
logger.debug("Permission manager initialized.")

try:
    logger.debug("Database is initializing...")
    database.create_tables([ServerList, Whitelist, Message, McsmDaemon, McsmInstance, BlockWord])
    logger.success("Database initialized")
except OperationalError as e:
    logger.error(e)
    logger.critical(f"Database init error")

mcsm = McsmManager(main_config.mcsm_config.api_key, main_config.mcsm_config.api_url,
                   use_database=sys_config.mcsm.use_database)
