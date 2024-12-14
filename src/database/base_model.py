from contextlib import contextmanager

from peewee import Database, Model

from src.base.config import main_config
from src.base.event_bus import event_bus
from src.base.logger import logger
from src.bus.event.event import ServerEvent
from src.database.database import ReconnectPooledMySQLDatabase, ReconnectPooledPostgresqlDatabase, \
    ReconnectPooledSqliteDatabase

database: Database

match main_config.database.type.lower():
    case 'mysql':
        database = ReconnectPooledMySQLDatabase.get_instance(database=main_config.database.database_name,
                                                             host=main_config.database.host,
                                                             port=main_config.database.port,
                                                             user=main_config.database.username,
                                                             password=main_config.database.password,
                                                             timeout=7200,
                                                             max_connections=64,
                                                             stale_timeout=300)
    case 'sqlite':
        database = ReconnectPooledSqliteDatabase.get_instance(database=main_config.database.database_name,
                                                              timeout=7200,
                                                              max_connections=64,
                                                              stale_timeout=300)
    case 'postgresql':
        database = ReconnectPooledPostgresqlDatabase.get_instance(database=main_config.database.database_name,
                                                                  host=main_config.database.host,
                                                                  port=main_config.database.port,
                                                                  user=main_config.database.username,
                                                                  password=main_config.database.password,
                                                                  timeout=7200,
                                                                  max_connections=64,
                                                                  stale_timeout=300)
    case _:
        logger.critical(f'Database type {main_config.database.type} not supported')

event_bus.subscribe(ServerEvent.STOPPING, lambda: database.close())


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
