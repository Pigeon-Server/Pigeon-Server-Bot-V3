class SysConfig:
    class Mcsm:
        enable: bool
        use_database: bool

        def __init__(self, data: dict):
            self.__dict__ = data

    log_level: str
    dev: bool
    mcsm: Mcsm | dict

    def __init__(self, data: dict):
        self.__dict__ = data
        self.mcsm = self.Mcsm(self.mcsm)
