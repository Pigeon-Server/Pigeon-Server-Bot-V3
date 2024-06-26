from typing import List, Optional, Union, overload

from satori import At, Element, Event, Guild, MessageObject, Quote
from satori.client import Account

from src.base.logger import logger
from src.base.config import config
from src.element.message import Message
from src.type.types import message_type


class MessageSender:
    _account: Optional[Account] = None

    def set_account(self, account: Account) -> None:
        self._account = account

    @overload
    async def send_message(self, channel_id: str, message: str) -> List[MessageObject]:
        ...

    @overload
    async def send_message(self, channel_id: str, message: list[str | Element]) -> List[MessageObject]:
        ...

    @overload
    async def send_message(self, channel_id: Event, message: str) -> List[MessageObject]:
        ...

    @overload
    async def send_message(self, channel_id: Event, message: list[str | Element]) -> List[MessageObject]:
        ...

    async def send_message(self, channel_id: Union[str, Event],
                           message: message_type) -> List[MessageObject]:
        if self._account is None:
            raise ValueError("Account is not set")
        if config.sys_config.dev:
            if isinstance(message, str):
                message = f"{'-' * 5}Dev{'-' * 5}\n{message}"
            if isinstance(message, list):
                message = [f"{'-' * 5}Dev{'-' * 5}\n"] + message
        log_message = Message.parse(message)
        if isinstance(channel_id, str):
            channel: Guild = await self._account.guild_get(guild_id=channel_id)
            logger.info(f'[消息]->{channel.name}({channel.id}): {log_message}')
            return await self._account.send_message(channel_id, message)
        if isinstance(channel_id, Event):
            logger.info(f'[消息]->{channel_id.guild.name}({channel_id.guild.id}): {log_message}')
            return await self._account.send(channel_id, message)

    async def send_quote_message(self, channel_id: str, replay_id: Union[str, MessageObject], msg: str,
                                 at_id: Optional[str] = None) -> List[MessageObject]:
        message: List[Union[str, Element]] = [Quote(replay_id, False)]
        if at_id:
            message.append(At(at_id))
            message.append(" ")
        message.append(msg)
        return await self.send_message(channel_id, message)
