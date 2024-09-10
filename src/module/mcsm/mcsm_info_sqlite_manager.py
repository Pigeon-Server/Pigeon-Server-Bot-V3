from typing import List

from src.element.result import Result
from src.module.database.database_adapter import DatabaseAdapter
from src.module.mcsm.mcsm_info_database_manager import McsmInfoDatabaseManager
from src.type.response_body import InstanceInfo, RemoteServices
from src.type.types import DataEngineType, ReturnType


class McsmInfoSqliteManager(McsmInfoDatabaseManager):
    def __init__(self, database_instance: DatabaseAdapter):
        McsmInfoDatabaseManager.__init__(self, database_instance, DataEngineType.SQLITE)
        if database_instance.get_database_type() != DataEngineType.SQLITE:
            raise ValueError("Database type is not SQLITE")

    def test(self) -> bool:
        try:
            self._database.run_command("""SELECT sqlite_version();""")
            return True
        except Exception as _:
            return False

    def get_daemon_id(self, remote_uuid: str) -> Result:
        result = self._database.run_command("""SELECT id FROM mcsm_daemon WHERE uuid = ?""",
                                            [remote_uuid], ReturnType.ALL)
        if len(result) != 1:
            return Result.of_failure()
        return Result.of_success(str(result[0][0]))

    def update_instance_info(self, daemon_id: str, instance_info: List[RemoteServices.RemoteService.Service]) -> None:
        instance_list_query = self._database.run_command("""SELECT uuid FROM mcsm_instance WHERE remote_id = ?""",
                                                         [daemon_id], ReturnType.ALL)
        instances = []
        if instance_list_query:
            for instance in instance_list_query:
                instances.append(instance[0])
        sqls = []
        args = []
        # 遍历instance列表
        for instance in instance_info:
            # 查询实例是否被记录
            if instance.instanceUuid in instances:
                # 已被记录就更新状态,然后下一循环
                instances.remove(instance.instanceUuid)
                sqls.append("""UPDATE mcsm_instance SET status = ? WHERE uuid = ?;""")
                args.append([instance.status, instance.instanceUuid])
                continue
            # 如果没有被记录
            sqls.append("""INSERT INTO mcsm_instance (uuid, name, status, remote_id) VALUES (?, ?, ?, ?);""")
            args.append([instance.instanceUuid, instance.config.nickname, instance.status, daemon_id])
        if instances:
            # 删除没有被访问到的instance列表
            sqls.append("""DELETE FROM mcsm_instance WHERE uuid IN ?;""")
            args.append(tuple(instances))
        self._database.run_command(sqls, args)

    def update_mcsm_info(self, mcsm_info: RemoteServices, force_load: bool = False) -> None:
        if force_load:
            self._database.run_command("""DELETE FROM mcsm_instance;DELETE FROM mcsm_daemon;""")
        daemon_list_query = self._database.run_command("""SELECT id, uuid FROM mcsm_daemon;""",
                                                       return_type=ReturnType.ALL)
        daemon_dict = {}
        if daemon_list_query:
            for daemon in daemon_list_query:
                daemon_dict[daemon[1]] = daemon[0]
        for service in mcsm_info.data:
            # 查询是否已经被记录
            if service.uuid in daemon_dict.keys():
                daemon_id = daemon_dict[service.uuid]
                del daemon_dict[service.uuid]
            else:
                # 如果数据库内没有记录
                daemon_id = self._database.run_command("""INSERT INTO mcsm_daemon (name, uuid) VALUES (?, ?);""",
                                                       [service.remarks, service.uuid], ReturnType.CURSOR_ID)
            self.update_instance_info(daemon_id, service.instances)
        if len(daemon_dict.keys()) != 0:
            # 删除没有被访问到的daemon列表
            self._database.run_command("""DELETE FROM mcsm_daemon WHERE uuid IN ?;""",
                                       [tuple(daemon_dict.keys()), ])

    def get_server_status(self, remote_name: str, instance_uuid: str) -> int:
        return (self._database.run_command("""SELECT status FROM mcsm_instance WHERE uuid = ?""",
                                           [instance_uuid], ReturnType.ALL))[0][0]

    def is_daemon_name(self, name: str) -> Result:
        res = self._database.run_command("""SELECT uuid FROM mcsm_daemon WHERE name = ?""",
                                         [name], ReturnType.ALL)
        if len(res) == 1:
            return Result.of_success(res[0][0])
        return Result.of_failure(f"{name}不是一个有效的守护进程名称")

    def is_server_name(self, name: str) -> Result:
        res = self._database.run_command("""SELECT uuid FROM mcsm_instance WHERE name = ?""",
                                         [name], ReturnType.ALL)
        if len(res) == 1:
            return Result.of_success(res[0][0])
        return Result.of_failure(f"{name}不是一个有效的实例名称")

    def is_daemon_uuid(self, uuid: str) -> Result:
        res = self._database.run_command("""SELECT name FROM mcsm_daemon WHERE uuid = ?""",
                                         [uuid], ReturnType.ALL)
        if len(res) == 1:
            return Result.of_success(res[0][0])
        return Result.of_failure(f"{uuid}不是一个有效的守护进程UUID")

    def is_server_uuid(self, uuid: str) -> Result:
        res = self._database.run_command("""SELECT name FROM mcsm_instance WHERE uuid = ?""",
                                         [uuid], ReturnType.ALL)
        if len(res) == 1:
            return Result.of_success(res[0][0])
        return Result.of_failure(f"{uuid}不是一个有效的实例UUID")

    def get_remote_uuid_by_instance_name(self, name: str) -> Result:
        res = self._database.run_command("""SELECT mcsm_daemon.uuid FROM mcsm_instance 
                                                                INNER JOIN mcsm_daemon 
                                                                ON mcsm_instance.remote_id = mcsm_daemon.id 
                                                                WHERE mcsm_instance.name = ?""",
                                         [name], ReturnType.ALL)
        if len(res) == 1:
            return Result.of_success(res[0][0])
        return Result.of_failure(f"{name}不是一个有效的实例名称")

    def update_instance_status(self, remote_uuid: str, instance_uuid: str, instance_data: InstanceInfo) -> None:
        self._database.run_command("""UPDATE mcsm_instance SET status = ? WHERE uuid = ?""",
                                   [instance_data.status, remote_uuid])

    def rename_instance(self, original_name: str, new_name: str) -> Result:
        self._database.run_command("""UPDATE mcsm_instance SET name = ? WHERE name = ?""",
                                   [new_name, original_name])
        return Result.of_success(f"修改实例名称[{original_name}] -> [{new_name}]")

    def rename_remote(self, original_name: str, new_name: str) -> Result:
        self._database.run_command("""UPDATE mcsm_daemon SET name = ? WHERE name = ?""",
                                   [new_name, original_name])
        return Result.of_success(f"修改守护进程名称[{original_name}] -> [{new_name}]")

    def list_remote_instances(self, remote_uuid: str, remote_name: str) -> Result:
        result: str = f"[{remote_name}]\n"
        instances_list_query = self._database.run_command("""SELECT mcsm_instance.`name`, mcsm_instance.`status`
                                                                    FROM mcsm_daemon INNER JOIN mcsm_instance
                                                                    ON mcsm_daemon.id = mcsm_instance.remote_id
                                                                        WHERE mcsm_daemon.uuid = ?""",
                                                          [remote_uuid], ReturnType.ALL)

        for instance in instances_list_query:
            result += f"\t{instance[0]}: {self.status(instance[1])}\n"
        return Result.of_success(result.removesuffix("\n"))
