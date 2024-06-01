import uuid
from enum import Enum
from typing import Any


class Sender(Enum):
    USER = 1
    BOT = 2
    RECOGNIZER = 3
    REMOTE_BOT = 4

    def to_str(self):
        if self == Sender.USER:
            return "USER"
        if self == Sender.RECOGNIZER:
            return "RECOGNIZER"
        if self == Sender.BOT:
            return "BOT"
        return "UNKNOWN"


class Langs(Enum):
    UN = 0
    LT = 1
    EN = 2
    DE = 3
    PL = 4
    FR = 5
    RU = 6

    __lang_map = {UN: "unk", LT: "lt", EN: "en", DE: "de", PL: "pl", FR: "fr", RU: "ru"}
    __str_lang_map = {}

    def to_str(self):
        return Langs.__lang_map.get(self.value, "lt")

    @staticmethod
    def from_str(lan: str):
        str_lang_map = {"lt": Langs.LT, "en": Langs.EN, "de": Langs.DE, "pl": Langs.PL, "fr": Langs.FR, "ru": Langs.RU,
                        "unk": Langs.UN}
        res = str_lang_map.get(lan, Langs.UN)
        return res


class DataType(Enum):
    TEXT = 1
    AUDIO = 2
    EVENT = 3
    STATUS = 4
    TEXT_RESULT = 6

    def to_str(self):
        if self == DataType.TEXT:
            return "TEXT"
        if self == DataType.AUDIO:
            return "AUDIO"
        if self == DataType.EVENT:
            return "EVENT"
        if self == DataType.STATUS:
            return "STATUS"
        if self == DataType.TEXT_RESULT:
            return "TEXT_RESULT"
        return "UNKNOWN"


class Data:
    def __init__(self, in_type: DataType, who: Sender = Sender.BOT, data: Any = None, data2: Any = None, id: str = None,
                 session_id: str = None, lang: str = Langs.UN.to_str()):
        self.type = in_type
        self.data = data
        self.data2 = data2
        self.who = who
        self.who = who
        self.session_id = session_id
        self.lang = lang
        if id:
            self.id = id
        else:
            self.id = str(uuid.uuid1())
