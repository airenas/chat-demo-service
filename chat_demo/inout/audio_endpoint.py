from aiohttp import web

from chat_demo.logger import logger


class AudioEndpoint:
    def __init__(self, tts, ws):
        self.tts = tts
        path = '/ai-demo-service/tts'
        logger.info(f"Init audio endpoint: {path}")
        ws.app.router.add_get(path, self.get_audio)

    async def get_audio(self, request):
        audio_content = self.tts.convert(
            "Laba diena. Šiais laikais, kai viskas vyksta greitai, svarbu ne tik greitai reaguoti, bet ir greitai suprasti.")
        headers = {'Content-Type': 'audio/mpeg'}
        return web.Response(body=audio_content, headers=headers)
