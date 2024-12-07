from contextlib import contextmanager

from peewee import Database, Model
from playhouse.pool import PooledMySQLDatabase, PooledPostgresqlDatabase, PooledSqliteDatabase

from src.base.config import main_config
from src.base.logger import logger
from src.utils.life_cycle_manager import LifeCycleEvent, LifeCycleManager

database: Database

match main_config.database.type.lower():
    case 'mysql':
        database = PooledMySQLDatabase(database=main_config.database.database_name,
                                       host=main_config.database.host,
                                       port=main_config.database.port,
                                       user=main_config.database.username,
                                       password=main_config.database.password,
                                       max_connections=64,
                                       stale_timeout=300)
    case 'sqlite':
        database = PooledSqliteDatabase(database=main_config.database.database_name,
                                        max_connections=64,
                                        stale_timeout=300)
    case 'postgresql':
        database = PooledPostgresqlDatabase(database=main_config.database.database_name,
                                            host=main_config.database.host,
                                            port=main_config.database.port,
                                            user=main_config.database.username,
                                            password=main_config.database.password,
                                            max_connections=64,
                                            stale_timeout=300)
    case _:
        logger.critical(f'Database type {main_config.database.type} not supported')

LifeCycleManager.add_life_cycle_event(LifeCycleEvent.STOPPING, lambda: database.close())


class BaseModel(Model):
    class Meta:
        database = database


@contextmanager
def transaction_manager():
    transaction = database.atomic()
    try:
        with transaction:
            yield
    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        raise


def database_transaction(func):
    def wrapper(*args, **kwargs):
        with transaction_manager():
            return func(*args, **kwargs)

    return wrapper
