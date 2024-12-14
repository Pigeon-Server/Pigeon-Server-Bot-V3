from peewee import AutoField, CharField, CompositeKey, ForeignKeyField, IntegerField

from src.database.base_model import BaseModel


class McsmDaemon(BaseModel):
    id = AutoField()
    uuid = CharField(max_length=32, unique=True)
    name = CharField(max_length=64)

    class Meta:
        table_name = 'mcsm_daemon'

    def __str__(self):
        return f"Daemon-{self.id}: {self.name}({self.uuid})"


class McsmInstance(BaseModel):
    id = AutoField()
    uuid = CharField(max_length=32, unique=True)
    name = CharField(max_length=64)
    status = IntegerField()
    remote = ForeignKeyField(column_name='remote_id', field='id', model=McsmDaemon)

    class Meta:
        table_name = 'mcsm_instance'

    def __str__(self):
        return f"Instance-{self.id}: {self.name}({self.uuid}) -> {self.remote.name}({self.remote.uuid})"
