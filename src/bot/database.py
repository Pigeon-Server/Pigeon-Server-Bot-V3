from src.base.logger import logger
from src.base.config import config
from src.module.database.database_adapter import DatabaseAdapter
from src.module.database.postgresql_adapter import PostgreSQLAdapter
from src.module.database.sqlite_adapter import SQLiteAdapter
from src.module.database.mysql_adapter import MysqlAdapter
from src.type.types import DataEngineType

try:
    logger.debug("Database is initializing...")
    database: DatabaseAdapter
    match DataEngineType(config.config.database.type.lower()):
        case DataEngineType.SQLITE:
            database = SQLiteAdapter(config.config.database)
        case DataEngineType.POSTGRESQL:
            database = PostgreSQLAdapter(config.config.database)
        case DataEngineType.MYSQL:
            database = MysqlAdapter(config.config.database)
    logger.debug("Database connection established.")
    database.database_init()
    logger.success("Database initialized")
except ValueError as e:
    logger.error(e)
    logger.error(f"Database type error, supported type is: sqlite, mysql, postgresql")
    exit(1)
except Exception as e:
    logger.error(e)
    logger.error(f"Database init error")
    exit(1)

