from abc import abstractmethod
from typing import List

from src.element.result import Result
from src.module.database.database_adapter import DatabaseAdapter
from src.module.mcsm.mcsm_info_manager import McsmInfoManager
from src.type.response_body import InstanceInfo, RemoteServices
from src.type.types import DataEngineType, ReturnType


class McsmInfoDatabaseManager(McsmInfoManager):
    _database: DatabaseAdapter

    def __init__(self, database_instance: DatabaseAdapter, data_engine: DataEngineType):
        super().__init__(data_engine)
        self._database = database_instance

    def get_number(self) -> tuple[int, int]:
        res = self._database.run_command(
            """SELECT COUNT(*) FROM mcsm_daemon UNION SELECT COUNT(*) FROM mcsm_instance;""",
            return_type=ReturnType.ALL)
        return res[0][0], res[1][0]

    @abstractmethod
    def get_daemon_id(self, remote_uuid: str) -> Result:
        raise NotImplementedError

    @abstractmethod
    def update_instance_info(self, daemon_id: str, instance_info: List[RemoteServices.RemoteService.Service]) -> None:
        raise NotImplementedError

    @abstractmethod
    def test(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def update_mcsm_info(self, mcsm_info: RemoteServices, force_load: bool = False) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_server_status(self, remote_name: str, instance_uuid: str) -> int:
        raise NotImplementedError()

    @abstractmethod
    def is_daemon_name(self, name: str) -> Result:
        raise NotImplementedError()

    @abstractmethod
    def is_server_name(self, name: str) -> Result:
        raise NotImplementedError()

    @abstractmethod
    def is_daemon_uuid(self, uuid: str) -> Result:
        raise NotImplementedError()

    @abstractmethod
    def is_server_uuid(self, uuid: str) -> Result:
        raise NotImplementedError()

    @abstractmethod
    def get_remote_uuid_by_instance_name(self, name: str) -> Result:
        raise NotImplementedError()

    def update_remote_status(self, remote_uuid: str, remote_data: RemoteServices) -> None:
        if remote_uuid:
            daemon_id = self.get_daemon_id(remote_uuid)
            if daemon_id.is_fail:
                self.update_mcsm_info(remote_data)
                return
            daemon_id = daemon_id.message
            for service in remote_data.data:
                if service.uuid != remote_uuid:
                    continue
                self.update_instance_info(daemon_id, service.instances)
            return
        self.update_mcsm_info(remote_data)

    @abstractmethod
    def update_instance_status(self, remote_uuid: str, instance_uuid: str, instance_data: InstanceInfo) -> None:
        raise NotImplementedError()

    @abstractmethod
    def rename_instance(self, original_name: str, new_name: str) -> Result:
        raise NotImplementedError()

    @abstractmethod
    def rename_remote(self, original_name: str, new_name: str) -> Result:
        raise NotImplementedError()

    def list_all_instances(self) -> Result:
        result: str = ""
        instances_list_query = self._database.run_command("""SELECT mcsm_daemon.`name` AS 'remote_name', 
                                                                        mcsm_instance.`name` AS 'instance_name', 
                                                                        mcsm_instance.`status`
                                                                    FROM mcsm_daemon INNER JOIN mcsm_instance
                                                                    ON mcsm_daemon.id = mcsm_instance.remote_id""",
                                                          return_type=ReturnType.ALL)
        instances = {}
        for instance in instances_list_query:
            if instance[0] in instances.keys():
                instances[instance[0]][instance[1]] = instance[2]
                continue
            instances[instance[0]] = {instance[1]: instance[2]}
        for daemon, instance in instances.items():
            result += f"[{daemon}]\n"
            for instance_name, status in instance.items():
                result += f"\t{instance_name}: {self.status(status)}\n"
        return Result.of_success(result.removesuffix("\n"))

    @abstractmethod
    def list_remote_instances(self, remote_uuid: str, remote_name: str) -> Result:
        raise NotImplementedError()
