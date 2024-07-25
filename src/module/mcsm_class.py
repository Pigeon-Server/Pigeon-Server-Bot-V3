from datetime import datetime

from bidict import bidict
from re import sub
from sys import exit
from typing import Dict, Optional, Tuple, Union
from requests import get
from asyncio.tasks import sleep
from src.base.logger import logger
from src.element.response import Response
from src.element.result import Result
from src.exception.exception import IncomingParametersError
from src.module.json_database import JsonDataBase
from src.type.response_body import RemoteServices, InstanceInfo
from src.type.types import HttpCode


class McsmManager(JsonDataBase):
    _api_url: str = None
    _api_key: str = None
    _enable_SSL: bool = True
    _status_code: list[str] = ["状态未知", "已停止", "停止中", "启动中", "运行中"]
    _daemon_uuid: bidict
    _server: Dict[str, Union[bidict, dict]]

    def __init__(self, apikey: str, url: str = "http://127.0.0.1:23333", enable_ssl: bool = False) -> None:
        """
        Args:
            apikey: API 接口密钥
            url: MCSM网页端后台地址（跨域请求 API 接口须打开）
            enable_ssl: 是否启用ssl连接（注意：如果网页是http访问，则此选项永远为False）
        """
        super().__init__("mcsm.json", 5)
        if not url.startswith("http"):
            raise IncomingParametersError("api地址错误,必须以http或https开头")
        self._enable_SSL = False if url.startswith("http://") else enable_ssl
        self._api_url = url if "/api" in url else f"{url}/api"
        self._api_key = apikey
        self.test_connect()
        self.get_mcsm_info()

    def test_connect(self) -> None:
        """
        测试到MCSM的连接\n
        """
        try:
            response = self._call_api("overview")
            if response is None:
                raise ConnectionError("Connect timed out")
            if not response.success:
                match response.code:
                    case HttpCode.ERROR_PARAMS:
                        logger.critical("访问参数错误")
                    case HttpCode.FORBIDDEN:
                        logger.critical("Apikey错误")
                    case HttpCode.SERVER_ERROR:
                        logger.critical("服务器出错")
                exit()
        except ConnectionError as err:
            logger.error(err)
            logger.critical("无法访问MCSM，请检查网络和url设置是否出错")

    def _call_api(self, path: str, params: Optional[dict] = None) -> Response:
        """
        对API发起请求\n
        Args:
            path: api路径
            params: 需要在请求中额外添加的参数（除apikey以外的参数）
        Returns:
            dict: 返回api返回的内容(dict)没有访问成功则抛出异常
        """
        if path.startswith("/api"):
            url = f"{self._api_url}{path[4:]}"
        elif path.startswith("api"):
            url = f"{self._api_url}{path[3:]}"
        elif path.startswith("/"):
            url = f"{self._api_url}{path}"
        else:
            url = f"{self._api_url}/{path}"
        param = {
            "apikey": self._api_key
        }
        if params is not None:
            if not isinstance(params, dict):
                raise ValueError("请求参数错误！")
            param.update(params)
        logger.trace(f"HTTP请求：GET {url}")
        try:
            res = get(url=url, headers={"Content-Type": "application/json; charset=utf-8"},
                      params=param, timeout=10, verify=self._enable_SSL).json()
            return Response(res)
        except OSError as e:
            logger.error(e)

    def get_mcsm_info(self, force_load: bool = False) -> None:
        """
        获取当前面板下所有守护进程UUID以及所有实例名
        Args:
            force_load: 是否强制刷新已储存的uuid
        """
        backup = self._stored_data
        try:
            data = self._call_api("service/remote_services")
            body = RemoteServices(data.body)
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
            for service in body.data:
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

    def status(self, code: int) -> str:
        return self._status_code[code + 1]

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

    def get_server_remote_uuid_by_name(self, name: str) -> Result:
        for k, v in self._server.items():
            for k_, v_ in v.items():
                if k_ == name:
                    return Result.of_success(k)
        return Result.of_failure(f"{name}不是一个有效的实例名称")

    def get_server_remote_name_by_name(self, name: str) -> Result:
        for k, v in self._server.items():
            for k_, v_ in v.items():
                if k_ == name:
                    return Result.of_success(self._daemon_uuid.inverse[k])
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

    # 第一次封装
    def get_instance_info(self, remote_uuid: str, instance_uuid: str) -> Response:
        """
        获取实例状态\n
        Args:
            remote_uuid: 守护进程uuid
            instance_uuid: 实例uuid
        """
        return self._call_api("/instance", {"uuid": instance_uuid, "remote_uuid": remote_uuid})

    def update_instance_status(self, remote_uuid: Optional[str] = None, instance_uuid: Optional[str] = None) -> None:
        """
        刷新所有守护进程的所有实例的运行状态
        刷新某一守护进程的所有实例的运行状态
        刷新某一守护进程的某一实例的运行状态
        Args:
            remote_uuid: 守护进程uuid，可为空
            instance_uuid: 实例uuid，可为空
        """
        if instance_uuid is None:
            data = self._call_api("service/remote_services")
            body = RemoteServices(data.body)
            daemon_list = self._stored_data["daemon_list"]
            for service in body.data:
                if ((remote_uuid is not None and service.uuid != remote_uuid)
                        or service.uuid not in self._daemon_uuid.inverse.keys()):
                    continue
                service.remarks = self._daemon_uuid.inverse[service.uuid]
                for instance in service.instances:
                    daemon_list[service.remarks]["instances"][instance.instanceUuid] = instance.status
            self.write_data()
            return
        if remote_uuid is None:
            raise RuntimeError("传入参数错误")
        data = self.get_instance_info(remote_uuid, instance_uuid)
        body = InstanceInfo(data.body)
        self._stored_data["daemon_list"][self._daemon_uuid.inverse[remote_uuid]]["instances"][
            instance_uuid] = body.data.status
        self.write_data()

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

    def start_instance(self, remote_uuid: str, instance_uuid: str) -> Result:
        daemon, server = self.check_uuid(remote_uuid, instance_uuid)
        if daemon.is_fail:
            return daemon
        if server.is_fail:
            return server
        self.update_instance_status(remote_uuid, instance_uuid)
        match self.get_server_status(daemon.message, instance_uuid):
            case -1:
                return Result.of_failure("实例状态未知，无法启动")
            case 0:
                logger.debug(f"启动服务器{server.message}({daemon.message})")
                res = self._call_api("/protected_instance/open", {"uuid": instance_uuid, "remote_uuid": remote_uuid})
                if res.success:
                    return Result.of_success("执行成功，实例正在启动")
                return Result.of_failure(f"实例启动失败，api返回Code: {res.code}")
            case 1:
                return Result.of_failure("实例正在停止，无法启动")
            case 2:
                return Result.of_failure("实例正在启动中，请耐心等待")
            case 3:
                return Result.of_failure("实例已在运行")

    def stop_instance(self, remote_uuid: str, instance_uuid: str, force_kill: bool = False) -> Result:
        daemon, server = self.check_uuid(remote_uuid, instance_uuid)
        if daemon.is_fail:
            return daemon
        if server.is_fail:
            return server
        self.update_instance_status(remote_uuid, instance_uuid)
        match self.get_server_status(daemon.message, instance_uuid):
            case -1:
                return Result.of_failure("实例状态未知，无法启动")
            case 0:
                return Result.of_failure("实例已停止，无法关闭")
            case 1:
                if not force_kill:
                    return Result.of_failure("实例正在停止，无法关闭")
            case 2:
                if not force_kill:
                    return Result.of_failure("实例正在启动中，无法关闭")
        if force_kill:
            logger.debug(f"强制关闭实例{server.message}({daemon.message})")
            res = self._call_api("/protected_instance/kill", {"uuid": instance_uuid, "remote_uuid": remote_uuid})
            if res.success:
                return Result.of_success("执行成功，强制关闭实例")
            return Result.of_failure(f"强制关闭实例失败，api返回Code: {res.code}")
        logger.debug(f"关闭实例{server.message}({daemon.message})")
        res = self._call_api("/protected_instance/stop", {"uuid": instance_uuid, "remote_uuid": remote_uuid})
        if res.success:
            return Result.of_success("执行成功，实例正在关闭")
        return Result.of_failure(f"关闭实例失败，api返回Code: {res.code}")

    def restart_instance(self, remote_uuid: str, instance_uuid: str) -> Result:
        daemon, server = self.check_uuid(remote_uuid, instance_uuid)
        if daemon.is_fail:
            return daemon
        if server.is_fail:
            return server
        self.update_instance_status(remote_uuid, instance_uuid)
        match self.get_server_status(daemon.message, instance_uuid):
            case -1:
                return Result.of_failure("实例状态未知，无法重启")
            case 0:
                return Result.of_failure("实例已停止，无法重启")
            case 1:
                return Result.of_failure("实例正在停止，无法重启")
            case 2:
                return Result.of_failure("实例正在启动中，无法重启")
            case 3:
                logger.debug(f"重启实例{server.message}({daemon.message})")
                res = self._call_api("/protected_instance/restart", {"uuid": instance_uuid, "remote_uuid": remote_uuid})
                if res.success:
                    return Result.of_success("执行成功，实例正在重启")
                return Result.of_failure(f"重启实例失败，api返回Code: {res.code}")

    def _command(self, instance_uuid: str, remote_uuid: str, command: str) -> float:
        res = self._call_api("/protected_instance/command", {
            "remote_uuid": remote_uuid,
            "uuid": instance_uuid,
            "command": command
        })
        return res.timestamp / 1000

    def _get_command_output(self, instance_uuid: str, remote_uuid: str, time_stamp: float) -> Result:
        data = self._call_api("/api/protected_instance/outputlog", {
            "remote_uuid": remote_uuid,
            "uuid": instance_uuid,
            "size": 10240
        })
        if not data.success:
            return Result.of_failure(f"命令执行失败, apiCode: {data.code}")
        temp_list: list = []
        time = datetime.fromtimestamp(time_stamp).strftime("[%H:%M:%S]")
        data = data.body.data.split('\n')
        for item in data:
            if time in item and "[Server thread/INFO]" in item:
                temp_list.append(item)
        res: str = ""
        for raw in temp_list:
            if raw.find("]: ") != -1:
                res += f"{raw[raw.find(']: ') + 3:]}\n"
        res = res.removesuffix("\n")
        res = sub(r"(\033\[(\d+|\d+;\d+|\d+;\d+;\d+)?m)?", "", res)
        return Result.of_success(res)

    # 第二次封装
    def check_instance_status(self, instance_name: str, remote_name: str = None) -> Result:
        daemon, server = self.check_name(remote_name, instance_name)
        if server.is_fail:
            return server
        instance_uuid = server.message
        if remote_name is None:
            remote_uuid = self.get_server_remote_uuid_by_name(instance_name).message
            remote_name = self.is_daemon_uuid(remote_uuid).message
        else:
            if daemon.is_fail:
                return daemon
            remote_uuid = daemon.message
        self.update_instance_status(remote_uuid, instance_uuid)
        return Result.of_success(f"守护进程名称: {remote_name}\n"
                                 f"实例名称: {instance_name}\n"
                                 f"实例状态: {self.status(self.get_server_status(remote_name, instance_uuid))}")

    async def run_command(self, instance_name: str, command: str) -> Result:
        _, server = self.check_name(instance_name=instance_name)
        if server.is_fail:
            return server
        remote_uuid = self.get_server_remote_uuid_by_name(instance_name).message
        instance_uuid = server.message
        self.update_instance_status(remote_uuid, instance_uuid)
        status = self.get_server_status(self.is_daemon_uuid(remote_uuid).message, instance_uuid)
        if status != 3:
            return Result.of_failure(f"实例当前状态是:{self.status(status)},无法执行命令")
        time_stamp = self._command(instance_uuid, remote_uuid, command)
        await sleep(1)
        return self._get_command_output(instance_uuid, remote_uuid, time_stamp)

    def list_instance(self, remote_name: str = None) -> Result:
        result: str = ""
        if remote_name is None:
            self.update_instance_status()
            for k, v in self._stored_data["daemon_list"].items():
                result += f"[{k}]\n"
                for k_, v_ in v["instances"].items():
                    result += f"\t{self._server[v["uuid"]].inverse[k_]}: {self.status(v_)}\n"
            return Result.of_success(result.removesuffix("\n"))
        daemon, _ = self.check_name(remote_name)
        if daemon.is_fail:
            return daemon
        remote_uuid = daemon.message
        self.update_instance_status(remote_uuid)
        result += f"[{remote_name}]\n"
        for k_, v_ in self._stored_data["daemon_list"][remote_name]["instances"].items():
            result += f"\t{self._server[remote_uuid].inverse[k_]}: {self.status(v_)}\n"
        return Result.of_success(result.removesuffix("\n"))

    def rename(self, original_name: str, new_name: str) -> Result:
        if original_name == new_name:
            return Result.of_failure("未更改，与原名一致")
        if self.is_daemon_name(new_name).is_success:
            return Result.of_failure("未更改，新名字与守护进程名称重复")
        if self.is_server_name(new_name).is_success:
            return Result.of_failure("未更改，新名字与实例名称重复")
        daemon, server = self.check_name(original_name, original_name)
        if daemon.is_fail and server.is_fail:
            return Result.of_failure(f"{original_name}不是一个有效的守护进程名称或实例名称")
        if daemon.is_success and server.is_success:
            return Result.of_failure(f"守护进程名称和实例名称出现重复,请检查")
        if daemon.is_success:
            self._stored_data["daemon_list"][new_name] = self._stored_data["daemon_list"].pop(original_name)
            self._stored_data["daemon_uuid"][new_name] = self._stored_data["daemon_uuid"].pop(original_name)
            self._daemon_uuid[new_name] = self._daemon_uuid.pop(original_name)
            self.write_data()
            return Result.of_success(f"修改守护进程名称[{original_name}] -> [{new_name}]")
        daemon_uuid = self.get_server_remote_uuid_by_name(original_name).message
        server_list = self._stored_data["servers"][daemon_uuid]
        server_list[new_name] = server_list.pop(original_name)
        self._server[daemon_uuid][new_name] = self._server[daemon_uuid].pop(original_name)
        self.write_data()
        return Result.of_success(f"修改实例名称[{original_name}] -> [{new_name}]")

    def stop(self, instance_name: str, remote_name: str = None, force_kill: bool = False) -> Result:
        daemon, server = self.check_name(remote_name, instance_name)
        if server.is_fail:
            return server
        instance_uuid = server.message
        if remote_name is not None:
            if daemon.is_fail:
                return daemon
            remote_uuid = daemon.message
        else:
            remote_uuid = self.get_server_remote_uuid_by_name(instance_name).message
        return self.stop_instance(remote_uuid, instance_uuid, force_kill)

    def start(self, instance_name: str, remote_name: str = None) -> Result:
        daemon, server = self.check_name(remote_name, instance_name)
        if server.is_fail:
            return server
        instance_uuid = server.message
        if remote_name is not None:
            if daemon.is_fail:
                return daemon
            remote_uuid = daemon.message
        else:
            remote_uuid = self.get_server_remote_uuid_by_name(instance_name).message
        return self.start_instance(remote_uuid, instance_uuid)

    def restart(self, instance_name: str, remote_name: str = None) -> Result:
        daemon, server = self.check_name(remote_name, instance_name)
        if server.is_fail:
            return server
        instance_uuid = server.message
        if remote_name is not None:
            if daemon.is_fail:
                return daemon
            remote_uuid = daemon.message
        else:
            remote_uuid = self.get_server_remote_uuid_by_name(instance_name).message
        return self.restart_instance(remote_uuid, instance_uuid)
