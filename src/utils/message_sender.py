from typing import List, Optional, Union, overload

from satori import At, Element, Event, Guild, MessageObject, Quote
from satori.client import Account

from src.base.config import sys_config
from src.base.logger import logger
from src.element.message import Message
from src.type.types import MessageType


class MessageSender:
    _account: Optional[Account] = None

    @staticmethod
    def set_account(account: Account) -> None:
        MessageSender._account = account

    @staticmethod
    @overload
    async def send_message(channel_id: str, message: str) -> List[MessageObject]:
        ...

    @staticmethod
    @overload
    async def send_message(channel_id: str, message: list[str | Element]) -> List[MessageObject]:
        ...

    @staticmethod
    @overload
    async def send_message(channel_id: Event, message: str) -> List[MessageObject]:
        ...

    @staticmethod
    @overload
    async def send_message(channel_id: Event, message: list[str | Element]) -> List[MessageObject]:
        ...

    @staticmethod
    async def send_message(channel_id: Union[str, Event],
                           message: MessageType) -> List[MessageObject]:
        if MessageSender._account is None:
            raise ValueError("Account is not set")
        if sys_config.dev:
            if isinstance(message, str):
                message = f"{'-' * 5}Dev{'-' * 5}\n{message}"
            if isinstance(message, list):
                message = [f"{'-' * 5}Dev{'-' * 5}\n"] + message
        log_message = Message.parse(message)
        if isinstance(channel_id, str):
            channel: Guild = await MessageSender._account.guild_get(guild_id=channel_id)
            logger.info(f'[消息]->{channel.name}({channel.id}): {log_message}')
            return await MessageSender._account.send_message(channel_id, message)
        if isinstance(channel_id, Event):
            logger.info(f'[消息]->{channel_id.guild.name}({channel_id.guild.id}): {log_message}')
            return await MessageSender._account.send(channel_id, message)

    @staticmethod
    async def send_quote_message(channel_id: str, replay_id: Union[str, MessageObject], msg: str,
                                 at_id: Optional[str] = None) -> List[MessageObject]:
        if MessageSender._account is None:
            raise ValueError("Account is not set")
        message: List[Union[str, Element]] = [Quote(replay_id, False)]
        if at_id:
            message.append(At(at_id))
            message.append(" ")
        message.append(msg)
        return await MessageSender.send_message(channel_id, message)
