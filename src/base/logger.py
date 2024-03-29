# 日志模块
from datetime import datetime
from os import getcwd
from os.path import join

from loguru import logger

from src.utils.file_utils import check_directory

# 检查是否存在logs文件夹
check_directory(join(getcwd(), "logs"), True)
# 创建日志
# if not load(open(f"config/module.json5", "r", encoding="UTF-8", errors="ignore"))["debug_mode"]:
#     logger.remove()
#     logger.add(stderr, level="INFO")
logger.add(f"./logs/output_{datetime.strftime(datetime.now(), '%Y-%m-%d')}.log",
           format="[{time:MM-DD HH:mm:ss}] - {level}: {message}", rotation="00:00")
