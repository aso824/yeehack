import json
from asyncio import Event

from aiohttp import web

import errors
from lock import Lock

routes = web.RouteTableDef()


class Server:
    def __init__(self, port: int):
        self.port: int = port

    async def start(self):
        app = web.Application()
        app.add_routes(routes)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner)
        await site.start()

        await Event().wait()

    @routes.post('/info')
    async def info(request):
        try:
            data = await request.json()
            sn = data['sn']
        except (json.decoder.JSONDecodeError, AttributeError, KeyError):
            return web.json_response({'error': 'Invalid input'}, status=400)

        try:
            lock = await Lock.create(sn, bytearray())
            level = await lock.get_battery()
        except errors.DeviceNotFoundError:
            return web.json_response({'error': 'Device not found'}, status=400)

        return web.json_response({'battery': level})

    @routes.post('/do')
    async def do(request):
        try:
            data = await request.json()
            action = data['action']
            sn = data['sn']
            sign_key = data['sign_key']
        except (json.decoder.JSONDecodeError, AttributeError, KeyError):
            return web.json_response({'error': 'Invalid input'}, status=400)

        try:
            lock = await Lock.create(sn, bytearray.fromhex(sign_key))
        except ValueError:
            return web.json_response({'error': 'Sign key is not a hexadecimal string'}, status=400)
        except errors.DeviceNotFoundError:
            return web.json_response({'error': 'Device not found'}, status=400)

        if action == 'lock':
            await lock.lock()
        elif action == 'unlock':
            await lock.unlock()
        elif action == 'temp_unlock':
            await lock.temp_unlock()
        else:
            return web.json_response({'error': 'Unknown action to do'}, status=400)

        return web.json_response({'success': True})

