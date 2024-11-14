from contextlib import contextmanager

from peewee import Database, Model, MySQLDatabase, PostgresqlDatabase, SqliteDatabase

from src.base.config import main_config
from src.base.logger import logger
from src.utils.life_cycle_manager import LifeCycleEvent, LifeCycleManager

database: Database

match main_config.database.type.lower():
    case 'mysql':
        database = MySQLDatabase(database=main_config.database.database_name, host=main_config.database.host,
                                 port=main_config.database.port, user=main_config.database.username,
                                 password=main_config.database.password)
    case 'sqlite':
        database = SqliteDatabase(database=main_config.database.database_name)
    case 'postgresql':
        database = PostgresqlDatabase(database=main_config.database.database_name, host=main_config.database.host,
                                      port=main_config.database.port, user=main_config.database.username,
                                      password=main_config.database.password)
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
