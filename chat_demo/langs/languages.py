from langdetect import detect_langs

from chat_demo.api.data import Langs
from chat_demo.logger import logger


class LangsDetector:

    def detect(self, txt: str) -> Langs:
        if not txt:
            return Langs.UN
        txt_s = txt.strip()
        if not txt_s:
            return Langs.UN
        try:
            detected_langs = detect_langs(txt_s)
        except Exception as e:
            logger.error(f"Failed to detect language '{txt_s}': {e}")
            return Langs.UN
        for lang in detected_langs:
            if Langs.from_str(lang.lang) != Langs.UN:
                return Langs.from_str(lang.lang)
        return Langs.UN
