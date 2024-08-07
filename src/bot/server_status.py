from src.base.logger import logger
from src.module.server_status import ServerStatus

logger.debug("Initializing ServerStatus...")

server = ServerStatus()

logger.debug("ServerStatus initialized")
