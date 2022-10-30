import queue


class Stream:
    def __init__(self, id, socket):
        self.id = id
        self.socket = socket
        self._input = None
        self._output = queue.Queue()
        self.ack()

    def ack(self):
        header = b""
        header += bytes(int("0x00", 16).to_bytes(1, "big"))
        header += bytes(int("0x00", 16).to_bytes(1, "big"))
        header += bytes(int("0x02", 16).to_bytes(2, "big"))
        header += bytes(self.id.to_bytes(4, "big"))
        header += bytes(int("0x00", 16).to_bytes(4, "big"))
        self.socket.send(header)

    def accept(self):
        while True:
            data = self._output.get(True)
            if data != None:
                pass
