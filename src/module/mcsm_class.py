from bidict import bidict
from sys import exit
from time import strftime, localtime
from typing import Dict, List, Optional, Tuple, Union, overload
from requests import get
from asyncio.tasks import sleep
from src.base.logger import logger
from src.element.response import Response
from src.element.result import Result
from src.exception.exception import IncomingParametersError
from src.module.json_database import JsonDataBase
from src.type.response_body import RemoteServices, InstanceInfo
from src.type.types import HttpCode


class MCSMClass(JsonDataBase):
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
            if not response.success:
                match response.code:
                    case HttpCode.ERROR_PARAMS:
                        logger.error("访问参数错误")
                    case HttpCode.FORBIDDEN:
                        logger.error("Apikey错误")
                    case HttpCode.SERVER_ERROR:
                        logger.error("服务器出错")
                exit()
        except ConnectionError as err:
            logger.error("无法访问MCSM，请检查网络和url设置是否出错")
            logger.error(err)
            exit()

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
        logger.debug(f"HTTP请求：GET {url}")
        res = get(url=url, headers={"Content-Type": "application/json; charset=utf-8"},
                  params=param, timeout=10, verify=self._enable_SSL).json()
        return Response(res)

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

    def _status(self, code: int) -> str:
        return self._status_code[code + 1]

    def _translate_name_to_uuid(self, name: str) -> str:
        if name in self._name_to_uuid.keys():
            return self._name_to_uuid[name]["Service"]
        else:
            return self._name_to_uuid[self._stored_data[self._server_list_dict[name]][self._server_list_dict[name]]][
                name]

    def _get_remote_uuid(self, name: str) -> str:
        if name in self._name_to_uuid.keys():
            return self._name_to_uuid[name]["Service"]
        else:
            return self._server_list_dict[name]

    def _is_remote_name(self, name: str) -> int:
        if name in self._server_list_dict.keys():
            return 0
        elif name in self._name_to_uuid.keys():
            return 1
        else:
            return 2

    def is_daemon_name(self, name: str) -> Result:
        if name in self._daemon_uuid.keys():
            return Result.of_success(self._daemon_uuid[name])
        return Result.of_failure(f"{name}不是一个有效的守护进程名称")

    def is_server_name(self, name: str) -> Result:
        for k, v in self._server.items():
            for k_, v_ in v.items():
                if k_ == name:
                    return Result.of_success(k)
        return Result.of_failure(f"{name}不是一个有效的实例名称")

    def is_daemon_uuid(self, uuid: str) -> Result:
        if uuid in self._daemon_uuid.inverse.keys():
            return Result.of_success(self._daemon_uuid.inverse[uuid])
        return Result.of_failure(f"{uuid}不是一个有效的守护进程UUID")

    def is_server_uuid(self, uuid: str) -> Result:
        for k, v in self._server.items():
            for k_, v_ in v.inverse.items():
                if k_ == uuid:
                    return Result.of_success(k)
        return Result.of_failure(f"{uuid}不是一个有效的实例UUID")

    # 第一次封装
    def _get_instance_info(self, remote_uuid: str, instance_uuid: str) -> \
            Optional[Union[int, Response]]:
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
        data = self._get_instance_info(remote_uuid, instance_uuid)
        body = InstanceInfo(data.body)
        self._stored_data["daemon_list"][self._daemon_uuid.inverse[remote_uuid]]["instances"][
            instance_uuid] = body.data.status
        self.write_data()

    @overload
    def _check_name(self, remote_name: str, instance_name: str) -> List[Result]:
        ...

    def _check_name(self, remote_name: Optional[str] = None,
                    instance_name: Optional[str] = None) -> Union[Result, List[Result]]:
        if remote_name is None:
            if instance_name is None:
                return Result.of_failure("至少传入一个参数")
            return self.is_server_name(instance_name)
        if instance_name is None:
            return self.is_daemon_name(remote_name)
        res = []
        temp = self.is_daemon_name(remote_name)
        if temp.is_fail:
            return temp
        res.append(temp)
        temp = self.is_server_name(instance_name)
        if temp.is_fail:
            return temp
        res.append(temp)
        return res

    def _check_uuid(self, remote_uuid: str, instance_uuid: str) -> Tuple[Result, Result]:
        return self.is_daemon_uuid(remote_uuid), self.is_server_uuid(instance_uuid)

    def _start_instance(self, remote_uuid: str, instance_uuid: str) -> Result:
        daemon, server = self._check_uuid(remote_uuid, instance_uuid)
        if daemon.is_fail:
            return daemon
        if server.is_fail:
            return server
        self.update_instance_status(remote_uuid, instance_uuid)
        match self._stored_data["daemon_list"][server.message]["instances"][instance_uuid]:
            case -1:
                return Result.of_failure("实例状态未知，无法启动")
            case 0:
                res = self._call_api("/protected_instance/open", {"uuid": instance_uuid, "remote_uuid": remote_uuid})
                if res.success:
                    return Result.of_failure("执行成功，实例正在启动")
                return Result.of_failure(f"实例启动失败，api返回Code: {res.code}")
            case 1:
                return Result.of_failure("实例正在停止，无法启动")
            case 2:
                return Result.of_failure("实例正在启动中，请耐心等待")
            case 3:
                return Result.of_failure("实例已在运行")

    def _stop_instance(self, remote_uuid: str, instance_uuid: str, force_kill: bool = False) -> Result:
        daemon, server = self._check_uuid(remote_uuid, instance_uuid)
        if daemon.is_fail:
            return daemon
        if server.is_fail:
            return server
        self.update_instance_status(remote_uuid, instance_uuid)
        if force_kill:
            match self._stored_data["daemon_list"][server.message]["instances"][instance_uuid]:
                case -1:
                    return Result.of_failure("实例状态未知，无法启动")
                case 0:
                    return Result.of_failure("实例已停止，无法关闭")
            res = self._call_api("/api/protected_instance/kill", {"uuid": instance_uuid, "remote_uuid": remote_uuid})
            if res.success:
                return Result.of_failure("执行成功，强制关闭实例")
            return Result.of_failure(f"实例启动失败，api返回Code: {res.code}")
        else:
            match self._get_instance_info(remote_uuid, instance_uuid):
                case -1:
                    return "实例状态未知，无法关闭"
                case 0:
                    return "实例已停止，无法关闭"
                case 1:
                    return "实例正在停止，无法关闭"
                case 2:
                    return "实例正在启动中，无法关闭"
                case 3:
                    try:
                        self._call_api("/api/protected_instance/stop",
                                       {"uuid": instance_uuid, "remote_uuid": remote_uuid})
                    except RuntimeError as err:
                        logger.error(err)
                        return "关闭实例失败，api返回异常"
                    else:
                        return "执行成功，实例正在关闭"

    def _restart_instance(self, remote_uuid: str, instance_uuid: str) -> str:
        match self._get_instance_info(remote_uuid, instance_uuid):
            case -1:
                return "实例状态未知，无法重启"
            case 0:
                return "实例已停止，无法重启"
            case 1:
                return "实例正在停止，无法重启"
            case 2:
                return "实例正在启动中，无法重启"
            case 3:
                try:
                    self._call_api("/api/protected_instance/restart",
                                   {"uuid": instance_uuid, "remote_uuid": remote_uuid})
                except RuntimeError as err:
                    logger.error(err)
                    return "重启实例失败，api返回异常"
                else:
                    return "执行成功，实例正在重启"

    def _command(self, instance_uuid: str, remote_uuid: str, command: str) -> float:
        try:
            data = self._call_api("api/protected_instance/command", {
                "remote_uuid": remote_uuid,
                "uuid": instance_uuid,
                "command": command
            })
        except RuntimeError as err:
            logger.error(err)
            raise RuntimeError
        else:
            return data.get("time") / 1000

    def _get_command_output(self, instance_uuid: str, remote_uuid: str, time_stamp: float) -> str:
        try:
            data = self._call_api("/api/protected_instance/outputlog", {
                "remote_uuid": remote_uuid,
                "uuid": instance_uuid
            })
        except RuntimeError as err:
            logger.error(err)
            raise RuntimeError
        else:
            temp_list: list = []
            time = strftime("[%H:%M:%S]", localtime(time_stamp))
            data = data["data"].split('\n')
            for item in data:
                if time in item and "[Server thread/INFO]" in item:
                    temp_list.append(item)
            res: str = ""
            for raw in temp_list:
                if raw.find("]: ") != -1:
                    res += f"{raw[raw.find(']: ') + 3:]}\n"
            return res.removesuffix("\n")

    # 第二次封装
    def check_instance_status(self, instance_uuid: str, remote_name: str = None) -> str:
        res = self._check_name(remote_name, instance_uuid)
        if isinstance(res, bool):
            if remote_name is None:
                remote_uuid = self._get_remote_uuid(instance_uuid)
                remote_name = self._stored_data[remote_uuid][remote_uuid]
            else:
                remote_uuid = self._translate_name_to_uuid(remote_name)
            return f"守护进程名称: {remote_name}\n实例名称: {instance_uuid}\n实例运行状态: {self._status(self._get_instance_info(remote_uuid, self._translate_name_to_uuid(instance_uuid)))}"
        else:
            return res

    async def run_command(self, instance_name: str, remote_name: str, command: str) -> str:
        res = self._check_name(remote_name, instance_name)
        if isinstance(res, bool):
            instance_uuid = self._translate_name_to_uuid(instance_name)
            remote_uuid = self._translate_name_to_uuid(remote_name)
            status = self._get_instance_info(remote_uuid, instance_uuid)
            if status == 3:
                time_stamp = self._command(instance_uuid, remote_uuid, command)
                await sleep(1)
                return self._get_command_output(instance_uuid, remote_uuid, time_stamp)
            else:
                return f"实例当前状态是:{self._status(status)},无法执行命令"
        else:
            return res

    def list_instance(self, remote_name: str = None) -> str:
        result: str = ""
        if remote_name is None:
            for item in self._server:
                result += f"[{self._server[item]['name']}]\n"
                for raw in self._server[item]["instances"]:
                    result += f"{self._server[item]['instances'][raw]['name']} : {self._status(self._server[item]['instances'][raw]['status'])}\n"
            return result.removesuffix("\n")
        res = self._check_name(remote_name)
        if isinstance(res, bool):
            remote_uuid = self._translate_name_to_uuid(remote_name)
            result += f"[{remote_name}]\n"
            for raw in self._server[remote_uuid]["instances"]:
                result += f"{self._server[remote_uuid]['instances'][raw]['name']} : {self._status(self._server[remote_uuid]['instances'][raw]['status'])}\n"
            return result.removesuffix("\n")
        else:
            return res

    def rename(self, original_name: str, new_name: str) -> str:
        if original_name == new_name:
            return "未更改，与原名一致"
        if new_name in self._name_to_uuid.keys():
            return "未更改，新名字与守护进程名称重复"
        if new_name in self._server_list_dict.keys():
            return "未更改，新名字与实例名称重复"
        match self._is_remote_name(original_name):
            case 0:
                try:
                    remote_uuid = self._server_list_dict[original_name]
                    del self._server_list_dict[original_name]
                    self._server_list_dict[new_name] = remote_uuid
                    instance_uuid = self._name_to_uuid[self._server[remote_uuid]["name"]][original_name]
                    del self._name_to_uuid[self._server[remote_uuid]["name"]][original_name]
                    self._name_to_uuid[self._server[remote_uuid]["name"]][new_name] = instance_uuid
                    self._stored_data[remote_uuid][instance_uuid] = new_name
                    self.write_data()
                    self._server[remote_uuid]["instances"][instance_uuid]["name"] = new_name
                except:
                    return "修改名称失败"
                else:
                    return f"改名成功：\n[{original_name}] -> [{new_name}]"
            case 1:
                try:
                    remote_uuid = self._name_to_uuid[original_name]["Service"]
                    self._name_to_uuid[new_name] = self._name_to_uuid[original_name]
                    del self._name_to_uuid[original_name]
                    self._stored_data[remote_uuid][remote_uuid] = new_name
                    self.write_data()
                    self._server[remote_uuid]["name"] = new_name
                except:
                    return "修改名称失败"
                else:
                    return f"改名成功：\n[{original_name}] -> [{new_name}]"
            case 2:
                return f"{original_name}不是一个有效的守护进程名称或实例名称"

    def stop(self, instance_name: str, remote_name: str = None, force_kill: bool = False) -> str:
        res = self._check_name(remote_name, instance_name)
        if isinstance(res, bool):
            if remote_name is None:
                return self._stop_instance(self._server_list_dict[instance_name],
                                           self._translate_name_to_uuid(instance_name), force_kill)
            else:
                return self._stop_instance(self._translate_name_to_uuid(remote_name),
                                           self._translate_name_to_uuid(instance_name), force_kill)
        else:
            return res

    def start(self, instance_name: str, remote_name: str = None) -> str:
        res = self._check_name(remote_name, instance_name)
        if isinstance(res, bool):
            if remote_name is None:
                return self._start_instance(self._server_list_dict[instance_name],
                                            self._translate_name_to_uuid(instance_name))
            else:
                return self._start_instance(self._translate_name_to_uuid(remote_name),
                                            self._translate_name_to_uuid(instance_name))
        else:
            return res

    def restart(self, instance_name: str, remote_name: str = None) -> str:
        res = self._check_name(remote_name, instance_name)
        if isinstance(res, bool):
            if remote_name is None:
                return self._restart_instance(self._server_list_dict[instance_name],
                                              self._translate_name_to_uuid(instance_name))
            else:
                return self._restart_instance(self._translate_name_to_uuid(remote_name),
                                              self._translate_name_to_uuid(instance_name))
        else:
            return res

# 数据结构备忘
# self.__NameToUUID
# {
#   'Server2': {
#     'Service': '40c4a15d59af40b38c4147340445c1d3',
#     'Velocity': '9fda84e890de4d64bc51ad8ea7633c75'
#   },
#   'Server1': {
#     'Service': 'df473f5da63640b9b4617e4cde3f0a8e',
#     '原版服-1.18.1': '6856f8a753ff4317a1f03f3bee0ae93c'
#   }
# }
# self.__ServerListDict
# {
#   'Velocity': '40c4a15d59af40b38c4147340445c1d3',
#   '原版服-1.18.1': 'df473f5da63640b9b4617e4cde3f0a8e'
# }
# self.__Server
# {
#   '40c4a15d59af40b38c4147340445c1d3': {
#     'name': 'Server2',
#     'instances': {
#       '9fda84e890de4d64bc51ad8ea7633c75': {
#         'name': 'Velocity',
#         'status': 3
#       }
#     }
#   },
#   'df473f5da63640b9b4617e4cde3f0a8e': {
#     'name': 'Server1',
#     'instances': {
#       '6856f8a753ff4317a1f03f3bee0ae93c': {
#         'name': '原版服-1.18.1',
#         'status': 3
#       }
#     }
#   }
# }
# self.Data(存入文件)
# {
#   '40c4a15d59af40b38c4147340445c1d3': {
#     '40c4a15d59af40b38c4147340445c1d3': 'Server2',
#     '9fda84e890de4d64bc51ad8ea7633c75': 'Velocity'
#   },
#   'df473f5da63640b9b4617e4cde3f0a8e': {
#     'df473f5da63640b9b4617e4cde3f0a8e': 'Server1',
#     '6856f8a753ff4317a1f03f3bee0ae93c': '原版服-1.18.1'
#   }
# }
