from src.base.config import config
from src.base.logger import logger
from src.command.command_parser_manager import CommandParserManager
from src.command.mcsm_command import McsmCommand
from src.command.other_command import OtherCommand
from src.command.permission_command import PermissionCommand
from src.command.server_list_command import ServerListCommand
from src.command.server_status_command import ServerStatusCommand
from src.module.mcsm.mcsm_class import McsmManager
from src.module.permission_manager import PermissionManager
from src.module.server_status import ServerStatus
from src.database.base_model import database
from src.database.server_model import ServerList, Whitelist
from src.database.message_model import Message
from src.database.mcsm_model import McsmDaemon, McsmInstance

logger.debug("Initializing permission manager...")
ps_manager = PermissionManager()
logger.debug("Permission manager initialized.")

logger.debug("Initializing CommandParserManager...")
cp_manager = CommandParserManager()
permission_command = PermissionCommand()
server_status_command = ServerStatusCommand()
mcsm_command = McsmCommand()
server_list_command = ServerListCommand()
other_cmd = OtherCommand()
logger.debug("Initializing CommandParser...")

logger.debug("Adding CommandParser...")
cp_manager.add_command_parser(permission_command)
cp_manager.add_command_parser(server_status_command)
cp_manager.add_command_parser(mcsm_command)
cp_manager.add_command_parser(server_list_command)
cp_manager.add_command_parser(other_cmd)
logger.debug("Finished Initializing CommandParserManager.")

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

mcsm = McsmManager(config.config.mcsm_config.api_key, config.config.mcsm_config.api_url,
                   use_database=config.sys_config.mcsm.use_database)
