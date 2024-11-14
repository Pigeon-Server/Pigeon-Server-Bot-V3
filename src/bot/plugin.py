from src.base.config import main_config, sys_config
from src.base.logger import logger
from src.module.mcsm.mcsm_class import McsmManager
from src.module.permission_manager import PermissionManager
from src.module.server_status import ServerStatus
from src.database.base_model import database
from src.database.server_model import ServerList, Whitelist
from src.database.message_model import Message
from src.database.mcsm_model import McsmDaemon, McsmInstance
from src.utils.life_cycle_manager import LifeCycleEvent, LifeCycleManager

LifeCycleManager.emit_life_cycle_event(LifeCycleEvent.INITIAL)

logger.debug("Initializing permission manager...")
ps_manager = PermissionManager()
logger.debug("Permission manager initialized.")

try:
    logger.debug("Database is initializing...")
    database.create_tables([ServerList, Whitelist, Message, McsmDaemon, McsmInstance])
    logger.success("Database initialized")
except Exception as e:
    logger.error(e)
    logger.error(f"Database init error")
    exit(1)

logger.debug("Initializing ServerStatus...")
server = ServerStatus()
logger.debug("ServerStatus initialized")

mcsm = McsmManager(main_config.mcsm_config.api_key, main_config.mcsm_config.api_url,
                   use_database=sys_config.mcsm.use_database)
