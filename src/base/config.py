from os import getcwd
from os.path import join
from typing import Optional

from loguru import logger

from src.type.config import Config as MainConfig
from src.type.sys_config import SysConfig
from src.type.types import VersionType
from src.utils.file_utils import check_file
from src.utils.version import Version
from src.utils.json_utils import read_json


class Config:
    _config_version: Version = Version([1, 2, 0])
    _main_config: Optional[MainConfig] = None
    _sys_config: Optional[SysConfig] = None

    @staticmethod
    def load_config(filename: str) -> Optional[dict]:
        default_file = join(getcwd(), "config\\default", filename)
        filename = join(getcwd(), "config", filename)
        if check_file(filename):
            return read_json(filename)
        if check_file(default_file):
            with open(filename, "w", encoding="utf-8") as f:
                with open(default_file, "r", encoding="utf-8") as fd:
                    f.write(fd.read())
            return read_json(filename)
        logger.error(f"{default_file}文件不存在,请前往Github下载")
        return None

    @staticmethod
    def reload_config():
        Config._main_config = MainConfig(Config.load_config("config.json5"))
        logger.debug(f"Config version: {Config._main_config.config_version}")
        version = Version(Config._main_config.config_version)
        res = Config._config_version.check_version(version)
        if res == VersionType.MAJOR_UNMATCH or res == VersionType.MINOR_UNMATCH:
            logger.critical(
                f"Config version error! Require {Config._config_version} but got {version}")
            exit(-1)
        if res == VersionType.PATCH_UNMATCH:
            logger.warning(
                f"Config version not match! Require {Config._config_version} but got {version}")
        Config._sys_config = SysConfig(Config.load_config("system_config.json5"))
        if Config._sys_config.mcsm.use_database and Config._main_config.mcsm_config.update_time < 600:
            Config._main_config.mcsm_config.update_time = 600

    @staticmethod
    def main_config() -> MainConfig:
        if Config._main_config is None:
            Config.reload_config()
        return Config._main_config

    @staticmethod
    def sys_config() -> SysConfig:
        if Config._sys_config is None:
            Config.reload_config()
        return Config._sys_config


main_config = Config.main_config()
sys_config = Config.sys_config()
