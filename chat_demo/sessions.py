import threading

from chat_demo.api.data import Data, Sender, DataType
from chat_demo.inout.bot_connection import BotConnection
from chat_demo.logger import logger


class ChatSession:
    def __init__(self, session_id: str = None, out_func=None, url: str = None):
        self.session_id = session_id
        self.bot_connection = None
        self.lock = threading.Lock()
        self.out_func = out_func
        self.url = url

    def get_bot_connection(self) -> BotConnection:
        with self.lock:
            if not self.bot_connection:
                self.bot_connection = BotConnection(out_func=self.__out_func, url=self.url)
            return self.bot_connection

    def __out_func(self, data):
        logger.info(f"out_func {data}")
        self.out_func(
            Data(session_id=self.session_id, who=Sender.REMOTE_BOT, data=data.get('text'), in_type=DataType.TEXT))


class Sessions:
    def __init__(self, out_func, url: str = None):
        logger.info(f"Init sessions, bot url {url}")
        self.__sessions = {}
        self.out_func = out_func
        self._lock = threading.Lock()
        self.url = url

    def get(self, session: str) -> ChatSession:
        with self._lock:
            if session in self.__sessions:
                return self.__sessions[session]
            logger.info(f"create session {session}")
            res = ChatSession(session, self.out_func, self.url)
            self.__sessions[session] = res
            return res

    def drop(self, session: str):
        with self._lock:
            if session in self.__sessions:
                logger.info(f"drop {session}")
                del self.__sessions[session]
