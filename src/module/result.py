from typing import Optional


class Result:
    _status: bool
    _message: Optional[str]

    def __init__(self, status: bool, message: Optional[str] = None):
        self._status = status
        self._message = message

    @property
    def status(self) -> bool:
        return self._status

    @property
    def message(self) -> Optional[str]:
        return self._message

    @property
    def is_success(self) -> bool:
        return self._status is True

    @property
    def is_fail(self) -> bool:
        return self._status is False

    @classmethod
    def of_success(cls, message: Optional[str] = None) -> 'Result':
        return cls(True, message)

    @classmethod
    def of_failure(cls, message: Optional[str] = None) -> 'Result':
        return cls(False, message)
