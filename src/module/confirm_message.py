from asyncio import AbstractEventLoop, get_event_loop, run_coroutine_threadsafe
from threading import Timer
from typing import Awaitable, Callable, Optional

from satori import Event
from satori.client import Account, App
from typing_extensions import Any

from src.element.message import Message
from src.type.types import ReplyType


class Confirm:
    _target_message: Message
    _callback: Callable[[ReplyType], Awaitable[Any]]
    _enable_timeout: bool = False
    _timeout: int
    _app: App
    _timer: Optional[Timer] = None
    _loop: AbstractEventLoop = get_event_loop()
    _accept_checker: Callable[[str], bool]
    _reject_checker: Callable[[str], bool]

    def __init__(self, app: App, target_message: Message, callback: Callable[[ReplyType], Awaitable[Any]],
                 timeout: int = -1, accept_checker: Optional[Callable[[str], bool]] = None,
                 reject_checker: Optional[Callable[[str], bool]] = None):
        self._target_message = target_message
        self._callback = callback
        if timeout != -1:
            self._enable_timeout = True
            self._timeout = timeout
        self._app = app
        self._accept_checker = accept_checker if accept_checker else lambda msg: msg == "是"
        self._reject_checker = reject_checker if reject_checker else lambda msg: msg == "否"

    def start(self) -> None:
        if self._enable_timeout:
            self._timer = Timer(self._timeout, self.stop_timeout)
            self._timer.start()
        self._app.event_callbacks.append(self.handler)

    def stop_timeout(self) -> None:
        run_coroutine_threadsafe(self._callback(ReplyType.TIMEOUT), self._loop)
        self.stop()

    def stop(self) -> None:
        if self._timer.is_alive():
            self._timer.cancel()
        self._app.event_callbacks.remove(self.handler)

    async def handler(self, account: Account, event: Event) -> None:
        now_message: Message = Message(event)
        if (now_message.sender_id == self._target_message.sender_id
                and now_message.group_id == self._target_message.group_id):
            if self._accept_checker(now_message.message):
                await self._callback(ReplyType.ACCEPT)
                self.stop()
                return
            if self._reject_checker(now_message.message):
                await self._callback(ReplyType.REJECT)
                self.stop()
                return
        return
