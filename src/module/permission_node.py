from typing import Optional, Union

from src.base.config import ConfigSet
from src.module.json_database import DataType, JsonDataBase
from src.module.permissions import *
from src.module.result import Result


class PermissionManager(JsonDataBase):
    _group_permission: JsonDataBase
    _permission_node_list: list

    def __init__(self) -> None:
        """
        类构造函数
        """
        super().__init__("permission.json", DataType.DICT)
        self._group_permission = JsonDataBase("permissionGroup.json", DataType.DICT)
        if self._group_permission._stored_data == {}:
            self._group_permission._stored_data = ConfigSet.load_config("permission.json5")
            self._group_permission.write_data()
        # self._permission_node_list = (Mcsm.get_all_permission_node() + Permission.get_all_permission_node()
        #                               + Blacklist.get_all_permission_node() + Whitelist.get_all_permission_node()
        #                               + Token.get_all_permission_node() + Question.get_all_permission_node())

    def reload_group_permission(self, over_write: bool = False) -> Result:
        """
        重新从配置文件中加载权限组配置\n
        Args:
            over_write: 是覆盖模式还是追加模式，默认为追加
        Returns:
            返回执行状态
        """
        try:
            if over_write:
                self._group_permission._stored_data = ConfigSet.load_config("permission.json5")
                self._group_permission.write_data()
                return Result.of_success("重载权限组成功")
            raw: str
            data: dict = ConfigSet.load_config("permission.json5")
            for raw in data:
                if raw in self._group_permission._stored_data.keys():
                    temp = data[raw]["permission"]
                    for item in temp:
                        if item not in self._group_permission._stored_data[raw]["permission"]:
                            self._group_permission._stored_data[raw]["permission"].append(item)
                    if "parent" in data[raw].keys():
                        if "parent" in self._group_permission._stored_data[raw].keys():
                            temp = data[raw]["parent"]
                            for item in temp:
                                if item not in self._group_permission._stored_data[raw]["parent"]:
                                    self._group_permission._stored_data[raw]["parent"].append(item)
                            continue
                        self._group_permission._stored_data[raw]["parent"] = data[raw]["parent"]
                        continue
                self._group_permission._stored_data[raw] = data[raw]
            self._group_permission.write_data()
            return Result.of_success("重载权限组成功")
        except:
            return Result.of_failure("重载权限组失败")

    def get_group_permission(self, group_name: str, raw_content: bool = False) -> list:
        """
        获取权限组的所有权限（包括继承的权限组）\n
        Args:
            group_name: 要查询的组名，可以单个也可以用列表
            raw_content
        Returns:
            返回权限节点列表
        """
        try:
            if group_name not in self._group_permission._stored_data.keys():
                return []
            result: list = []
            if "parent" in self._group_permission._stored_data[group_name].keys():
                result += self._get_group_permission(self._group_permission._stored_data[group_name]["parent"])
                if not raw_content:
                    result = self._permission_del(result)
            if "permission" in self._group_permission._stored_data[group_name].keys():
                result += self._group_permission._stored_data[group_name]["permission"]
                if not raw_content:
                    result = self._permission_del(result)
            return result
        except:
            return []

    def get_player_permission(self, user_id: str, raw_content: bool = False) -> list:
        """
        获取某个玩家的全部权限\n
        Args:
            user_id: 玩家id
            raw_content
        Returns:
            返回权限节点列表
        """
        try:
            if user_id not in self._stored_data.keys():
                return []
            result: list = []
            if "group" in self._stored_data[user_id].keys():
                result += self._get_group_permission(self._stored_data[user_id]["group"])
                if not raw_content:
                    result = self._permission_del(result)
            if "permission" in self._stored_data[user_id].keys():
                result += self._stored_data[user_id]["permission"]
                if not raw_content:
                    result = self._permission_del(result)
            return result
        except:
            return []

    def add_player_permission(self, user_id: str, permission: str) -> Result:
        """
        向某个玩家添加一个权限节点\n
        Args:
            user_id: 玩家id
            permission: 要添加的权限节点
        Returns:
            执行信息
        """
        try:
            if user_id not in self._stored_data.keys():
                self._stored_data[user_id] = {
                    "group": ["default"],
                    "permission": [permission]
                }
                return Result.of_success(f"成功为「{user_id}」添加权限「{permission}」")
            permissions = self.get_player_permission(user_id)
            if permission in permissions:
                return Result.of_failure(f"「{user_id}」已有「{permission}」权限")
            if f"-{permission}" in self._stored_data[user_id]["permission"]:
                self._stored_data[user_id]["permission"].remove(f"-{permission}")
            self._stored_data[user_id]["permission"].append(permission)
            self.write_data()
            return Result.of_success(f"成功为「{user_id}」添加权限「{permission}」")
        except:
            return Result.of_failure(f"向「{user_id}」添加权限「{permission}」失败")

    def remove_player_permission(self, user_id: str, permission: str) -> Result:
        """
        移除某个玩家的某个权限节点\n
        Args:
            user_id: 玩家id
            permission: 权限节点
        Returns:
            执行结果
        """
        try:
            if user_id not in self._stored_data.keys():
                return Result.of_failure(f"无法找到用户「{user_id}」的权限信息")
            if f"-{permission}" in self._stored_data[user_id]["permission"]:
                return Result.of_failure(f"此用户没有「{permission}」权限")
            if permission in self._stored_data[user_id]["permission"]:
                self._stored_data[user_id]["permission"].remove(permission)
            else:
                if self._stored_data[user_id]["permission"]:
                    self._stored_data[user_id]["permission"].append(f"-{permission}")
                else:
                    self._stored_data[user_id]["permission"] = [f"-{permission}"]
            self.write_data()
            return Result.of_success(f"成功移除「{user_id}」权限「{permission}」")
        except:
            return Result.of_failure(f"移除「{user_id}」的权限「{permission}」失败")

    def check_player_permission(self, user_id: Union[str, int], permission: str) -> Result:
        """
        检查玩家是否拥有某一权限节点\n
        Args:
            user_id: 玩家id
            permission: 权限节点
        Returns:
            拥有Ture 未拥有False
        """
        user_id = str(user_id)
        try:
            if user_id not in self._stored_data.keys():
                return Result.of_failure()
            if f"-{permission}" in self._stored_data[user_id]["permission"]:
                return Result.of_failure()
            data: list = self.get_player_permission(user_id)
            return Result(self._check_permission(data, permission))
        except:
            return Result.of_failure()

    def clone_player_permission(self, from_id: str, to_id: str) -> Result:
        """
        克隆某一玩家的权限\n
        Args:
            from_id: 克隆对象id
            to_id: 克隆目标id
        Returns:
            返回执行消息
        """
        try:
            if from_id not in self._stored_data.keys():
                return Result.of_failure(f"无法查询到「{from_id}」的权限记录")
            self._stored_data[to_id] = self._stored_data[from_id]
            self.write_data()
            return Result.of_success(f"成功将「{from_id}」的权限克隆到「{to_id}」")
        except:
            return Result.of_failure("克隆权限时出现错误")

    def get_player_info(self, user_id: str) -> Optional[dict]:
        """
        获取玩家所有权限信息\n
        Args:
            user_id: 目标玩家id
        Returns:
            如果玩家不存在返回None，存在返回字典
        """
        if user_id in self._stored_data.keys():
            return self._stored_data[user_id]
        return None

    def get_group_info(self, group_name: str) -> Optional[dict]:
        """
        获取某一权限组所有权限信息\n
        Args:
            group_name: 权限组id
        Returns:
            如果权限组不存在返回None，存在返回字典
        """
        if group_name in self._group_permission._stored_data.keys():
            return self._group_permission._stored_data[group_name]
        return None

    def clone_group_permission(self, from_group: str, to_group: str) -> Result:
        """
        克隆某一权限组的权限到另一权限组\n
        Args:
            from_group: 克隆对象权限组名
            to_group: 克隆目标权限组名
        Returns:
            返回执行消息
        """
        try:
            if from_group not in self._group_permission._stored_data.keys():
                return Result.of_failure(f"权限组「{from_group}」不存在")
            self._group_permission._stored_data[to_group] = self._group_permission._stored_data[from_group]
            self._group_permission.write_data()
            return Result.of_success(f"成功将权限组「{from_group}」的权限克隆到「{from_group}」")
        except:
            return Result.of_failure("克隆权限时出现错误")

    @property
    def permission_node(self) -> list:
        """
        获得所有的权限节点列表\n
        Returns:
            返回所有的权限节点列表
        """
        return self._permission_node_list

    def add_group_permission(self, group_name: str, permission: str) -> Result:
        """
        向权限组内添加权限\n
        Args:
            group_name: 权限组名
            permission: 权限节点名
        Returns:
            执行结果
        """
        try:
            if group_name not in self._group_permission._stored_data.keys():
                self._group_permission._stored_data[group_name] = {
                    "permission": [
                        permission
                    ]
                }
            else:
                permissions = self.get_group_permission(group_name)
                if permission in permissions:
                    return Result.of_success(f"权限组「{group_name}」已有「{permission}」权限")
                if self._group_permission._stored_data[group_name]["permission"]:
                    self._group_permission._stored_data[group_name]["permission"].append(permission)
                else:
                    self._group_permission._stored_data[group_name]["permission"] = [permission]
            self._group_permission.write_data()
            return Result.of_success(f"成功向权限组「{group_name}」添加权限「{permission}」")
        except:
            return Result.of_failure(f"向权限组「{group_name}」添加权限「{permission}」失败")

    def remove_group_permission(self, group_name: str, permission: str) -> Result:
        """
        从权限组内移除权限\n
        Args:
            group_name: 权限组名
            permission: 权限节点名
        Returns:
            执行结果
        """
        try:
            if group_name not in self._group_permission._stored_data.keys():
                return Result.of_failure(f"权限组「{group_name}」不存在")
            if f"-{permission}" in self._group_permission._stored_data[group_name]["permission"]:
                return Result.of_failure(f"权限组「{group_name}」未拥有「{permission}」权限")
            if permission in self._group_permission._stored_data[group_name]["permission"]:
                self._group_permission._stored_data[group_name]["permission"].remove(permission)
            else:
                if self._group_permission._stored_data[group_name]["permission"]:
                    self._group_permission._stored_data[group_name]["permission"].append(f"-{permission}")
                else:
                    self._group_permission._stored_data[group_name]["permission"] = [f"-{permission}"]
            self._group_permission.write_data()
            return Result.of_success(f"成功移除权限组「{group_name}」权限「{permission}」")
        except:
            return Result.of_failure(f"移除权限组「{group_name}」的权限「{permission}」失败")

    def check_group_permission(self, group_name: str, permission: str) -> Result:
        """
        检查某一权限组是否拥有某一权限\n
        Args:
            group_name: 权限组名
            permission: 权限节点名
        Returns:
            拥有True 未拥有 False
        """
        try:
            if f"-{permission}" in self._group_permission._stored_data[group_name]["permission"]:
                return Result.of_failure()
            data = self.get_group_permission(group_name)
            return Result(self._check_permission(data, permission))
        except:
            return Result.of_failure()

    def add_group_parent(self, group_name: str, parent_group: str) -> Result:
        """
        向某一权限组内添加父权限组\n
        Args:
            group_name: 权限组名
            parent_group: 父权限组名
        Returns:
            返回运行结果
        """
        try:
            if parent_group not in self._group_permission._stored_data.keys():
                return Result.of_failure(f"权限组「{parent_group}」不存在")
            if group_name not in self._group_permission._stored_data.keys():
                self._group_permission._stored_data[group_name] = {
                    "parent": [parent_group]
                }
                return Result.of_failure(f"无法找到目标权限组「{group_name}」,已自动创建")
            if "parent" in self._group_permission._stored_data[group_name].keys():
                self._group_permission._stored_data[group_name]["parent"].append(parent_group)
            else:
                self._group_permission._stored_data[group_name]["parent"] = [parent_group]
            return Result.of_success(f"成功为权限组「{group_name}」添加父权限组「{parent_group}」")
        except:
            return Result.of_failure(f"向权限组「{group_name}」添加父权限组「{parent_group}」失败")
        finally:
            self._group_permission.write_data()

    def remove_group_parent(self, group_name: str, parent_group: str) -> Result:
        """
        从某一权限组内移除父权限组\n
        Args:
            group_name: 权限组名
            parent_group: 父权限组名
        Returns:
            执行结果
        """
        try:
            if parent_group not in self._group_permission._stored_data.keys():
                return Result.of_failure(f"权限组「{parent_group}」不存在")
            if group_name not in self._group_permission._stored_data.keys():
                return Result.of_failure(f"权限组「{group_name}」不存在")
            if "parent" not in self._group_permission._stored_data[group_name]:
                return Result.of_failure(f"权限组「{group_name}」还没有父权限组")
            self._group_permission._stored_data[group_name]["parent"].remove(parent_group)
            self._group_permission.write_data()
            return Result.of_success(f"成功移除权限组「{group_name}」父权限组「{parent_group}」")
        except:
            return Result.of_failure(f"移除权限组「{group_name}」父权限组「{parent_group}」失败")

    def add_player_parent(self, user_id: str, parent_group: str) -> Result:
        """
        为玩家添加继承权限组\n
        Args:
            user_id: 玩家ID
            parent_group: 要继承的权限组
        Returns:
            返回执行结果
        """
        try:
            if parent_group not in self._group_permission._stored_data.keys():
                return Result.of_failure(f"权限组「{parent_group}」不存在")
            if user_id not in self._stored_data.keys():
                self._stored_data[user_id] = {
                    "group": [parent_group]
                }
                return Result.of_failure(f"无法找到目标「{user_id}」,已自动创建")
            if "group" in self._stored_data[user_id].keys():
                self._stored_data[user_id]["group"].append(parent_group)
            else:
                self._stored_data[user_id]["group"] = [parent_group]
            return Result.of_success(f"向用户「{user_id}」添加权限组「{parent_group}」成功")
        except:
            return Result.of_failure(f"向用户「{user_id}」添加权限组「{parent_group}」失败")
        finally:
            self.write_data()

    def remove_player_parent(self, user_id: str, parent_group: str) -> Result:
        """
        移除玩家继承的权限组\n
        Args:
            user_id: 玩家ID
            parent_group: 要移除的父权限组
        Returns:
            执行结果
        """
        try:
            if parent_group not in self._group_permission._stored_data.keys():
                return Result.of_failure(f"权限组「{parent_group}」不存在")
            if user_id not in self._stored_data.keys():
                return Result.of_failure(f"用户「{user_id}」未被设置过权限组")
            if "group" not in self._stored_data[user_id].keys():
                return Result.of_failure(f"用户「{user_id}」未被设置过权限组")
            self._stored_data[user_id]["group"].remove(parent_group)
            self.write_data()
            return Result.of_success(f"移除用户「{user_id}」权限组「{parent_group}」成功")
        except:
            return Result.of_failure(f"移除用户「{user_id}」权限组「{parent_group}」失败")

    def del_group(self, group_name: str) -> Result:
        """
        删除权限组\n
        Args:
            group_name: 要删除的权限组名
        Returns:
            返回执行结果
        """
        try:
            if group_name not in self._group_permission._stored_data.keys():
                return Result.of_failure(f"权限组「{group_name}」不存在")
            del self._group_permission._stored_data[group_name]
            self._group_permission.write_data()
            return Result.of_success(f"成功删除权限组：{group_name}")
        except:
            return Result.of_failure(f"删除权限组「{group_name}」失败")

    def del_player(self, user_id: str) -> Result:
        """
        删除某一玩家\n
        Args:
            user_id: 玩家id
        Returns:
            返回执行结果
        """
        try:
            if user_id not in self._stored_data.keys():
                return Result.of_failure(f"无法找到用户「{user_id}」")
            del self._stored_data[user_id]
            self.write_data()
            return Result.of_success(f"成功删除用户：「{user_id}」")
        except:
            return Result.of_failure(f"删除用户「{user_id}」失败")

    def set_player_parent(self, user_id: str, group_name: Union[str, list] = None) -> Result:
        """
        为某一玩家设置权限组\n
        Args:
            user_id: 玩家id
            group_name: 要设置的权限名
        Returns:
            执行结果
        """
        try:
            if user_id not in self._stored_data.keys():
                return Result.of_failure(f"无法找到用户「{user_id}」")
            if group_name is None:
                self._stored_data[user_id]["group"] = []
            elif isinstance(group_name, str):
                self._stored_data[user_id]["group"] = [group_name]
            elif isinstance(group_name, list):
                self._stored_data[user_id]["group"] = group_name
            else:
                raise ValueError
            self.write_data()
            return Result.of_success(f"设置「{user_id}」的权限组为「{str(group_name)}」")
        except:
            return Result.of_failure(f"设置「{user_id}」的权限组失败")

    def create_group(self, group_name: str, group: str = None) -> Result:
        """
        创建权限组\n
        Args:
            group_name: 权限组名
            group: 初始继承的权限组
        Returns:
            执行结果
        """
        if group_name in self._group_permission._stored_data.keys():
            return Result.of_failure(f"权限组「{group_name}」已存在")
        self._group_permission._stored_data[group_name] = {
            "parent": [group if group else "default"],
            "permission": []
        }
        self._group_permission.write_data()
        return Result.of_success(f"权限组「{group_name}」创建成功")

    def create_player(self, user_id: str, group: str = None) -> Result:
        """
        创建玩家\n
        Args:
            user_id: 玩家ID
            group: 初始继承的权限组
        Returns:
            执行结果
        """
        if user_id in self._stored_data.keys():
            return Result.of_failure(f"用户「{user_id}」已存在")
        self._stored_data[user_id] = {
            "group": [group if group else "default"],
            "permission": []
        }
        self.write_data()
        return Result.of_success(f"用户「{user_id}」添加成功")

    @staticmethod
    def _permission_del(data: list, remove_all: bool = False) -> list:
        need_del: set = set({})
        for raw in data:
            if raw in need_del:
                continue
            if raw == "-*.*":
                return []
            if raw.startswith("-"):
                origin = len(need_del)
                permission = raw[1:].split(".")
                length = len(permission)
                if permission[length - 1] == "*":
                    permission_prefix = f"{'.'.join(permission[:-1])}."
                    for i in data:
                        if i in need_del:
                            continue
                        if i.startswith(permission_prefix):
                            need_del.add(i)
                elif raw[1:] in data:
                    need_del.add(raw[1:])
                if remove_all or origin != len(need_del):
                    need_del.add(raw)
        return list(filter(lambda x: x not in need_del, data))

    @staticmethod
    def _check_permission(data: list, permission: str) -> bool:
        if "*.*" in data:
            return True
        if permission == "*.*":
            return permission in data
        temp = permission.split(".")
        length = len(temp)
        if length <= 1 or "*" in temp[:-1] or permission == ".".join("*" * length):
            raise ValueError(permission)
        for i in range(1, length):
            if f"{'.'.join(temp[:i])}.*" in data:
                return True
        return permission in data

    def _get_group_permission(self, group_name: Union[list, str]) -> list:
        """
        获取权限组的所有权限（包括继承的权限组）\n
        Args:
            group_name: 要查询的组名，可以单个也可以用列表
        Returns:
            返回权限节点列表
        """

        result = []
        name: str
        if not isinstance(group_name, list):
            group_name = [group_name]
        for name in group_name:
            if name in self._group_permission._stored_data.keys():
                if "parent" in self._group_permission._stored_data[name].keys():
                    result += self._get_group_permission(self._group_permission._stored_data[name]["parent"])
                result += self._group_permission._stored_data[name]["permission"]
        return list(set(result))
