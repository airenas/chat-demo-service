from chat_demo.api.data import Langs
from chat_demo.logger import logger


class Translator:

    def __init__(self):
        logger.info("Init translator")

    def convert(self, txt: str, _from: Langs, _to: Langs) -> str:
        logger.info(f"Translating from {_from.to_str()} to {_to.to_str()}")
        res = txt
        return res
