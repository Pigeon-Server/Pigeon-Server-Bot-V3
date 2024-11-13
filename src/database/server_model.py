from peewee import CharField, IntegerField, SQL

from src.database.base_model import BaseModel


class ServerList(BaseModel):
    enable = IntegerField(constraints=[SQL("DEFAULT 1")])
    priority = IntegerField(constraints=[SQL("DEFAULT 0")])
    server_ip = CharField()
    server_name = CharField()

    class Meta:
        table_name = 'server_list'
        indexes = (
            (('id', 'server_name'), True),
        )

    def __str__(self):
        return f"{self.server_name}({self.server_ip}): {'已启用' if self.enable else '未启用'} | {self.priority}"


class Whitelist(BaseModel):
    uuid = CharField(column_name='UUID', null=True)
    user = CharField(null=True)

    class Meta:
        table_name = 'whitelist'
        primary_key = False

    def __str__(self):
        return f"{self.user}[{self.uuid}]"
