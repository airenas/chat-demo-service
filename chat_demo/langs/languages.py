from langdetect import detect_langs

from chat_demo.api.data import Langs


class LangsDetector:

    def detect(self, txt: str) -> Langs:
        if not txt:
            return Langs.UN
        if txt.strip() == "":
            return Langs.UN
        detected_langs = detect_langs(txt.strip())
        for lang in detected_langs:
            if Langs.from_str(lang.lang) != Langs.UN:
                return Langs.from_str(lang.lang)
        return Langs.UN
