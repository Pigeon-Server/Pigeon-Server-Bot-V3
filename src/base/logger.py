# 日志模块
from datetime import datetime
from os import getcwd
from os.path import join
from sys import stdout

from loguru import logger

from src.base.config import config
from src.utils.file_utils import check_directory

# 检查是否存在logs文件夹
check_directory(join(getcwd(), "logs"), True)

log_format = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> <light-red>|</> "
              "<yellow>{thread:<5}</> <light-red>|</> "
              "<magenta>{elapsed}</> <light-red>|</> "
              "<level>{level:8}</> <light-red>|</> "
              "<cyan>{name}<light-red>:</>{function}<light-red>:</>{line}</> "
              "<light-red>-</> <level>{message}</>")

logger.debug(f"Change logger level to {config.sys_config.log_level.upper()}")
logger.remove()
logger.add(stdout,
           format=log_format,
           level=config.sys_config.log_level.upper())
logger.add(join(getcwd(), f"./logs/output_{datetime.strftime(datetime.now(), '%Y-%m-%d')}.log"),
           format=log_format, rotation="00:00", compression="zip",
           level=config.sys_config.log_level.upper())
if config.sys_config.log_level.upper() != "TRACE":
    logger.add(join(getcwd(), f"./logs/output_{datetime.strftime(datetime.now(), '%Y-%m-%d')}-full.log"),
               format=log_format, rotation="00:00", compression="zip",
               level="TRACE")
logger.add(lambda _: exit(-1), level="CRITICAL")
