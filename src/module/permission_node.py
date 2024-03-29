from typing import Optional, Union

from src.base.config import ConfigSet
from src.module.json_database import JsonDataBase
from src.module.permissions import *


class PermissionClass(JsonDataBase):
    _group_permission: JsonDataBase
    _permission_node_list: list

    def __init__(self) -> None:
        """
        类构造函数
        """
        super().__init__("permission.json", 5)
        self._group_permission = JsonDataBase("permissionGroup.json", 5)
        if self._group_permission._stored_data == {}:
            self._group_permission._stored_data = self.load_config("permission.json5")
            self._group_permission.write_data()
        self._permission_node_list = Mcsm.get_all_permission_node()
        self._permission_node_list += Permission.get_all_permission_node()
        self._permission_node_list += Blacklist.get_all_permission_node()
        self._permission_node_list += Whitelist.get_all_permission_node()
        self._permission_node_list += Token.get_all_permission_node()
        self._permission_node_list += Question.get_all_permission_node()
        self.n = 0

    def reload_group_permission(self, over_write: bool = False) -> str:
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
            else:
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
                            else:
                                self._group_permission._stored_data[raw]["parent"] = data[raw]["parent"]
                    else:
                        self._group_permission._stored_data[raw] = data[raw]
                self._group_permission.write_data()
        except:
            return "重载权限组失败"
        else:
            return "重载权限组成功"

    def get_group_permission(self, group_name: Union[list, str]) -> list:
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
            group_name = list(group_name)
        for name in group_name:
            if name in self._group_permission._stored_data.keys():
                if "parent" in self._group_permission._stored_data[name].keys():
                    result += self.get_group_permission(self._group_permission._stored_data[name]["parent"])
                result += self._group_permission._stored_data[name]["permission"]
        return list(set(result))

    def get_player_permission(self, user_id: str) -> list:
        """
        获取某个玩家的全部权限\n
        Args:
            user_id: 玩家id
        Returns:
            返回权限节点列表
        """
        try:
            if user_id in self._stored_data.keys():
                result: list = []
                if "permission" in self._stored_data[user_id].keys():
                    result += self._stored_data[user_id]["permission"]
                if "group" in self._stored_data[user_id].keys():
                    result += self.get_group_permission(self._stored_data[user_id]["group"])
                return result
            else:
                return []
        except:
            return []

    def add_player_permission(self, user_id: str, permission: str) -> str:
        """
        向某个玩家添加一个权限节点\n
        Args:
            user_id: 玩家id
            permission: 要添加的权限节点
        Returns:
            执行信息
        """
        try:
            if user_id in self._stored_data.keys():
                if "group" in self._stored_data[user_id]:
                    userPermission = self.get_group_permission(self._stored_data[user_id]["group"]) + self._stored_data[user_id]["permission"]
                else:
                    userPermission = self._stored_data[user_id]["permission"]
                if permission in userPermission:
                    return f"此用户已有{permission}权限" if permission in self._stored_data[user_id]["permission"] else "该用户下某一用户组具有该权限"
                else:
                    self._stored_data[user_id]["permission"].append(permission)
            else:
                self._stored_data[user_id] = {
                    "group": ["default"],
                    "permission": [permission]
                }
            self.write_data()
        except:
            return f"向「{user_id}」添加权限“{permission}”失败"
        else:
            return f"成功为「{user_id}」添加权限”{permission}“"

    def remove_player_permission(self, user_id: str, permission: str) -> str:
        """
        移除某个玩家的某个权限节点\n
        Args:
            user_id: 玩家id
            permission: 权限节点
        Returns:
            执行结果
        """
        try:
            if user_id in self._stored_data.keys():
                if permission in self._stored_data[user_id]["permission"]:
                    self._stored_data[user_id]["permission"].remove(permission)
                else:
                    return f"此用户没有“{permission}”权限"
            self.write_data()
        except:
            return f"移除「{user_id}」的权限”{permission}“失败"
        else:
            return f"成功移除「{user_id}」权限“{permission}”"

    def check_player_permission(self, user_id: str, permission: str) -> bool:
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
            if user_id in self._stored_data.keys():
                # data: list = self.Data[userId]["permission"] 错误用法！！！！！！！！！！！！！！！！！！！！
                data: list = []
                data += self._stored_data[user_id]["permission"]
                if "group" in self._stored_data[user_id].keys():
                    data += self.get_group_permission(self._stored_data[user_id]["group"])
                if f"-{permission}" in data:
                    return False
                data = self._permission_del(data)
                if "*.*" in data:
                    return True
                return self._check_permission(data, permission)
        except:
            return False

    def clone_player_permission(self, from_id: str, to_id: str) -> str:
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
                return f"无法查询到「{from_id}」的权限记录"
            else:
                self._stored_data[to_id] = self._stored_data[from_id]
                self.write_data()
        except:
            return "克隆权限时出现错误"
        else:
            return f"成功将「{from_id}」的权限克隆到「{to_id}」"

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
        else:
            return None

    def get_group_info(self, group_name: str) -> Optional[dict]:
        """
        获取某一权限组所有权限信息\n
        Args:
            group_name: 目标玩家id
        Returns:
            如果权限组不存在返回None，存在返回字典
        """
        if group_name in self._group_permission._stored_data.keys():
            return self._group_permission._stored_data[group_name]
        else:
            return None

    def clone_group_permission(self, from_group: str, to_group: str) -> str:
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
                return f"权限组「{from_group}」不存在"
            else:
                self._group_permission._stored_data[to_group] = self._group_permission._stored_data[from_group]
                self._group_permission.write_data()
        except:
            return "克隆权限时出现错误"
        else:
            return f"成功将权限组「{from_group}」的权限克隆到「{from_group}」"

    def get_permission_node(self) -> list:
        """
        获得所有的权限节点列表\n
        Returns:
            返回所有的权限节点列表
        """
        return self._permission_node_list

    def add_group_permission(self, group_name: str, permission: str) -> str:
        """
        向权限组内添加权限\n
        Args:
            group_name: 权限组名
            permission: 权限节点名
        Returns:
            执行结果
        """
        try:
            if group_name in self._group_permission._stored_data.keys():
                self._group_permission._stored_data[group_name]["permission"].append(permission)
            else:
                self._group_permission._stored_data[group_name] = {
                    "permission": [
                        permission
                    ]
                }
            self._group_permission.write_data()
        except:
            return f"向权限组「{group_name}」添加权限“{group_name}”失败"
        else:
            return f"成功向权限组「{group_name}」添加权限”{permission}“"

    def remove_group_permission(self, group_name: str, permission: str) -> str:
        """
        从权限组内移除权限\n
        Args:
            group_name: 权限组名
            permission: 权限节点名
        Returns:
            执行结果
        """
        try:
            if group_name in self._group_permission._stored_data.keys():
                if "permission" in self._group_permission._stored_data[group_name].keys():
                    if permission in self._group_permission._stored_data[group_name]["permission"]:
                        self._group_permission._stored_data[group_name]["permission"].remove(permission)
                    else:
                        return f"权限组「{group_name}」未拥有“{permission}”权限"
                else:
                    self._group_permission._stored_data[group_name]["permission"] = []
                self._group_permission.write_data()
            else:
                return f"权限组「{group_name}」不存在"
        except:
            return f"移除权限组「{group_name}」的权限”{permission}“失败"
        else:
            return f"成功移除权限组「{group_name}」权限“{permission}”"

    def check_group_permission(self, group_name: str, permission: str) -> bool:
        """
        检查某一权限组是否拥有某一权限\n
        Args:
            group_name: 权限组名
            permission: 权限节点名
        Returns:
            拥有True 未拥有 False
        """
        try:
            data = self.get_group_permission(group_name)
            if f"-{permission}" in data:
                return False
            data = self._permission_del(data)
            if "*.*" in data:
                return True
            return self._check_permission(data, permission)
        except:
            return False

    def add_group_parent(self, group_name: str, parent_group: str) -> str:
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
                return f"权限组「{parent_group}」不存在"
            if group_name in self._group_permission._stored_data.keys():
                if "parent" in self._group_permission._stored_data[group_name].keys():
                    self._group_permission._stored_data[group_name]["parent"].append(parent_group)
                else:
                    self._group_permission._stored_data[group_name]["parent"] = [parent_group]
                self._group_permission.write_data()
            else:
                self._group_permission._stored_data[group_name] = {
                    "parent": [parent_group]
                }
                self._group_permission.write_data()
                return f"无法找到目标权限组「{group_name}」,已自动创建"
        except:
            return f"向权限组「{group_name}」添加父权限组「{parent_group}」失败"
        else:
            return f"成功为权限组「{group_name}」添加父权限组「{parent_group}」"

    def remove_group_parent(self, group_name: str, parent_group: str) -> str:
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
                return f"权限组「{parent_group}」不存在"
            if group_name in self._group_permission._stored_data.keys():
                if "parent" in self._group_permission._stored_data[group_name]:
                    self._group_permission._stored_data[group_name]["parent"].remove(parent_group)
                    self._group_permission.write_data()
                else:
                    return f"权限组「{group_name}」还没有父权限组"
            else:
                return f"权限组「{group_name}」不存在"
        except:
            return f"移除权限组「{group_name}」父权限组「{parent_group}」失败"
        else:
            return f"成功移除权限组「{group_name}」父权限组「{parent_group}」"

    def add_player_parent(self, user_id: str, parent_group: str) -> str:
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
                return f"权限组「{parent_group}」不存在"
            if user_id in self._stored_data.keys():
                if "group" in self._stored_data[user_id].keys():
                    self._stored_data[user_id]["group"].append(parent_group)
                else:
                    self._stored_data[user_id]["group"] = [parent_group]
                self.write_data()
            else:
                self._stored_data[user_id] = {
                    "group": [parent_group]
                }
                self._group_permission.write_data()
                return f"无法找到目标{user_id},已自动创建"
        except:
            return f"向用户{user_id}添加权限组{parent_group}失败"
        else:
            return f"向用户{user_id}添加权限组{parent_group}成功"

    def remove_player_parent(self, user_id: str, parent_group: str) -> str:
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
                return f"权限组「{parent_group}」不存在"
            if user_id in self._stored_data.keys():
                if "group" in self._stored_data[user_id].keys():
                    self._stored_data[user_id]["group"].remove(parent_group)
                    self.write_data()
                else:
                    return f"用户「{user_id}」未被设置过权限组"
            else:
                return f"无法找到用户：{user_id}"
        except:
            return f"移除用户「{user_id}」权限组{parent_group}失败"
        else:
            return f"移除用户「{user_id}」权限组{parent_group}成功"

    def del_group(self, group_name: str) -> str:
        """
        删除权限组\n
        Args:
            group_name: 要删除的权限组名
        Returns:
            返回执行结果
        """
        try:
            if group_name in self._group_permission._stored_data.keys():
                del self._group_permission._stored_data[group_name]
                self._group_permission.write_data()
            else:
                return f"权限组「{group_name}」不存在"
        except:
            return f"删除权限组「{group_name}」失败"
        else:
            return f"成功删除权限组：{group_name}"

    def del_player(self, user_id: str) -> str:
        """
        删除某一玩家\n
        Args:
            user_id: 玩家id
        Returns:
            返回执行结果
        """
        try:
            if user_id in self._stored_data.keys():
                del self._stored_data[user_id]
                self.write_data()
            else:
                return f"无法找到用户「{user_id}」"
        except:
            return f"删除用户「{user_id}」失败"
        else:
            return f"成功删除用户：{user_id}"

    def set_player_group(self, user_id: str, group_name: Union[str, list] = None) -> str:
        """
        为某一玩家设置权限组\n
        Args:
            user_id: 玩家id
            group_name: 要设置的权限名
        Returns:
            执行结果
        """
        try:
            if user_id in self._stored_data.keys():
                if group_name is None:
                    self._stored_data[user_id]["group"] = []
                elif isinstance(group_name, str):
                    self._stored_data[user_id]["group"] = [group_name]
                elif isinstance(group_name, list):
                    self._stored_data[user_id]["group"] = group_name
                else:
                    raise ValueError
                self.write_data()
        except:
            return f"设置「{user_id}」的权限组失败"
        else:
            return f"设置「{user_id}」的权限组为「{str(group_name)}」"

    def creat_group(self, group_name: str) -> str:
        """
        创建权限组\n
        Args:
            group_name: 权限组名
        Returns:
            执行结果
        """
        if group_name not in self._group_permission._stored_data.keys():
            self._group_permission._stored_data[group_name] = {
                "parent": ["default"],
                "permission": []
            }
            self._group_permission.write_data()
            return f"权限组「{group_name}」创建成功"
        else:
            return f"权限组「{group_name}」已存在"

    def creat_player(self, user_id: str, group: str = None) -> str:
        """
        创建玩家\n
        Args:
            user_id: 玩家ID
            group: 初始继承的权限组
        Returns:
            执行结果
        """
        if user_id not in self._stored_data.keys():
            self._stored_data[user_id] = {
                "group": ["default" if group is None else group],
                "permission": []
            }
            self.write_data()
            return f"用户「{user_id}」添加成功"
        else:
            return f"用户「{user_id}」已存在"

    @staticmethod
    def _permission_del(data: list) -> list:
        for raw in data:
            if raw.startswith("-"):
                check = raw[1:].split(".")
                match len(check):
                    case 2:
                        if raw[1:] == "*.*":
                            data.remove("*.*")
                        elif check[1] == "*":
                            for item in data:
                                if item.startswith(check[0]):
                                    data.remove(item)
                        else:
                            if raw[1:] in data:
                                data.remove(raw[1:])
                    case 3:
                        if check[2] == "*":
                            for item in data:
                                if item.startswith(f"{check[0]}.{check[1]}"):
                                    data.remove(item)
                        else:
                            if raw[1:] in data:
                                data.remove(raw[1:])
                    case 4:
                        if check[3] == "*":
                            for item in data:
                                if item.startswith(f"{check[0]}.{check[1]},{check[2]}"):
                                    data.remove(item)
                        else:
                            if raw[1:] in data:
                                data.remove(raw[1:])
                data.remove(raw)
        return data

    @staticmethod
    def _check_permission(data: list, permission: str) -> bool:
        temp = permission.split(".")
        match len(temp):
            case 1:
                raise ValueError(permission)
            case 2:
                if permission == "*.*":
                    return permission in data
                elif temp[1] == "*":
                    return permission in data
                elif temp[0] == "*":
                    raise ValueError(permission)
                else:
                    if f"{temp[0]}.*" in data:
                        return True
                    else:
                        return permission in data
            case 3:
                if permission == "*.*.*":
                    raise ValueError(permission)
                elif temp[2] == "*":
                    return permission in data
                elif temp[0] == "*" or temp[1] == "*":
                    raise ValueError(permission)
                else:
                    if f"{temp[0]}.*" in data or f"{temp[0]}.{temp[1]}.*" in data:
                        return True
                    else:
                        return permission in data
            case 4:
                if permission == "*.*.*.*":
                    raise ValueError(permission)
                elif temp[3] == "*":
                    return permission in data
                elif temp[0] == "*" or temp[1] == "*" or temp[2] == "*":
                    raise ValueError(permission)
                else:
                    if f"{temp[0]}.*" in data or f"{temp[0]}.{temp[1]}.*" in data or f"{temp[0]}.{temp[1]}.{temp[2]}.*" in data:
                        return True
                    else:
                        return permission in data
            case 5:
                if permission == "*.*.*.*.*":
                    raise ValueError(permission)
                elif temp[4] == "*":
                    return permission in data
                elif temp[0] == "*" or temp[1] == "*" or temp[2] == "*" or temp[3] == "*":
                    raise ValueError(permission)
                else:
                    if f"{temp[0]}.*" in data or f"{temp[0]}.{temp[1]}.*" in data or f"{temp[0]}.{temp[1]}.{temp[2]}.*" in data or f"{temp[0]}.{temp[1]}.{temp[2]}.{temp[3]}.*" in data:
                        return True
                    else:
                        return permission in data
