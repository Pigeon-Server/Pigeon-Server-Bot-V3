from typing import Any, Callable, TypeVar, Generic

T = TypeVar('T', bound=Callable)


class EventCallback(Generic[T]):
    def __init__(self, callback: T, weight: int = 1) -> None:
        self._callback = callback
        self._weight = weight
        self._async = False

    @property
    def weight(self) -> int:
        return self._weight

    @weight.setter
    def weight(self, weight: int) -> None:
        self._weight = weight

    @property
    def callback(self) -> T:
        return self._callback

    @property
    def is_async(self) -> bool:
        return self._async

    def __eq__(self, __value: Any) -> bool:
        if isinstance(__value, self.__class__):
            return self._callback == __value._callback and self._weight == __value._weight
        else:
            return self._callback == __value
