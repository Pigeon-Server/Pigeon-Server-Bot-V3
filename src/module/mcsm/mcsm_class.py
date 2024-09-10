from datetime import datetime

from re import sub
from sys import exit
from typing import Optional
from requests import get
from asyncio.tasks import sleep

from src.base.config import config
from src.base.logger import logger
from src.element.response import Response
from src.element.result import Result
from src.exception.exception import IncomingParametersError
from src.module.database.database_adapter import DatabaseAdapter
from src.module.json_database import DataType, JsonDataBase
from src.module.mcsm.mcsm_info_mysql_manager import McsmInfoMySQLManager
from src.module.mcsm.mcsm_info_json_manager import McsmInfoJsonManager
from src.module.mcsm.mcsm_info_manager import McsmInfoManager
from src.module.mcsm.mcsm_info_sqlite_manager import McsmInfoSqliteManager
from src.type.response_body import RemoteServices, InstanceInfo
from src.type.types import DataEngineType, HttpCode


class McsmManager(JsonDataBase):
    _api_url: str = None
    _api_key: str = None
    _enable_SSL: bool = True
    _status_code: list[str] = ["状态未知", "已停止", "停止中", "启动中", "运行中"]
    _info_manager: McsmInfoManager

    def __init__(self, apikey: str, url: str = "http://127.0.0.1:23333", enable_ssl: bool = False,
                 use_database: bool = False, database_instance: Optional[DatabaseAdapter] = None) -> None:
        """
        Args:
            apikey: API 接口密钥
            url: MCSM网页端后台地址（跨域请求 API 接口须打开）
            enable_ssl: 是否启用ssl连接（注意：如果网页是http访问，则此选项永远为False）
        """
        super().__init__("mcsm.json", DataType.DICT)
        if not url.startswith("http"):
            raise IncomingParametersError("api地址错误,必须以http或https开头")
        self._enable_SSL = False if url.startswith("http://") else enable_ssl
        self._api_url = url if "/api" in url else f"{url}/api"
        self._api_key = apikey
        if config.sys_config.mcsm.use_database:
            match database_instance.get_database_type():
                case DataEngineType.MYSQL:
                    self._info_manager = McsmInfoMySQLManager(database_instance)
                case DataEngineType.SQLITE:
                    self._info_manager = McsmInfoSqliteManager(database_instance)
                case DataEngineType.JSON:
                    self._info_manager = McsmInfoJsonManager()
        else:
            self._info_manager = McsmInfoJsonManager()
        self.test_connect()
        self.get_mcsm_info()

    def test_connect(self) -> bool:
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
            return True
        except ConnectionError as err:
            logger.error(err)
            logger.critical("无法访问MCSM，请检查网络和url设置是否出错")
            return False

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
        data = self._call_api("service/remote_services")
        body = RemoteServices(data.body)
        self._info_manager.update_mcsm_info(body, force_load)

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
            self._info_manager.update_remote_status(remote_uuid, body)
            return
        if remote_uuid is None:
            raise RuntimeError("传入参数错误")
        data = self.get_instance_info(remote_uuid, instance_uuid)
        body = InstanceInfo(data.body)
        self._info_manager.update_instance_status(remote_uuid, instance_uuid, body)

    def start_instance(self, remote_uuid: str, instance_uuid: str) -> Result:
        daemon, server = self._info_manager.check_uuid(remote_uuid, instance_uuid)
        if daemon.is_fail:
            return daemon
        if server.is_fail:
            return server
        self.update_instance_status(remote_uuid, instance_uuid)
        match self._info_manager.get_server_status(daemon.message, instance_uuid):
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
        daemon, server = self._info_manager.check_uuid(remote_uuid, instance_uuid)
        if daemon.is_fail:
            return daemon
        if server.is_fail:
            return server
        self.update_instance_status(remote_uuid, instance_uuid)
        match self._info_manager.get_server_status(daemon.message, instance_uuid):
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
        daemon, server = self._info_manager.check_uuid(remote_uuid, instance_uuid)
        if daemon.is_fail:
            return daemon
        if server.is_fail:
            return server
        self.update_instance_status(remote_uuid, instance_uuid)
        match self._info_manager.get_server_status(daemon.message, instance_uuid):
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
            if time in item:
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
        daemon, server = self._info_manager.check_name(remote_name, instance_name)
        if server.is_fail:
            return server
        instance_uuid = server.message
        if remote_name is None:
            remote_uuid = self._info_manager.get_remote_uuid_by_instance_name(instance_name).message
            remote_name = self._info_manager.is_daemon_uuid(remote_uuid).message
        else:
            if daemon.is_fail:
                return daemon
            remote_uuid = daemon.message
        self.update_instance_status(remote_uuid, instance_uuid)
        return Result.of_success(f"守护进程名称: {remote_name}\n"
                                 f"实例名称: {instance_name}\n"
                                 f"实例状态: {self._info_manager.status(self._info_manager.get_server_status(remote_name, instance_uuid))}")

    async def run_command(self, instance_name: str, command: str) -> Result:
        _, server = self._info_manager.check_name(instance_name=instance_name)
        if server.is_fail:
            return server
        remote_uuid = self._info_manager.get_remote_uuid_by_instance_name(instance_name).message
        instance_uuid = server.message
        self.update_instance_status(remote_uuid, instance_uuid)
        status = self._info_manager.get_server_status(self._info_manager.is_daemon_uuid(remote_uuid).message,
                                                      instance_uuid)
        if status != 3:
            return Result.of_failure(f"实例当前状态是:{self._info_manager.status(status)},无法执行命令")
        time_stamp = self._command(instance_uuid, remote_uuid, command)
        await sleep(1)
        return self._get_command_output(instance_uuid, remote_uuid, time_stamp)

    def list_instance(self, remote_name: str = None) -> Result:
        if remote_name is None:
            self.update_instance_status()
            return self._info_manager.list_all_instances()
        daemon, _ = self._info_manager.check_name(remote_name)
        if daemon.is_fail:
            return daemon
        remote_uuid = daemon.message
        self.update_instance_status(remote_uuid)
        return self._info_manager.list_remote_instances(remote_uuid, remote_name)

    def rename(self, original_name: str, new_name: str) -> Result:
        if original_name == new_name:
            return Result.of_failure("未更改，与原名一致")
        if self._info_manager.is_daemon_name(new_name).is_success:
            return Result.of_failure("未更改，新名字与守护进程名称重复")
        if self._info_manager.is_server_name(new_name).is_success:
            return Result.of_failure("未更改，新名字与实例名称重复")
        daemon, server = self._info_manager.check_name(original_name, original_name)
        if daemon.is_fail and server.is_fail:
            return Result.of_failure(f"{original_name}不是一个有效的守护进程名称或实例名称")
        if daemon.is_success and server.is_success:
            return Result.of_failure(f"守护进程名称和实例名称出现重复,请检查")
        if daemon.is_success:
            return self._info_manager.rename_remote(original_name, new_name)
        return self._info_manager.rename_instance(original_name, new_name)

    def stop(self, instance_name: str, remote_name: str = None, force_kill: bool = False) -> Result:
        daemon, server = self._info_manager.check_name(remote_name, instance_name)
        if server.is_fail:
            return server
        instance_uuid = server.message
        if remote_name is not None:
            if daemon.is_fail:
                return daemon
            remote_uuid = daemon.message
        else:
            remote_uuid = self._info_manager.get_remote_uuid_by_instance_name(instance_name).message
        return self.stop_instance(remote_uuid, instance_uuid, force_kill)

    def start(self, instance_name: str, remote_name: str = None) -> Result:
        daemon, server = self._info_manager.check_name(remote_name, instance_name)
        if server.is_fail:
            return server
        instance_uuid = server.message
        if remote_name is not None:
            if daemon.is_fail:
                return daemon
            remote_uuid = daemon.message
        else:
            remote_uuid = self._info_manager.get_remote_uuid_by_instance_name(instance_name).message
        return self.start_instance(remote_uuid, instance_uuid)

    def restart(self, instance_name: str, remote_name: str = None) -> Result:
        daemon, server = self._info_manager.check_name(remote_name, instance_name)
        if server.is_fail:
            return server
        instance_uuid = server.message
        if remote_name is not None:
            if daemon.is_fail:
                return daemon
            remote_uuid = daemon.message
        else:
            remote_uuid = self._info_manager.get_remote_uuid_by_instance_name(instance_name).message
        return self.restart_instance(remote_uuid, instance_uuid)

    def status(self) -> Result:
        daemon, instance = self._info_manager.get_number()
        return Result.of_success((f"Mcsm:\n "
                                  f"\t状态：{'已启用' if config.sys_config.mcsm.enable else '未启用'}\n"
                                  f"\t数据引擎: {self._info_manager.data_engine.value}\n"
                                  f"\tAPI状态: {'正常' if self.test_connect() else '异常'}\n"
                                  f"\t数据引擎状态: {'正常' if self._info_manager.test() else '异常'}\n"
                                  f"\t守护进程数量: {daemon}\n"
                                  f"\t实例数量: {instance}\n"))
