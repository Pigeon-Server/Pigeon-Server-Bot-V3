from src.base.config import config
from src.bot.database import database
from src.module.mcsm.mcsm_class import McsmManager

mcsm: McsmManager

if config.sys_config.mcsm.use_database:
    mcsm = McsmManager(config.config.mcsm_config.api_key, config.config.mcsm_config.api_url,
                       use_database=True, database_instance=database)
else:
    mcsm = McsmManager(config.config.mcsm_config.api_key, config.config.mcsm_config.api_url)
