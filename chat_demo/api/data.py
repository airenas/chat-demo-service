import uuid
from enum import Enum
from typing import Any


class Sender(Enum):
    USER = 1
    BOT = 2
    RECOGNIZER = 3

    def to_str(self):
        if self == Sender.USER:
            return "USER"
        if self == Sender.RECOGNIZER:
            return "RECOGNIZER"
        if self == Sender.BOT:
            return "BOT"
        return "UNKNOWN"


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
    def __init__(self, in_type: DataType, who: Sender = Sender.BOT, data: Any = None, data2: Any = None):
        self.type = in_type
        self.data = data
        self.data2 = data2
        self.who = who
        self.id = str(uuid.uuid1())
