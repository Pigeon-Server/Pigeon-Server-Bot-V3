class Config:
    class DatabaseConfig:
        host: str
        password: str
        username: str
        database_name: str
        port: int
        auto_commit: bool
        ping_delay: int

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

    class McsmConfig:
        api_key: str
        api_url: str
        update_time: int

        def __init__(self, data: dict):
            self.__dict__ = data

    config_version: str
    database: DatabaseConfig | dict
    group_config: GroupConfig | dict
    login_config: LoginConfig | dict
    mcsm_config: McsmConfig | dict

    def __init__(self, data: dict):
        self.__dict__ = data
        self.database = self.DatabaseConfig(self.database)
        self.group_config = self.GroupConfig(self.group_config)
        self.login_config = self.LoginConfig(self.login_config)
        self.mcsm_config = self.McsmConfig(self.mcsm_config)
