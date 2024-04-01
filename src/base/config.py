from json import load as js_load
from os import getcwd
from os.path import join
from typing import Optional

from json5.lib import load as js5_load

from src.base.logger import logger
from src.type.Config import Config
from src.type.SysConfig import SysConfig
from src.utils.file_utils import check_file


class ConfigSet:
    _config: Config
    _sys_config: SysConfig

    @staticmethod
    def load_config(filename: str) -> Optional[dict]:
        def read_config() -> Optional[dict]:
            try:
                with open(filename, "r", encoding="utf-8") as _f:
                    if filename.endswith(".json"):
                        return js_load(_f)
                    return js5_load(_f)
            except Exception as e:
                logger.error(e)
                logger.error(f"{filename}已损坏,请检查")
                return None

        default_file = join(getcwd(), "config\\default", filename)
        filename = join(getcwd(), "config", filename)
        if check_file(filename):
            return read_config()
        if check_file(default_file):
            with open(filename, "w", encoding="utf-8") as f:
                with open(default_file, "r", encoding="utf-8") as fd:
                    f.write(fd.read())
            return read_config()
        logger.error(f"{default_file}文件不存在,请前往Github下载")
        return None

    def __init__(self):
        self.reload_config()

    def __repr__(self):
        return f"ConfigSet({self._config}, {self._sys_config})"

    def reload_config(self):
        self._config = Config(self.load_config("config.json5"))
        self._sys_config = SysConfig(self.load_config("system_config.json5"))

    @property
    def config(self) -> Config:
        return self._config

    @property
    def sys_config(self) -> SysConfig:
        return self._sys_config


config = ConfigSet()
