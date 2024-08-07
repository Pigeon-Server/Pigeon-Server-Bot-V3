from typing import Dict, Union

from bidict import bidict

from src.base.logger import logger
from src.element.result import Result
from src.module.json_database import DataType, JsonDataBase
from src.module.mcsm.mcsm_info_manager import McsmInfoManager
from src.type.response_body import InstanceInfo, RemoteServices


class McsmInfoJsonManager(McsmInfoManager, JsonDataBase):
    _daemon_uuid: bidict
    _server: Dict[str, Union[bidict, dict]]

    def __init__(self):
        McsmInfoManager.__init__(self)
        JsonDataBase.__init__(self, "mcsm.json", DataType.DICT)

    def test(self) -> bool:
        try:
            self.write_data()
            return True
        except Exception as _:
            return False

    def get_number(self) -> tuple[int, int]:
        instance_number = 0
        for server in self._stored_data["servers"].keys():
            instance_number += len(self._stored_data["servers"][server].keys())
        return len(self._stored_data["daemon_list"].keys()), instance_number

    def update_mcsm_info(self, mcsm_info: RemoteServices, force_load: bool = False) -> None:
        backup = self._stored_data
        try:
            if force_load:
                self._stored_data = {}
            if "daemon_list" not in self._stored_data.keys():
                self._stored_data["daemon_list"] = {}
            if "servers" not in self._stored_data.keys():
                self._stored_data["servers"] = {}
            if "daemon_uuid" not in self._stored_data.keys():
                self._stored_data["daemon_uuid"] = {}
            # 从json里面读取数据
            self._server = self._stored_data["servers"]
            daemon_uuid = self._stored_data["daemon_uuid"]
            daemon_list = self._stored_data["daemon_list"]
            self._daemon_uuid = bidict(daemon_uuid)
            for service in mcsm_info.data:
                # 如果UUID已经被记录
                if service.uuid in self._daemon_uuid.inverse.keys():
                    # 更新daemon名称
                    service.remarks = self._daemon_uuid.inverse[service.uuid]
                else:
                    # 如果没有那么就新增字段
                    daemon_uuid[service.remarks] = service.uuid
                    self._daemon_uuid[service.remarks] = service.uuid
                # 如果在servers里面没有字段
                if service.uuid not in self._server.keys():
                    # 创建一个空白的字段
                    self._server[service.uuid] = {}
                # 如果daemon_list里面没有字段:
                if service.remarks not in daemon_list.keys():
                    # 创建一个基础字段
                    daemon_list[service.remarks] = {
                        "uuid": service.uuid,
                        "available": service.available,
                        "instances": {}
                    }
                # 每次运行都清空instances
                daemon_list[service.remarks]["instances"] = {}
                server = bidict(self._server[service.uuid])
                # 遍历instances列表
                for instance in service.instances:
                    # 如果server里面有记录
                    if instance.instanceUuid in server.inverse.keys():
                        # 更新server的名称
                        instance.config.nickname = server.inverse[instance.instanceUuid]
                    else:
                        # 如果没有记录,则创建一条记录
                        self._server[service.uuid][instance.config.nickname] = instance.instanceUuid
                    daemon_list[service.remarks]["instances"][instance.instanceUuid] = instance.status
                for k, v in server.inverse.items():
                    if k not in daemon_list[service.remarks]["instances"].keys():
                        del self._server[service.uuid][v]
            self._server = dict(self._stored_data["servers"])
            for k, v in self._server.items():
                self._server[k] = bidict(v)
        except Exception as e:
            logger.error("MCSM初始化失败")
            logger.error(e)
            self._stored_data = backup
            raise e
        finally:
            self.write_data()

    def get_server_status(self, remote_name: str, instance_uuid: str) -> int:
        return self._stored_data["daemon_list"][remote_name]["instances"][instance_uuid]

    def is_daemon_name(self, name: str) -> Result:
        if name in self._daemon_uuid.keys():
            return Result.of_success(self._daemon_uuid[name])
        return Result.of_failure(f"{name}不是一个有效的守护进程名称")

    def is_server_name(self, name: str) -> Result:
        for k, v in self._server.items():
            for k_, v_ in v.items():
                if k_ == name:
                    return Result.of_success(v_)
        return Result.of_failure(f"{name}不是一个有效的实例名称")

    def is_daemon_uuid(self, uuid: str) -> Result:
        if uuid in self._daemon_uuid.inverse.keys():
            return Result.of_success(self._daemon_uuid.inverse[uuid])
        return Result.of_failure(f"{uuid}不是一个有效的守护进程UUID")

    def is_server_uuid(self, uuid: str) -> Result:
        for k, v in self._server.items():
            for k_, v_ in v.inverse.items():
                if k_ == uuid:
                    return Result.of_success(v_)
        return Result.of_failure(f"{uuid}不是一个有效的实例UUID")

    def get_remote_uuid_by_instance_name(self, name: str) -> Result:
        for k, v in self._server.items():
            for k_, v_ in v.items():
                if k_ == name:
                    return Result.of_success(k)
        return Result.of_failure(f"{name}不是一个有效的实例名称")

    def update_remote_status(self, remote_uuid: str, remote_data: RemoteServices) -> None:
        daemon_list = self._stored_data["daemon_list"]
        for service in remote_data.data:
            if ((remote_uuid is not None and service.uuid != remote_uuid)
                    or service.uuid not in self._daemon_uuid.inverse.keys()):
                continue
            service.remarks = self._daemon_uuid.inverse[service.uuid]
            for instance in service.instances:
                daemon_list[service.remarks]["instances"][instance.instanceUuid] = instance.status
        self.write_data()

    def update_instance_status(self, remote_uuid: str, instance_uuid: str, instance_data: InstanceInfo) -> None:
        self._stored_data["daemon_list"][self._daemon_uuid.inverse[remote_uuid]]["instances"][
            instance_uuid] = instance_data.data.status
        self.write_data()

    def rename_instance(self, original_name: str, new_name: str) -> Result:
        daemon_uuid = self.get_remote_uuid_by_instance_name(original_name).message
        server_list = self._stored_data["servers"][daemon_uuid]
        server_list[new_name] = server_list.pop(original_name)
        self._server[daemon_uuid][new_name] = self._server[daemon_uuid].pop(original_name)
        self.write_data()
        return Result.of_success(f"修改实例名称[{original_name}] -> [{new_name}]")

    def rename_remote(self, original_name: str, new_name: str) -> Result:
        self._stored_data["daemon_list"][new_name] = self._stored_data["daemon_list"].pop(original_name)
        self._stored_data["daemon_uuid"][new_name] = self._stored_data["daemon_uuid"].pop(original_name)
        self._daemon_uuid[new_name] = self._daemon_uuid.pop(original_name)
        self.write_data()
        return Result.of_success(f"修改守护进程名称[{original_name}] -> [{new_name}]")

    def list_all_instances(self) -> Result:
        result: str = ""
        for k, v in self._stored_data["daemon_list"].items():
            result += f"[{k}]\n"
            for k_, v_ in v["instances"].items():
                result += f"\t{self._server[v["uuid"]].inverse[k_]}: {self.status(v_)}\n"
        return Result.of_success(result.removesuffix("\n"))

    def list_remote_instances(self, remote_uuid: str, remote_name: str) -> Result:
        result = f"[{remote_name}]\n"
        for k_, v_ in self._stored_data["daemon_list"][remote_name]["instances"].items():
            result += f"\t{self._server[remote_uuid].inverse[k_]}: {self.status(v_)}\n"
        return Result.of_success(result.removesuffix("\n"))
