class CustomError(Exception):
    info: str

    def __init__(self):
        super().__init__(self)
        self.info = "未知错误"

    def __str__(self):
        return self.info


class QuotationUnmatchedError(CustomError):
    def __init__(self, info: str = "命令中的引号不匹配"):
        super().__init__()
        self.info = info


class JsonFileNotFoundError(CustomError):

    def __init__(self, info: str = "无法找到JSON文件"):
        super().__init__()
        self.info = info


class IncomingParametersError(CustomError):
    def __init__(self, info: str = "传入的参数类型不正确"):
        super().__init__()
        self.info = info


class CommandNotFoundError(CustomError):
    def __init__(self, info: str = "无法找到对应命令"):
        super().__init__()
        self.info = info


class ConnectionTypeError(CustomError):
    def __init__(self, info: str = "不支持的连接方式"):
        super().__init__()
        self.info = info


class NoParametersError(CustomError):
    def __init__(self, info: str = "未传入参数"):
        super().__init__()
        self.info = info


class ConnectServerError(CustomError):
    def __init__(self, info: str = "连接到服务器出错"):
        super().__init__()
        self.info = info


class WebsocketUrlError(CustomError):
    def __init__(self, info: str = "无效的连接地址"):
        super().__init__()
        self.info = info


class NoKeyError(CustomError):
    def __init__(self, info: str = "无法找到字典的键值"):
        super().__init__()
        self.info = info
