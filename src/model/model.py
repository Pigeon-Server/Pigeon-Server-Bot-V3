from abc import ABC, abstractmethod


class Model(ABC):
    @abstractmethod
    def insert(self) -> tuple[str, list[str]]:
        ...

    @abstractmethod
    def select(self) -> tuple[str, list[str]]:
        ...

    @abstractmethod
    def delete(self) -> tuple[str, list[str]]:
        ...

    @abstractmethod
    def update(self) -> tuple[str, list[str]]:
        ...

