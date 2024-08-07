from src.base.logger import logger
from src.command.command_parser_manager import CommandParserManager
from src.command.mcsm_command import McsmCommand
from src.command.other_command import OtherCommand
from src.command.permission_command import PermissionCommand
from src.command.server_list_command import ServerListCommand
from src.command.server_status_command import ServerStatusCommand

logger.debug("Initializing CommandParserManager...")

cp_manager = CommandParserManager()

logger.debug("Initializing CommandParser...")

permission_command = PermissionCommand()
server_status_command = ServerStatusCommand()
mcsm_command = McsmCommand()
server_list_command = ServerListCommand()
other_cmd = OtherCommand()

logger.debug("Adding CommandParser...")

cp_manager.add_command_parser(permission_command)
cp_manager.add_command_parser(server_status_command)
cp_manager.add_command_parser(mcsm_command)
cp_manager.add_command_parser(server_list_command)
cp_manager.add_command_parser(other_cmd)

logger.debug("Finished Initializing CommandParserManager.")
