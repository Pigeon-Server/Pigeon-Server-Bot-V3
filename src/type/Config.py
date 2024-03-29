from typing import Dict


class Config:
    class DatabaseConfig:
        host: str
        password: str
        username: str
        database_name: str
        port: int
        auto_commit: bool

        def __init__(self, data: dict):
            self.__dict__ = data

    class GroupConfig:
        admin_group: str

        def __init__(self, data: dict):
            self.__dict__ = data

    class LoginConfig:
        qq: str
        host: str
        port: int
        token: str

        def __init__(self, data: dict):
            self.__dict__ = data

    database: DatabaseConfig | dict
    group_config: GroupConfig | dict
    login_config: LoginConfig | dict
    server_list: Dict[str, str]

    def __init__(self, data: dict):
        self.__dict__ = data
        self.database = self.DatabaseConfig(self.database)
        self.group_config = self.GroupConfig(self.group_config)
        self.login_config = self.LoginConfig(self.login_config)
