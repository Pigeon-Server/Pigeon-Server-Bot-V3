from peewee import CharField, CompositeKey, DateTimeField, IntegerField, SQL, TextField

from src.database.base_model import BaseModel


class Message(BaseModel):
    group_id = CharField()
    group_name = CharField()
    id = IntegerField()
    is_command = IntegerField(constraints=[SQL("DEFAULT 0")])
    message = TextField(null=True)
    message_id = CharField()
    send_time = DateTimeField()
    sender_id = CharField()
    sender_name = CharField()

    class Meta:
        table_name = 'message'
        indexes = (
            (('group_id', 'group_name'), False),
            (('id', 'message_id'), True),
            (('id', 'message_id'), True),
            (('sender_id', 'sender_name'), False),
        )
        primary_key = CompositeKey('id', 'message_id')

    def __str__(self):
        return f"[{self.send_time}] {self.group_name}({self.group_id})-{self.sender_name}({self.sender_id}):{self.message}"
    