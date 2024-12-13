from playhouse.pool import PooledMySQLDatabase, PooledPostgresqlDatabase, PooledSqliteDatabase
from playhouse.shortcuts import ReconnectMixin


class ReconnectPooledMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    _instance = None

    @classmethod
    def get_instance(cls, **db_config):
        if not cls._instance:
            cls._instance = cls(**db_config)
        return cls._instance


class ReconnectPooledSqliteDatabase(ReconnectMixin, PooledSqliteDatabase):
    _instance = None

    @classmethod
    def get_instance(cls, **db_config):
        if not cls._instance:
            cls._instance = cls(**db_config)
        return cls._instance


class ReconnectPooledPostgresqlDatabase(ReconnectMixin, PooledPostgresqlDatabase):
    _instance = None

    @classmethod
    def get_instance(cls, **db_config):
        if not cls._instance:
            cls._instance = cls(**db_config)
        return cls._instance
