from peewee import CharField, IntegerField, SQL, AutoField, BooleanField

from src.database.base_model import BaseModel


class ServerList(BaseModel):
    id = AutoField()
    server_name = CharField(max_length=80, unique=True)
    server_ip = CharField(max_length=80)
    priority = IntegerField(constraints=[SQL("DEFAULT 0")])
    enable = BooleanField(constraints=[SQL("DEFAULT 1")])

    class Meta:
        table_name = 'server_list'
        indexes = (
            (('id', 'server_name'), True),
        )

    def __str__(self):
        return f"{self.server_name}({self.server_ip}): {'已启用' if self.enable else '未启用'} | {self.priority}"


class Whitelist(BaseModel):
    uuid = CharField(max_length=100, column_name='UUID', null=True)
    user = CharField(max_length=100, null=True)

    class Meta:
        table_name = 'whitelist'
        primary_key = False

    def __str__(self):
        return f"{self.user}[{self.uuid}]"
