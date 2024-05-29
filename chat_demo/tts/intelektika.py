import base64

import requests

from chat_demo.logger import logger


class IntelektikaTTS:
    def __init__(self, url: str, key: str, voice: str):
        logger.info("Init TTS at: %s, voice %s" % (url, voice))
        self.__url = url
        self.__key = key
        self.__voice = voice

    def convert(self, txt: str) -> bytes:
        in_data = {'text': txt, "voice": self.__voice}
        x = requests.post(self.__url, json=in_data, headers={"Authorization": "Key " + self.__key}, timeout=30)
        if x.status_code != 200:
            raise Exception("Can't synthesize: " + x.text)
        data = x.json()
        res = data['audioAsString']
        base64_bytes = res.encode('ascii')
        return base64.decodebytes(base64_bytes)
