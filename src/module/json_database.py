from enum import Enum
from os import getcwd
from os.path import join
from typing import Optional, Union

from src.base.logger import logger
from src.exception.exception import NoKeyError
from src.utils.file_utils import check_directory, check_file
from src.utils.json_utils import read_json, write_json


class DataType(Enum):
    """枚举类，用来转换类型和数字"""
    STR = 1
    INT = 2
    FLOAT = 3
    LIST = 4
    DICT = 5


class JsonDataBase:
    _stored_data: Union[dict, list]

    def __init__(self, file_name: str, data_type: DataType) -> None:
        """
        类构造函数\n
        Args:
            file_name: 要使用的文件名，应该位于data文件夹下，如果不存在会自动创建
            data_type: 文件内存储的格式 1:str 2:int 3: float 4: list: 5: dict 除了dict外，其他类型均为list存储
        """
        self._data_path: str = join(getcwd(), "data")
        self._data_type: DataType = DataType(data_type)
        check_directory(self._data_path, create_if_not_exist=True)
        self._data_file_path: str = join(self._data_path, file_name)
        if check_file(self._data_file_path):
            self._stored_data = read_json(self._data_file_path, skip_file_check=True)
            if self._stored_data is None:
                self._stored_data = {}
            return
        if DataType(data_type) == DataType.DICT:
            write_json(self._data_file_path, {})
            self._stored_data = {}
            return
        write_json(self._data_file_path, [])
        self._stored_data = []

    def edit_data(self, data: Union[str, int, float, list, dict], target: Optional[str] = None,
                  del_data: bool = False) -> bool:
        """
        编辑数据, 可添加可删除\n
        可编辑受限制：\n
        int float str list 四种存储类型无target属性，只有一层深度，均有delData属性\n
        dict 存储类型有target属性，当第一层为list类型时有delData属性\n
        注意，dict套dict时仅支持传入dict类型的参数进行修改，其他参数将会抛出错误\n
        Args:
            data: 要修改或删除的数据
            target: 要修改的键名，仅当存储类型为dict的时候需要传入
            del_data: 是否为删除模式，当存储类型为dict以外的四种类型或存储类型为dict且target下为list类型时生效
        Return:
            bool: True 成功  False 失败
        """

        def edit() -> None:
            if target is None:
                raise NoKeyError("未指定修改的键值")
            if target is not None:
                if target not in self._stored_data.keys():
                    if not del_data:
                        self._stored_data[target] = data
                        return
                temp_data = self._stored_data[target]
                if isinstance(temp_data, list):
                    self._stored_data[target].remove(data) if del_data else self._stored_data[target].append(data)
                    return
                if isinstance(temp_data, str) or isinstance(temp_data, int) or isinstance(temp_data, float):
                    self._stored_data[target] = data
                    return
                if isinstance(temp_data, dict):
                    if isinstance(data, dict):
                        self._stored_data[target] = data
                        return
                    raise RuntimeError("不支持此类修改")

        backup_data = self._stored_data
        if self.is_dict:
            edit()
            try:
                self.write_data()
                return True
            except:
                self._stored_data = backup_data
                self.write_data()
                return False
        try:
            self._stored_data.remove(data) if del_data else self._stored_data.append(data)
            self.write_data()
            return True
        except:
            self._stored_data = backup_data
            self.write_data()
            return False

    def reload_data(self) -> None:
        """
        重新从文件加载数据\n
        """
        logger.trace(f"Reload file {self._data_file_path}")
        self._stored_data = read_json(self._data_file_path)

    def write_data(self) -> None:
        """
        将本地缓存的内容写入文件\n
        """
        logger.trace(f"Save file {self._data_file_path}")
        write_json(self._data_file_path, self._stored_data)

    def query_data(self, data: Union[str, int, float, list, dict], target: Optional[str] = None) -> bool:
        """
        查询数据\n
        查询限制：\n
        int str float list 四种存储类型无target属性,查询无限制,均可查询\n
        dict 存储类型有target属性\n
        注意，当第一层为dict类型时无法查询，且会抛出错误\n
        Args:
            data: 查询的数据
            target: 要查询的键名，仅当存储类型为dict的时候需要传入
        Return:
            bool: True 成功  False 失败
        """
        if self.is_dict:
            if target is None:
                raise NoKeyError("未指定查询的键值")
            if target not in self._stored_data.keys():
                return False
            temp_data = self._stored_data[target]
            if isinstance(temp_data, list):
                return True if data in temp_data else False
            if isinstance(temp_data, str) or isinstance(temp_data, int):
                return True if data == temp_data else False
            if isinstance(temp_data, float):
                return True if abs(temp_data - data) <= 1e-8 else False
            if isinstance(temp_data, dict):
                raise RuntimeError("不支持此类型的查询")
        return True if data in self._stored_data else False

    @property
    def data_type(self) -> DataType:
        return self._data_type

    @property
    def is_dict(self) -> bool:
        return self._data_type == DataType.DICT

    @property
    def stored_data(self) -> dict:
        return self._stored_data
