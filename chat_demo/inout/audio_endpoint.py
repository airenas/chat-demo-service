from aiohttp import web

from chat_demo.logger import logger
from chat_demo.sessions import Sessions


class AudioEndpoint:
    def __init__(self, tts, ws, sessions: Sessions):
        self.__tts = tts
        self.__sessions = sessions
        path = '/ai-demo-service/tts/{session}/{id}'
        logger.info(f"Init audio endpoint: {path}")
        ws.app.router.add_get(path, self.get_audio)

    async def get_audio(self, request):
        sid = request.match_info.get('session', None)
        if not sid:
            logger.error(f"no session")
            return web.Response(status=400, text="No session id")
        msg_id = request.match_info.get('id', None)
        if not msg_id:
            logger.error(f"no id")
            return web.Response(status=400, text="No id")
        logger.info(f"handler get audio {sid}/{msg_id}")

        session = self.__sessions.get(sid)
        if not session:
            logger.error(f"no session {sid}")
            return web.Response(status=404, text="No session")
        msg = session.get_msg(msg_id)
        if not msg:
            logger.error(f"no id {id}")
            return web.Response(status=404, text="No message by id")

        with msg.lock:
            if not msg.audio:
                msg.audio = self.__tts.convert(msg.text)

        headers = {'Content-Type': 'audio/mpeg'}
        return web.Response(body=msg.audio, headers=headers)
