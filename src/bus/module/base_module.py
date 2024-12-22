from abc import ABC, abstractmethod
from typing import Union

from src.bus.event.event import Event


class BaseModule(ABC):
    @abstractmethod
    async def resolve(self, event: Union[Event, str], *args, **kwargs) -> bool:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError
