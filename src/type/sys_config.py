class SysConfig:
    log_level: str
    dev: bool

    def __init__(self, data: dict):
        self.__dict__ = data
