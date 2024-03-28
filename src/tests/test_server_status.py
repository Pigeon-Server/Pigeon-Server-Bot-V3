from os import chdir

chdir("../../")

from src.module.server_status import ServerStatus
from unittest import IsolatedAsyncioTestCase


class TestServerStatus(IsolatedAsyncioTestCase):
    async def test_get_online_player(self):
        server = ServerStatus({
            "模组服-模块化科技": "play.pigeon-server.cn:25566",
        })
        result = await server.get_online_player()
        print(result)
