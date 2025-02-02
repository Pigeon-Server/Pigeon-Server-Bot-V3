from typing import Union

from src.bus.base_bus import BaseBus
from src.bus.event.event import Event
from src.bus.module.bus_filter import BusFilter
from src.bus.module.bus_inject import BusInject


class EventBus(BaseBus, BusFilter, BusInject):
    """
    事件总线
    """

    def __init__(self, max_concurrent_tasks: int = 10):
        BaseBus.__init__(self, max_concurrent_tasks)
        BusFilter.__init__(self)
        BusInject.__init__(self)

    async def publish(self, event: Union[Event, str], *args, **kwargs) -> None:
        await BusInject.resolve(self, event, args, kwargs)
        if await BusFilter.resolve(self, event, args, kwargs):
            return
        await super().publish(event, *args, **kwargs)

    def clear(self):
        super().clear()
