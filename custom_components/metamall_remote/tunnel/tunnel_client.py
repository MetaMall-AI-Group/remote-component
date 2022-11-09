import socket
import logging
import asyncio

logger = logging.getLogger(__name__)

class TunnelClient:
    def __init__(self, proxy_host, proxy_port, local_host, local_port):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._local_port = local_port
        self._local_host = local_host

        self._requests = dict()

        self.loop = asyncio.get_event_loop()

    async def start(self):
        """Start a tunnel client"""
        self.proxy.connect((self.proxy_host, self.proxy_port))
        while True:
            d = self.proxy.recv(8, socket.MSG_WAITALL)
            requestID = int.from_bytes(d[0:4], "big")
            length = int.from_bytes(d[4:8], "big")
            logger.debug("received request", requestID, length, d)
            content = self.socket.recv(length, socket.MSG_WAITALL)

            sock = self.get_request(requestID)
            sock.send(content)

            
    async def get_request(self, reqID):
        if self._requests.has_key(reqID):
            return self._requests[reqID]
        else:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.connect((self._local_host, self._local_port))

            self._requests[reqID] = _socket
            # self.wait_localserver_response(_socket, reqID)
            self.loop.run_until_complete()
            return _socket

    async def accept_localserver_response(self, socket, requestID):
        while True:
            d = socket.recv(1024)
            if len(d) > 0:
                # id | type | len | data
                self.socket.send(
                    requestID.to_bytes(4, "big")
                    + int("0x01", 16).to_bytes(1, "big")
                    + len(d).to_bytes(4, "big")
                    + d
                )
                logger.debug("response for ", requestID, " length ", len(d))

            else:
                self.socket.send(
                    requestID.to_bytes(4, "big")
                    + int("0x00", 16).to_bytes(1, "big")
                    + int("0", 10).to_bytes(4, "big")
                )
                logger.debug("finish request:", requestID)
                return
        print('======break the loop of receive response fromlocal =====')

