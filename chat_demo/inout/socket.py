import asyncio

import socketio
from aiohttp import web

from chat_demo.api.data import Data, DataType, Sender
from chat_demo.logger import logger


class SocketIO:
    def __init__(self, msg_func, port):
        self.__port = port
        logger.info("Init socket IO")
        self.msg_func = msg_func
        self.sio = socketio.AsyncServer(cors_allowed_origins='*')
        self.sio.on("message", self.message)
        self.sio.on("connect", self.connect)
        self.sio.on("disconnect", self.disconnect)
        self.loop = None

    def start(self):
        path = 'ai-demo-service/ws/socket.io'
        logger.info(f"Starting at {self.__port}, path={path}")
        app = web.Application()
        self.sio.attach(app, socketio_path=path)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        server = self.loop.create_server(app.make_handler(), port=self.__port)
        self.loop.run_until_complete(server)
        self.loop.run_forever()
        logger.debug("Exit socket listener")

    async def message(self, sid, data):
        if data['type'] == "AUDIO":
            self.msg_func(Data(in_type=DataType.AUDIO, who=Sender.USER, data=data['data'], session_id=sid))
        elif data['type'] == "EVENT":
            self.msg_func(Data(in_type=DataType.EVENT, who=Sender.USER, data=data['data'], session_id=sid))
        else:
            logger.info("message: %s, %s " % (sid, data))
            self.msg_func(Data(in_type=DataType.TEXT, who=Sender.USER, data=data['data'], session_id=sid))

    def process(self, d: Data):
        asyncio.run_coroutine_threadsafe(self.send(d), self.loop)

    async def send(self, d: Data):
        if d.who == Sender.REMOTE_BOT:
            pass
        elif d.type == DataType.TEXT or d.type == DataType.TEXT_RESULT or d.type == DataType.STATUS:
            logger.info("sending msg %s" % d.type)
            await self.sio.emit(event='message', to=d.session_id,
                                data={"type": d.type.to_str(), "data": str(d.data), "data2": str(d.data2),
                                      "who": d.who.to_str(), "id": d.id, "session_id": d.session_id})
        elif d.who == Sender.RECOGNIZER:
            pass
        else:
            logger.warning("Don't know what to do with %s - %s" % (d.type, d.data))

    async def connect(self, sid, environ):
        logger.info("connect: %s " % sid)
        self.msg_func(Data(in_type=DataType.EVENT, who=Sender.USER, data="connected", session_id=str(sid)))

    async def disconnect(self, sid):
        logger.info("disconnect: %s " % sid)
        self.msg_func(Data(in_type=DataType.EVENT, who=Sender.USER, data="disconnected", session_id=str(sid)))

    def stop(self):
        logger.debug("stopping socket listener loop")
        self.loop.call_soon_threadsafe(self.loop.stop)
