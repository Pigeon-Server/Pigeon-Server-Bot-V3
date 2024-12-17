from datetime import datetime
from time import localtime, strftime

from src.type.response_body import ResponseHeader
from src.type.types import HttpCode


class Response:

    def __init__(self, body: ResponseHeader):
        self._body: ResponseHeader = ResponseHeader(body) if isinstance(body, dict) else body
        self._time: int = self._body.time
        self._status: HttpCode
        match self._body.status:
            case 200:
                self._status = HttpCode.OK
            case 400:
                self._status = HttpCode.ERROR_PARAMS
            case 403:
                self._status = HttpCode.FORBIDDEN
            case 500:
                self._status = HttpCode.SERVER_ERROR

    @property
    def body(self) -> ResponseHeader:
        return self._body

    @property
    def time(self) -> str:
        return strftime("%Y-%m-%d %H:%M:%S", localtime(self._time / 1000))

    @property
    def local_time(self) -> datetime:
        return localtime(self._time / 1000)

    @property
    def timestamp(self) -> int:
        return self._time

    @property
    def success(self) -> bool:
        return self._status == HttpCode.OK

    @property
    def code(self) -> HttpCode:
        return self._status
