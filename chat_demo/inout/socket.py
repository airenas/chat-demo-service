import asyncio

import socketio

from chat_demo.api.data import Data, DataType, Sender
from chat_demo.logger import logger


class SocketIO:
    def __init__(self, msg_func, ws):
        path = 'ai-demo-service/ws/socket.io'
        logger.info(f"Init socket IO: {path}")
        self.msg_func = msg_func
        self.sio = socketio.AsyncServer(cors_allowed_origins='*')
        self.sio.on("message", self.message)
        self.sio.on("connect", self.connect)
        self.sio.on("disconnect", self.disconnect)
        self.sio.attach(ws.app, socketio_path=path)
        self.ws = ws

    async def message(self, sid, data):
        if data['type'] == "AUDIO":
            self.msg_func(
                Data(in_type=DataType.AUDIO, who=Sender.USER, data=data['data'], session_id=sid, id=data.get('id')))
        elif data['type'] == "EVENT":
            self.msg_func(
                Data(in_type=DataType.EVENT, who=Sender.USER, data=data['data'], session_id=sid, id=data.get('id')))
        else:
            logger.info("message: %s, %s " % (sid, data))
            self.msg_func(
                Data(in_type=DataType.TEXT, who=Sender.USER, data=data['data'], session_id=sid, id=data.get('id')))

    def process(self, d: Data):
        asyncio.run_coroutine_threadsafe(self.send(d), self.ws.loop)

    async def send(self, d: Data):
        if d.who == Sender.REMOTE_BOT:
            pass
        elif d.type == DataType.TEXT or d.type == DataType.TEXT_RESULT or d.type == DataType.STATUS:
            logger.info("sending msg %s" % d.type)
            await self.sio.emit(event='message', to=d.session_id,
                                data={"type": d.type.to_str(), "data": str(d.data), "data2": str(d.data2),
                                      "who": d.who.to_str(), "id": d.id, "session_id": d.session_id, "lang": d.lang})
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
