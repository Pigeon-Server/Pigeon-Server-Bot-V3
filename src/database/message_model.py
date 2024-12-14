from peewee import AutoField, CharField, CompositeKey, DateTimeField, IntegerField, SQL, TextField, BooleanField

from src.database.base_model import BaseModel


class Message(BaseModel):
    id = AutoField()
    message_id = CharField(max_length=128, unique=True)
    sender_id = CharField(max_length=16)
    sender_name = CharField()
    group_id = CharField(max_length=16)
    group_name = CharField()
    is_command = BooleanField(constraints=[SQL("DEFAULT 0")])
    message = TextField(null=True)
    send_time = DateTimeField()

    class Meta:
        table_name = 'message_record'
        indexes = (
            (('group_id', 'group_name'), False),
            (('sender_id', 'sender_name'), False),
        )

    def __str__(self):
        return f"[{self.send_time}] {self.group_name}({self.group_id})-{self.sender_name}({self.sender_id}):{self.message}"


class BlockWord(BaseModel):
    id = AutoField()
    group_id = CharField(max_length=16)
    block_word = CharField()
    punish_level = IntegerField(constraints=[SQL("DEFAULT 1")])

    class Meta:
        table_name = 'block_words'
