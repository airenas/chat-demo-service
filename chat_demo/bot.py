import threading

from chat_demo.api.data import Data, DataType, Sender
from chat_demo.logger import logger
from chat_demo.sessions import Sessions


class DemoBot:
    def __init__(self, out_func, greet_on_connect: bool = True, sessions: Sessions = None):
        self.__out_func = out_func
        self.__status_timer = None
        self.__timer_lock = threading.Lock()
        self.__greet_on_connect = greet_on_connect
        self.__sessions = sessions
        logger.info("Init DemoBot")

    def process(self, data: Data):
        txt = data.data
        logger.debug(f"got: {txt}, session: {data.session_id}")
        session = self.__sessions.get(data.session_id)
        session.detect_lang(txt)
        self.__out_func(
            Data(in_type=DataType.TEXT, data=txt, who=Sender.USER, session_id=session.session_id, id=data.id,
                 lang=session.get_lang().to_str()))
        self.__send_status("thinking", session_id=session.session_id)
        session.bot_send(txt)
        self.__send_status("waiting", session_id=session.session_id)

    def process_event(self, inp: Data):
        logger.debug("bot got event %s" % inp.data)
        if inp.type == DataType.EVENT:
            if inp.who == Sender.REMOTE_BOT and inp.data == "failure":
                self.__out_func(
                    Data(in_type=DataType.TEXT, data="Atsiprašau, bet nesiseka atsakyti", session_id=inp.session_id))
            if inp.who == Sender.USER and inp.data == "connected":
                if self.__greet_on_connect:
                    self.__out_func(Data(in_type=DataType.STATUS, data="saying", session_id=inp.session_id))
                    self.__out_func(Data(in_type=DataType.TEXT, data="Labas", session_id=inp.session_id))
                self.__out_func(Data(in_type=DataType.STATUS, data="waiting", session_id=inp.session_id))
            elif inp.who == Sender.RECOGNIZER:
                if inp.data == "listen":
                    self.__send_status("rec_listen", session_id=inp.session_id)
                elif inp.data == "failed":
                    self.__send_status("rec_failed", session_id=inp.session_id)
                    self.__schedule_status_restore(inp.session_id)
                elif inp.data == "stopped":
                    self.__send_status("waiting", session_id=inp.session_id)

    def process_remote(self, inp: Data):
        logger.debug("bot got response %s" % inp.data)
        msg = Data(in_type=DataType.TEXT, data=inp.data, who=Sender.BOT, session_id=inp.session_id, lang=inp.lang)
        session = self.__sessions.get(inp.session_id)
        session.set_msg(msg)
        self.__out_func(msg)

    def __send_status(self, status, session_id):
        self.__stop_timer()
        self.__out_func(Data(in_type=DataType.STATUS, data=status, session_id=session_id))

    def __bot_out_func(self, session_id, status):
        self.__stop_timer()
        self.__out_func(Data(in_type=DataType.STATUS, data=status, session_id=session_id))

    def __schedule_status_restore(self, session_id):
        def after():
            self.__send_status("waiting", session_id=session_id)

        self.__stop_timer()
        with self.__timer_lock:
            self.__status_timer = threading.Timer(5.0, after)
            self.__status_timer.start()

    def __stop_timer(self):
        with self.__timer_lock:
            if self.__status_timer:
                self.__status_timer.cancel()
                self.__status_timer = None
