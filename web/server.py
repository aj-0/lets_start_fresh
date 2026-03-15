from aiohttp import web

routes = web.RouteTableDef()

@routes.get("/")
async def root(request):
    return web.Response(text="Bot is running! 🤖", status=200)

@routes.get("/health")
async def health(request):
    return web.json_response({"status": "ok"})

async def web_server():
    app = web.Application()
    app.add_routes(routes)
    return app
