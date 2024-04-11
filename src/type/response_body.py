from typing import List, TypeVar


class ResponseHeader:
    status: int
    data: dict
    time: int

    def __init__(self, data: dict):
        self.__dict__ = data


class InstanceConfig:
    nickname: str

    def __init__(self, data: dict):
        self.__dict__ = data


class Overview:
    class Remote:
        class Instance:
            running: int
            total: int

            def __init__(self, data: dict):
                self.__dict__ = data

        version: str
        process: dict
        instance: dict
        system: Instance | dict
        cpuMemChart: list
        uuid: str
        ip: str
        port: int
        available: bool
        remarks: str

        def __init__(self, data: dict):
            self.__dict__ = data
            self.system = self.Instance(self.system)

    class OverviewBody:
        class Remotes:
            available: int
            total: int

            def __init__(self, data: dict):
                self.__dict__ = data

        version: str
        specifiedDaemonVersion: str
        process: dict
        record: dict
        system: dict
        chart: dict
        remoteCount: Remotes | dict
        remote: List['Overview.Remote'] | dict

        def __init__(self, data: dict):
            self.__dict__ = data
            self.remoteCount = self.Remotes(self.remoteCount)
            remotes: List['Overview.Remote'] = []
            for remote in self.remote:
                remotes.append(Overview.Remote(remote))
            self.remote = remotes

    status: int
    data: OverviewBody
    time: int

    def __init__(self, data: ResponseHeader):
        self.status = data.status
        self.time = data.time
        self.data = self.OverviewBody(data.data)


class RemoteServicesList:
    class RemoteServices:
        uuid: str
        ip: str
        port: int
        available: bool
        remarks: str

        def __init__(self, data: dict):
            self.__dict__ = data

    status: int
    data: List[RemoteServices]
    time: int

    def __init__(self, data: ResponseHeader):
        self.status = data.status
        self.time = data.time
        self.data = []
        for remote in data.data:
            self.data.append(self.RemoteServices(remote))


class RemoteServices:
    class RemoteService:
        class Service:
            instanceUuid: str
            status: int
            config: InstanceConfig | dict

            def __init__(self, data: dict):
                self.__dict__ = data
                self.config = InstanceConfig(self.config)

        uuid: str
        ip: str
        port: int
        available: bool
        remarks: str
        instances: List[Service | dict]

        def __init__(self, data: dict):
            self.__dict__ = data
            temp: List[RemoteServices.RemoteService.Service] = []
            for ins in self.instances:
                temp.append(self.Service(ins))
            self.instances = temp

    status: int
    data: List[RemoteService]
    time: int

    def __init__(self, data: ResponseHeader):
        self.status = data.status
        self.time = data.time
        self.data = []
        for remote in data.data:
            self.data.append(self.RemoteService(remote))


class InstanceInfo:
    class Instance:
        instanceUuid: str
        status: int
        config: InstanceConfig

        def __init__(self, data: dict):
            self.__dict__ = data

    status: int
    data: Instance | dict
    time: int

    def __init__(self, data: ResponseHeader):
        self.status = data.status
        self.time = data.time
        self.data = self.Instance(data.data)
