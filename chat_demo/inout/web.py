import asyncio

from aiohttp import web

from chat_demo.logger import logger


class WebService:
    def __init__(self, port):
        self.__port = port
        logger.info(f"Init web, port: {port}")
        self.loop = None
        self.app = web.Application()

    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        server = self.loop.create_server(self.app.make_handler(), port=self.__port)
        self.loop.run_until_complete(server)
        self.loop.run_forever()
        logger.debug("Exit socket listener")

    def stop(self):
        logger.debug("stopping socket listener loop")
        self.loop.call_soon_threadsafe(self.loop.stop)
