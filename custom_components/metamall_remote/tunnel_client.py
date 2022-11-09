import socket
import logging
import asyncio
import threading
import queue
import time

logger = logging.getLogger(__name__)

class TunnelClient:
    def __init__(self, proxy_host, proxy_port, local_host, local_port):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._local_port = local_port
        self._local_host = local_host

        self._requests = dict()

        self._response_queue = queue.Queue()

        self.in_loop = asyncio.get_event_loop()
        self.out_loop = asyncio.new_event_loop()
        
       

    async def start(self):
        """Start a tunnel client"""
        logger.info("Connect to remote server for tunnel")
        self.proxy.connect((self.proxy_host, self.proxy_port))
        threading.Thread(target= self.read_from_proxy).start()
        threading.Thread(target= self._response_to_proxy).start()
        threading.Thread(target= self._ping).start()
            
    def get_request(self, reqID):
        if reqID in self._requests:
            _socket =  self._requests[reqID]
            if (getattr(_socket, '_closed') == True):
                return None
        else:
            try:
                _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                _socket.settimeout(10)
                _socket.connect((self._local_host, self._local_port))
                
                logger.debug("connected to local server")
            except Exception as e:
                logger.debug("connect to local server failed")
                return None
            

            self._requests[reqID] = _socket
            threading.Thread(target=self.accept_localserver_response, args=(_socket, reqID)).start()
            
            return _socket

    def _ping(self):
        while True:
            time.sleep(5)
            self.write_to_proxy(0, b"ping", True)

    def accept_localserver_response(self, socket, requestID):
        while True:
            d = socket.recv(1024)
            if len(d) > 0:
                
                self.write_to_proxy(requestID, d, close=False)
                logger.debug("response for %s length: %d" % (requestID, len(d)))

            else:
                self.write_to_proxy(requestID, b"", close=True)
                logger.debug("finish request: %s" % requestID)
                
                return

            # await asyncio.sleep(0.001)
        

    def write_to_proxy(self, requestID:int, data:bytes, close:bool=False):
        self._response_queue.put(
            requestID.to_bytes(4, "big")  
            + (int("0x00", 16).to_bytes(1, "big") if close else int("0x01", 16).to_bytes(1, "big")) 
            + len(data).to_bytes(4, "big") 
            + data
        )
        

    def read_from_proxy(self):
        while True:
            d = self.proxy.recv(8, socket.MSG_WAITALL)
            requestID = int.from_bytes(d[0:4], "big")
            length = int.from_bytes(d[4:8], "big")
            content = self.proxy.recv(length, socket.MSG_WAITALL)
            
            # get request socket to local server
            sock = self.get_request(requestID)
            if sock == None:
                self.write_to_proxy(requestID, b"", close=True)
            else:
                sock.send(content)
            # await asyncio.sleep(0.001)

    def _response_to_proxy(self):
        while True:
            try:
                data = self._response_queue.get(block=True, timeout=1)
                if data is None:
                    continue
                self.proxy.send(data)
                
            except queue.Empty:
                pass
            except Exception as e:
                
                logger.error(e)

            
            
            
