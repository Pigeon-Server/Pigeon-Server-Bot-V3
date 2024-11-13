from contextlib import contextmanager

from peewee import Database, Model, MySQLDatabase, PostgresqlDatabase, SqliteDatabase

from src.base.logger import logger
from src.base.config import config

database: Database

match config.config.database.type.lower():
    case 'mysql':
        database = MySQLDatabase(database=config.config.database.database_name, host=config.config.database.host,
                                 port=config.config.database.port, user=config.config.database.username,
                                 password=config.config.database.password)
    case 'sqlite':
        database = SqliteDatabase(database=config.config.database.database_name)
    case 'postgresql':
        database = PostgresqlDatabase(database=config.config.database.database_name, host=config.config.database.host,
                                      port=config.config.database.port, user=config.config.database.username,
                                      password=config.config.database.password)
    case _:
        logger.critical(f'Database type {config.config.database.type} not supported')


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
