from src.command.command_parser_manager import CommandParserManager
from src.command.mcsm_command import McsmCommand
from src.command.permission_command import PermissionCommand
from src.command.server_status_command import ServerStatusCommand

cp_manager = CommandParserManager()
permission_command = PermissionCommand()
server_status_command = ServerStatusCommand()
mcsm_command = McsmCommand()
cp_manager.add_command_parser(permission_command)
cp_manager.add_command_parser(server_status_command)
cp_manager.add_command_parser(mcsm_command)
