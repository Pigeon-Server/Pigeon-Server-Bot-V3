from os import getcwd
from os.path import join
from time import sleep
from threading import Thread

from src.base.config import config
from src.base.logger import logger
from src.bot.mcsm import mcsm
from src.element.permissions import Root
from src.utils.file_utils import check_directory, text_to_image

image_dir = join(getcwd(), "image")
permission_image_dir = join(image_dir, "permissions.png")


def update_mcsm_info_thread_handler():
    while True:
        logger.trace("Update MCSM info")
        mcsm.update_instance_status()
        sleep(config.config.mcsm_config.update_time)


def permission_node_image():
    logger.debug(f"Generating thread started")
    check_directory(image_dir, True)
    text_to_image(Root.instance, permission_image_dir)
    logger.debug(f"Generating thread stop")


Thread(target=permission_node_image, daemon=True).start()

update_mcsm_info_thread = Thread(target=update_mcsm_info_thread_handler, daemon=True)
