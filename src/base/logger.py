# 日志模块
import logging
from datetime import datetime
from os import getcwd
from os.path import join
from sys import stdout

from loguru import logger

from src.base.config import sys_config
from src.utils.file_utils import check_directory


def log_filter(record: dict) -> bool:
    return not (record.get("name") == "satori.client.network.websocket" and record.get("function") == "message_receive")


# 检查是否存在logs文件夹
check_directory(join(getcwd(), "logs"), create_if_not_exist=True)

log_format = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> <light-red>|</> "
              "<yellow>{thread:<5}</> <light-red>|</> "
              "<magenta>{elapsed}</> <light-red>|</> "
              "<level>{level:8}</> <light-red>|</> "
              "<cyan>{name}<light-red>:</>{function}<light-red>:</>{line}</> "
              "<light-red>-</> <level>{message}</>")
logger.debug(f"Change logger level to {sys_config.log_level.upper()}")
logger.remove()
logger.add(stdout,
           format=log_format,
           level=sys_config.log_level.upper(),
           filter=log_filter)
logger.add(join(getcwd(), f"./logs/output_{datetime.strftime(datetime.now(), '%Y-%m-%d')}.log"),
           format=log_format, rotation="00:00", compression="zip",
           level=sys_config.log_level.upper(),
           filter=log_filter)
if sys_config.log_level.upper() != "TRACE":
    logger.add(join(getcwd(), f"./logs/output_{datetime.strftime(datetime.now(), '%Y-%m-%d')}-full.log"),
               format=log_format, rotation="00:00", compression="zip",
               level="TRACE",
               filter=log_filter)
logger.add(lambda _: exit(-1), level="CRITICAL")


class LogHandler(logging.Handler):
    def emit(self, record):
        logger.log(record.levelname, record.getMessage())


logging.basicConfig(
    level=logging.DEBUG if sys_config.log_level.upper() == "TRACE" else sys_config.log_level.upper(),
    handlers=[])
logging.getLogger().addHandler(LogHandler())
