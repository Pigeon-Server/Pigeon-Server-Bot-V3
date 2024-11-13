from peewee import CharField, CompositeKey, ForeignKeyField, IntegerField

from src.database.base_model import BaseModel


class McsmDaemon(BaseModel):
    id = IntegerField(unique=True)
    name = CharField()
    uuid = CharField()

    class Meta:
        table_name = 'mcsm_daemon'
        indexes = (
            (('id', 'uuid'), True),
        )
        primary_key = CompositeKey('id', 'uuid')

    def __str__(self):
        return f"Daemon-{self.id}: {self.name}({self.uuid})"


class McsmInstance(BaseModel):
    id = IntegerField()
    name = CharField()
    remote = ForeignKeyField(column_name='remote_id', field='id', model=McsmDaemon)
    status = IntegerField()
    uuid = CharField()

    class Meta:
        table_name = 'mcsm_instance'
        indexes = (
            (('id', 'uuid'), True),
            (('id', 'uuid'), True),
        )
        primary_key = CompositeKey('id', 'uuid')

    def __str__(self):
        return f"Instance-{self.id}: {self.name}({self.uuid}) -> {self.remote.name}({self.remote.uuid})"
