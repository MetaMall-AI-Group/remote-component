from client import Client


class Stream():
    def __init__(self, client:Client):
        self.id = None
        self._input = None
        self._output = None
        self._client = client
        pass

    def reader_loop(self):
        '''
        1. read header
        -------------------------------------
        | SteamID(4B) | CMD(1B) | ...       |
        -------------------------------------
        '''
        pass