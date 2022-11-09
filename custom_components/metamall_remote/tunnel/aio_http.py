from aiohttp.web import AppRunner, SockSite
import socket
import logging

logger = logging.getLogger(__name__)

class AioHttp():
    def __init__(self, runner: AppRunner):
        self._socket = socket.socket()
        self._socket.setblocking(False)
        self._socket.bind(("127.0.0.0", 0))
        self._site = SockSite(runner, self._socket)
        self.host = None
        self.port = None

    async def start(self):
        await self._site.start()
        self.host, self.port = self._socket.getsockname()[:2]
        logger.info("AioHttp server started on %s:%s", self.host, self.port)