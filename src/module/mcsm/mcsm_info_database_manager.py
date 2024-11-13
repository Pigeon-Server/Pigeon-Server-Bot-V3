from typing import List, Optional, Tuple

from peewee import Case, Expression, fn

from src.database.mcsm_model import McsmDaemon, McsmInstance
from src.element.result import Result
from src.module.mcsm.mcsm_info_manager import McsmInfoManager
from src.type.response_body import InstanceInfo, RemoteServices
from src.database.base_model import database, database_transaction


class McsmInfoDatabaseManager(McsmInfoManager):

    def get_number(self) -> tuple[int, int]:
        res = McsmDaemon.select(fn.COUNT(McsmDaemon.id)).union(McsmInstance.select(fn.COUNT(McsmInstance.id))).execute()
        return res[0][0], res[1][0]

    @database_transaction
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

    def list_all_instances(self) -> Result:
        result: str = ""
        instances_list_query: list[McsmInstance] = (McsmInstance
                                                    .select(McsmDaemon.name, McsmInstance.name, McsmInstance.status)
                                                    .join(McsmDaemon)
                                                    .execute())
        instances = {}
        for instance in instances_list_query:
            if instance.remote.name in instances.keys():
                instances[instance.remote.name][instance.name] = instance.status
                continue
            instances[instance.remote.name] = {instance.name: instance.status}
        for daemon, instance in instances.items():
            result += f"[{daemon}]\n"
            for instance_name, status in instance.items():
                result += f"\t{instance_name}: {self.status(status)}\n"
        return Result.of_success(result.removesuffix("\n"))

    def test(self) -> bool:
        return database.is_connection_usable()

    @staticmethod
    def get_daemon_id(remote_uuid: str) -> Result:
        result: Optional[McsmDaemon] = McsmDaemon.select(McsmDaemon.id).where(McsmDaemon.uuid == remote_uuid).first()
        if result is None:
            return Result.of_failure()
        return Result.of_success(str(result.id))

    @database_transaction
    def update_instance_info(self, daemon_id: str, instance_info: List[RemoteServices.RemoteService.Service]) -> None:
        instances: dict[str, McsmInstance] = {instance.uuid: instance
                                              for instance in McsmInstance.select(McsmInstance.uuid)
                                              .where(McsmInstance.remote == daemon_id).execute()}
        case_statements: list[Tuple[Expression, int]] = []
        update_uuid: list[str] = []
        # 遍历instance列表
        for instance in instance_info:
            # 查询实例是否被记录
            if instance.instanceUuid in instances:
                # 已被记录就更新状态,然后下一循环
                update_uuid.append(instance.instanceUuid)
                case_statements.append((McsmInstance.uuid == instance.instanceUuid, instance.status))
                del instances[instance.instanceUuid]
                continue
            # 如果没有被记录
            McsmInstance.create(
                name=instance.config.nickname,
                uuid=instance.instanceUuid,
                status=instance.status,
                remote=daemon_id
            )
        if case_statements:
            (McsmInstance
             .update(status=Case(None, case_statements, McsmInstance.status))
             .where(McsmInstance.uuid << update_uuid)
             .execute())
        if instances:
            McsmInstance.delete().where(McsmInstance.uuid << list(instances.keys())).execute()

    @database_transaction
    def update_mcsm_info(self, mcsm_info: RemoteServices, force_load: bool = False) -> None:
        if force_load:
            McsmInstance.delete()
            McsmDaemon.delete()

        daemon_dict: dict[str, McsmDaemon] = {instance.uuid: instance for instance in McsmDaemon.select()}

        for service in mcsm_info.data:
            # 查询是否已经被记录
            if service.uuid in daemon_dict:
                daemon_id = daemon_dict[service.uuid].id
                del daemon_dict[service.uuid]
            else:
                # 如果数据库内没有记录
                daemon: McsmDaemon = McsmDaemon.create(uuid=service.uuid, name=service.remarks)
                daemon_id = daemon.id
            self.update_instance_info(daemon_id, service.instances)
        if len(daemon_dict.keys()) != 0:
            # 删除没有被访问到的daemon列表
            McsmDaemon.delete().where(McsmDaemon.uuid << list(daemon_dict.keys())).execute()

    def get_server_status(self, remote_name: str, instance_uuid: str) -> int:
        res: Optional[McsmInstance] = McsmInstance.select().where(McsmInstance.uuid == instance_uuid).first()
        if res is None:
            return -1
        return res.status

    def is_daemon_name(self, name: str) -> Result:
        res: Optional[McsmDaemon] = McsmDaemon.select().where(McsmDaemon.name == name).first()
        if res:
            return Result.of_success(res.uuid)
        return Result.of_failure(f"{name}不是一个有效的守护进程名称")

    def is_server_name(self, name: str) -> Result:
        res: Optional[McsmInstance] = McsmInstance.select(McsmInstance.uuid).where(McsmInstance.name == name).first()
        if res:
            return Result.of_success(res.uuid)
        return Result.of_failure(f"{name}不是一个有效的实例名称")

    def is_daemon_uuid(self, uuid: str) -> Result:
        res: Optional[McsmDaemon] = McsmDaemon.select().where(McsmDaemon.uuid == uuid).first()
        if res:
            return Result.of_success(res.name)
        return Result.of_failure(f"{uuid}不是一个有效的守护进程UUID")

    def is_server_uuid(self, uuid: str) -> Result:
        res: Optional[McsmInstance] = McsmInstance.select(McsmInstance.name).where(McsmInstance.uuid == uuid).first()
        if res:
            return Result.of_success(res.name)
        return Result.of_failure(f"{uuid}不是一个有效的实例UUID")

    def get_remote_uuid_by_instance_name(self, name: str) -> Result:
        res: Optional[McsmInstance] = (McsmInstance
                                       .select(McsmDaemon.uuid)
                                       .where(McsmInstance.name == name)
                                       .join(McsmDaemon)
                                       .first())
        if res:
            return Result.of_success(res.remote.uuid)
        return Result.of_failure(f"{name}不是一个有效的实例名称")

    def update_instance_status(self, remote_uuid: str, instance_uuid: str, instance_data: InstanceInfo) -> None:
        McsmInstance.update(status=instance_data.data.status).where(McsmInstance.uuid == instance_uuid).execute()

    def rename_instance(self, original_name: str, new_name: str) -> Result:
        McsmInstance.update(name=new_name).where(McsmInstance.name == original_name).execute()
        return Result.of_success(f"修改实例名称[{original_name}] -> [{new_name}]")

    def rename_remote(self, original_name: str, new_name: str) -> Result:
        McsmDaemon.update(name=new_name).where(McsmDaemon.name == original_name).execute()
        return Result.of_success(f"修改守护进程名称[{original_name}] -> [{new_name}]")

    def list_remote_instances(self, remote_uuid: str, remote_name: str) -> Result:
        result: str = f"[{remote_name}]\n"
        instances_list_query: list[McsmInstance] = (McsmInstance
                                                    .select(McsmInstance.name, McsmInstance.status)
                                                    .where(McsmDaemon.uuid == remote_uuid)
                                                    .join(McsmDaemon)
                                                    .execute())
        for instance in instances_list_query:
            result += f"\t{instance.name}: {self.status(instance.status)}\n"
        return Result.of_success(result.removesuffix("\n"))
