from src.base.config import config
from src.module.mcsm.mcsm_class import McsmManager

mcsm = McsmManager(config.config.mcsm_config.api_key, config.config.mcsm_config.api_url,
                   use_database=config.sys_config.mcsm.use_database)
