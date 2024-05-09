from chat_demo.api.data import Data, DataType, Sender
from chat_demo.logger import logger


class TerminalInput:
    def __init__(self, msg_func):
        logger.info("Init terminal input")
        self.msg_func = msg_func

    def start(self):
        while True:
            # print("You: ", end="")
            txt = input()
            self.msg_func(Data(in_type=DataType.TEXT, who=Sender.USER, data=txt))


class TerminalOutput:
    def __init__(self):
        logger.info("Init terminal output")

    def process(self, d: Data):
        if d.type == DataType.TEXT or d.type == DataType.TEXT_RESULT:
            print("%s: %s" % (d.who, d.data))
        elif d.type == DataType.STATUS:
            print("%s: %s" % (d.who, d.data))
        elif d.type == DataType.EVENT and d.who == Sender.RECOGNIZER:
            print("event %s: %s" % (d.who, d.data))
        else:
            logger.warning("Don't know what to do with %s - %s" % (d.type, d.data))
