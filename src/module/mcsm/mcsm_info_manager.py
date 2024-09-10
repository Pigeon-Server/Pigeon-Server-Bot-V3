from abc import abstractmethod
from typing import Optional, Tuple

from src.element.result import Result
from src.type.response_body import InstanceInfo, RemoteServices
from src.type.types import DataEngineType


class McsmInfoManager:
    _status_code: list[str] = ["状态未知", "已停止", "停止中", "启动中", "运行中"]
    _data_engine: DataEngineType

    def __init__(self, data_engine: DataEngineType):
        self._data_engine = data_engine

    @property
    def data_engine(self) -> DataEngineType:
        return self._data_engine

    def status(self, code: int) -> str:
        return self._status_code[code + 1]

    def check_name(self, remote_name: Optional[str] = None,
                   instance_name: Optional[str] = None) -> Tuple[Optional[Result], Optional[Result]]:
        if remote_name is None:
            if instance_name is None:
                return None, None
            return None, self.is_server_name(instance_name)
        if instance_name is None:
            return self.is_daemon_name(remote_name), None
        return self.is_daemon_name(remote_name), self.is_server_name(instance_name)

    def check_uuid(self, remote_uuid: str, instance_uuid: str) -> Tuple[Result, Result]:
        return self.is_daemon_uuid(remote_uuid), self.is_server_uuid(instance_uuid)

    @abstractmethod
    def get_number(self) -> tuple[int, int]:
        raise NotImplementedError

    @abstractmethod
    def test(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def update_mcsm_info(self, mcsm_info: RemoteServices, force_load: bool = False) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_server_status(self, remote_name: str, instance_uuid: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def is_daemon_name(self, name: str) -> Result:
        raise NotImplementedError

    @abstractmethod
    def is_server_name(self, name: str) -> Result:
        raise NotImplementedError

    @abstractmethod
    def is_daemon_uuid(self, uuid: str) -> Result:
        raise NotImplementedError

    @abstractmethod
    def is_server_uuid(self, uuid: str) -> Result:
        raise NotImplementedError

    @abstractmethod
    def get_remote_uuid_by_instance_name(self, name: str) -> Result:
        raise NotImplementedError

    @abstractmethod
    def update_remote_status(self, remote_uuid: str, remote_data: RemoteServices) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_instance_status(self, remote_uuid: str, instance_uuid: str, instance_data: InstanceInfo) -> None:
        raise NotImplementedError

    @abstractmethod
    def rename_instance(self, original_name: str, new_name: str) -> Result:
        raise NotImplementedError

    @abstractmethod
    def rename_remote(self, original_name: str, new_name: str) -> Result:
        raise NotImplementedError

    @abstractmethod
    def list_all_instances(self) -> Result:
        raise NotImplementedError

    @abstractmethod
    def list_remote_instances(self, remote_uuid: str, remote_name: str) -> Result:
        raise NotImplementedError
