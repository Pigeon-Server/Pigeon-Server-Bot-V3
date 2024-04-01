from src.base.config import config
from src.module.permission_node import PermissionManager
from src.module.server_status import ServerStatus

per = PermissionManager()
server = ServerStatus(config.config.server_list)
