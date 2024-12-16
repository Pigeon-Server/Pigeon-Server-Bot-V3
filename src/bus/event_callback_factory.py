from asyncio import iscoroutinefunction

from src.bus.handler.async_event_callback import AsyncEventCallback
from src.bus.handler.event_callback import EventCallback, T
from src.bus.handler.sync_event_callback import SyncEventCallback


class EventCallbackFactory:
    """
    创建 EventCallback 实例的工厂
    """
    @staticmethod
    def create(callback: T, weight: int = 1) -> EventCallback:
        if iscoroutinefunction(callback):
            return AsyncEventCallback(callback, weight)
        else:
            return SyncEventCallback(callback, weight)
