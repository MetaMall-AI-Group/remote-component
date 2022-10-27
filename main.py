import asyncio, logging


def start():
    reader, writer = asyncio.open_connection("127.0.0.1", "3000")

    with open("/cc") as file:
        logging.getLogger().info
