from peewee import AutoField, CharField, IntegerField, BooleanField, DateTimeField

from src.database.base_model import BaseModel
from src.element.message import Message


class Punishment(BaseModel):
    id = AutoField()
    user_id = CharField(max_length=16, unique=True)
    user_name = CharField(max_length=16)
    punish_level = IntegerField(default=0)
    under_punishment = BooleanField(default=False)
    punishment_end_date = DateTimeField(null=True)

    class Meta:
        table_name = 'punishments'

    def __str__(self):
        return (f"{self.user_name}({self.user_id})：\n"
                f"禁言中：{'是' if self.under_punishment else '否'}\n"
                f"累积处罚等级：{self.punish_level}"
                f"{f'\n解禁时间：{self.punishment_end_date}' if self.under_punishment else ''}")

    @classmethod
    def get_or_create(cls, message: Message) -> 'Punishment':
        punishment = cls.select().where(cls.user_id == message.sender_id).execute()
        if len(punishment) > 0:
            return punishment[0]
        return cls.create(user_id=message.sender_id, user_name=message.sender_name)
