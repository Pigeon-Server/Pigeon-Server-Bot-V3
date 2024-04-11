from src.base.config import config
from src.command.command_parser_manager import CommandParserManager
from src.module.permission_manager import PermissionManager
from src.module.server_status import ServerStatus
from src.command.permission_command import PermissionCommand
from src.command.server_status_command import ServerStatusCommand

ps_manager = PermissionManager()
server = ServerStatus(config.config.server_list)
cp_manager = CommandParserManager()
permission_command = PermissionCommand()
server_status_command = ServerStatusCommand()
cp_manager.add_command_parser(permission_command)
cp_manager.add_command_parser(server_status_command)
