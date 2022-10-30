from tunnel_client import TunnelClient

# from aiohttp import web


# async def handle(request: web.Request):
#     print("url:", request.url)
#     web.Response("hello, world. I am under path:" + request.path)


# webapp = web.Application()
# webapp.add_routes([web.get("/{tail:.*}", handle)])

# web.run_app(webapp)

client = TunnelClient("127.0.0.1", 7000)


client.start()
