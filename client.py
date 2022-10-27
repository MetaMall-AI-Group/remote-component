import asyncio

from stream import Stream

class Client():
    def __init__(self):
        self._connector = None
        self._event_loop = None
        self._streams = dict()
        self.reader =None
        self.writer = None
        pass

    def start(self):
        '''Start a tunnel client'''
        reader, writer = self._connector = asyncio.open_connection('127.0.0.1', 7000)
        self._event_loop = asyncio.get_event_loop()

        # accept msg from reader
        msg = {
            "streamID": None,
            "cmd": None,
            "data": None,
        }

        stream = self._streams.get(msg.streamID)
        if (stream is None):
            stream = self.newStream()

        if msg.cmd == 'pong':
            pass
        elif msg.cmd == 'proxy':
            # get local service
            # send data to the service
            # wait for response
            pass

    def newStream(self, streamID = None):
        return  Stream(self)

    async def ping(self):
        stream = self.newStream()
        stream.write(b"ping")
        # wait pong
        