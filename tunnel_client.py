import socket


class TunnelClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        """Start a tunnel client"""
        self.socket.connect(("127.0.0.1", 7000))
        while True:
            d = self.socket.recv(8, socket.MSG_WAITALL)
            requestID = int.from_bytes(d[0:4], "big")
            length = int.from_bytes(d[4:8], "big")
            print("received request", requestID, length, d)
            req = self.socket.recv(length, socket.MSG_WAITALL)

            self.doRequest(requestID, req)

    def doRequest(self, reqID: int, content):

        # reader, writer = asyncio.open_connection("127.0.0.1", 8000)
        # writer.write(content)
        # while True:
        #     reader.readuntil("\n\r")
        # while True:
        #     if req.closed:
        #         break
        #     req.recv()
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.connect(("127.0.0.1", 8000))
        _socket.send(content)
        n = 1
        while True:

            d = _socket.recv(1024)
            if len(d) > 0:
                # id | type | len | data
                self.socket.send(
                    reqID.to_bytes(4, "big")
                    + int("0x01", 16).to_bytes(1, "big")
                    + len(d).to_bytes(4, "big")
                    + d
                )
                print("response for ", reqID, " length ", len(d))

            else:
                self.socket.send(
                    reqID.to_bytes(4, "big")
                    + int("0x00", 16).to_bytes(1, "big")
                    + int("0", 10).to_bytes(4, "big")
                )
                print("finish request:", reqID)
                return
