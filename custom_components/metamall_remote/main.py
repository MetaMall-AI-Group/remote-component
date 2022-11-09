from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from tunnel_client import TunnelClient

import logging

logging.basicConfig(level=logging.DEBUG)

async def async_setup(hass: HomeAssistant, config: ConfigEntry):
    # start aiohttp server
    # aiohttp = AioHttp()
    tunnel = TunnelClient("127.0.0.1", 7000, '127.0.0.1', 8000)
    await tunnel.start()

tunnel = TunnelClient("127.0.0.1", 7000, '127.0.0.1', 8000)

import asyncio
asyncio.run(tunnel.start())

# import socket

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# sock.connect(("127.0.0.1", 7000))

# while True:
            
#     d = sock.recv(8, socket.MSG_WAITALL)
#     requestID = int.from_bytes(d[0:4], "big")
#     length = int.from_bytes(d[4:8], "big")
#     logging.debug("received request", requestID, length, d)
    