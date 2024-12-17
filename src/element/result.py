from typing import Optional


class Result:
    def __init__(self, status: bool, message: Optional[str] = None):
        self._status: bool = status
        self._message: Optional[str] = message

    @property
    def status(self) -> bool:
        return self._status

    @property
    def message(self) -> Optional[str]:
        return self._message

    @property
    def is_success(self) -> bool:
        return self._status

    @property
    def has_message(self) -> bool:
        return self._message is not None

    @property
    def is_fail(self) -> bool:
        return not self._status

    @classmethod
    def of_success(cls, message: Optional[str] = None) -> 'Result':
        return cls(True, message)

    @classmethod
    def of_failure(cls, message: Optional[str] = None) -> 'Result':
        return cls(False, message)

    def __repr__(self):
        return f'Result({self.status}, {self.message})'
