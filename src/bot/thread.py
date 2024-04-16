from time import sleep
from threading import Thread

from src.base.config import config
from src.base.logger import logger
from src.bot.mcsm import mcsm


def update_mcsm_info_thread_handler():
    while True:
        logger.trace("Update MCSM info")
        mcsm.update_instance_status()
        sleep(config.config.mcsm_config.update_time)


update_mcsm_info_thread = Thread(target=update_mcsm_info_thread_handler, daemon=True)
