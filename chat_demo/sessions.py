import threading
from typing import Dict

from chat_demo.api.data import Data, Sender, DataType
from chat_demo.asr.kaldi import Kaldi
from chat_demo.inout.bot_connection import BotConnection
from chat_demo.logger import logger


class Message:
    def __init__(self, text: str):
        self.lock = threading.Lock()
        self.text = text
        self.audio = None


class ChatSession:
    def __init__(self, session_id: str = None, out_func=None, in_func=None, bot_url: str = None,
                 kaldi_url: str = None):
        self.session_id = session_id
        self.__bot_connection: BotConnection = None
        self.__kaldi: Kaldi = None
        self.__kaldi_url = kaldi_url
        self.__kaldi_thread = None
        self.__lock = threading.Lock()
        self.__out_remote_func = out_func
        self.__in_func = in_func
        self.__bot_url = bot_url
        self.__messages = {}

    def get_bot_connection(self) -> BotConnection:
        with self.__lock:
            if not self.__bot_connection:
                self.__bot_connection = BotConnection(out_func=self.__out_func, url=self.__bot_url)
            if not self.__bot_connection.connected():
                self.__in_func(
                    Data(session_id=self.session_id, who=Sender.REMOTE_BOT, data="failure",
                         in_type=DataType.EVENT))
            return self.__bot_connection

    def __get_recognizer(self) -> Kaldi:
        with self.__lock:
            if not self.__kaldi:
                self.__kaldi = Kaldi(url=self.__kaldi_url, msg_func=self.__recognizer_func)
                self.__kaldi_thread = threading.Thread(target=self.__kaldi.start, daemon=True)
                self.__kaldi_thread.start()

            return self.__kaldi

    def set_msg(self, msg: Data):
        with self.__lock:
            logger.info(f"add msg to cache {msg.id}")
            self.__messages[msg.id] = Message(text=msg.data)

    def get_msg(self, msg_id) -> Message:
        with self.__lock:
            return self.__messages.get(msg_id)

    def process_msg(self, inp):
        if inp.type == DataType.AUDIO and inp.who == Sender.USER:
            logger.debug("got audio %d" % len(inp.data))
            self.__get_recognizer().add(inp.data)
        elif inp.type == DataType.EVENT and inp.who == Sender.USER and (
                inp.data == "AUDIO_START" or inp.data == "AUDIO_STOP"):
            self.__get_recognizer().event(inp.data)

    def drop(self):
        with self.__lock:
            if self.__bot_connection:
                self.__bot_connection.close()
            self.__bot_connection = None
            if self.__kaldi:
                self.__kaldi.stop()
            self.__kaldi = None
            if self.__kaldi_thread:
                self.__kaldi_thread.join()

    def __out_func(self, data):
        logger.info(f"out_func {data}")
        self.__in_func(
            Data(session_id=self.session_id, who=Sender.REMOTE_BOT, data=data.get('text'), in_type=DataType.TEXT))

    def __recognizer_func(self, data):
        logger.info(f"recognizer_func {data}")
        data.session_id = self.session_id
        self.__out_remote_func(data)


class Sessions:
    def __init__(self, session_factory):
        self.__sessions: Dict[str: ChatSession] = {}
        self.__session_factory = session_factory
        self._lock = threading.Lock()

    def get(self, session: str) -> ChatSession:
        with self._lock:
            if session in self.__sessions:
                return self.__sessions[session]
            logger.info(f"create session {session}")
            res = self.__session_factory(session)
            self.__sessions[session] = res
            return res

    def drop(self, session: str):
        with self._lock:
            session: ChatSession = self.__sessions.get(session)
            if session in self.__sessions:
                session.drop()
                del self.__sessions[session]
