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
        self.__out_func(Data(in_type=DataType.TEXT, data=txt, who=Sender.USER, session_id=session.session_id))
        self.__send_status("thinking", session_id=session.session_id)
        session.get_bot_connection().send(txt)
        self.__out_func(Data(in_type=DataType.TEXT, data=f"Gavau {txt}", who=Sender.BOT, id=id))
        # try:
        #     tree, ok = self.__cfg.parse(txt)
        #     if not ok:
        #         self.__send_status("saying")
        #         self.__out_func(Data(in_type=DataType.TEXT, data="Nesuprantu"))
        #     elif tree is None:
        #         self.__send_status("saying")
        #         self.__out_func(Data(in_type=DataType.TEXT, data="Pabaikite išraišką"))
        #     else:
        #         res = self.__parser.parse(tree)
        #         eq_res = self.__eq_parser.parse(tree)
        #         eq_svg = self.__eq_maker.prepare(eq_res)
        #         self.__send_status("saying")
        #         self.__out_func(Data(in_type=DataType.SVG, data=eq_svg, who=Sender.BOT, data2=res))
        #         self.__out_func(Data(in_type=DataType.TEXT_RESULT, data=self.number_as_text(res), who=Sender.BOT))
        # except UnknownLeave as err:
        #     logger.error(err)
        #     self.__send_status("saying")
        #     self.__out_func(Data(in_type=DataType.TEXT, data="Nežinau žodžio '%s'" % err.string, who=Sender.BOT))
        # except UnknownWord as err:
        #     logger.error(err)
        #     if err.word == "<unk>":
        #         self.__send_status("saying")
        #         self.__out_func(
        #             Data(in_type=DataType.TEXT, data="Pasakėte kažkokį nežinomą žodį", who=Sender.BOT))
        #     else:
        #         self.__send_status("saying")
        #         self.__out_func(
        #             Data(in_type=DataType.TEXT, data="Nežinau ką daryti su žodžiu '%s'" % err.word, who=Sender.BOT))
        # except ZeroDivisionError as err:
        #     logger.error(err)
        #     self.__send_status("saying")
        #     self.__out_func(Data(in_type=DataType.TEXT, data="Negaliu dalinti iš nulio", who=Sender.BOT))
        # except BaseException as err:
        #     logger.error(err)
        #     self.__send_status("saying")
        #     self.__out_func(Data(in_type=DataType.TEXT, data="Deja, kažkokia klaida!", who=Sender.BOT))
        self.__send_status("waiting", session_id=session.session_id )

    def process_event(self, inp: Data):
        logger.debug("bot got event %s" % inp.data)
        if inp.type == DataType.EVENT:
            if inp.who == Sender.USER and inp.data == "connected":
                if self.__greet_on_connect:
                    self.__out_func(Data(in_type=DataType.STATUS, data="saying"))
                    self.__out_func(Data(in_type=DataType.TEXT, data="Labas"))
                self.__out_func(Data(in_type=DataType.STATUS, data="waiting"))
            elif inp.who == Sender.RECOGNIZER:
                if inp.data == "listen":
                    self.__send_status("rec_listen", session_id=inp.session_id)
                elif inp.data == "failed":
                    self.__send_status("rec_failed", session_id=inp.session_id)
                    self.__schedule_status_restore()
                elif inp.data == "stopped":
                    self.__send_status("waiting", session_id=inp.session_id)

    def process_remote(self, inp: Data):
        logger.debug("bot got response %s" % inp.data)
        self.__out_func(Data(in_type=DataType.TEXT, data=inp.data, who=Sender.BOT, session_id=inp.session_id))

    def __send_status(self, status, session_id):
        self.__stop_timer()
        self.__out_func(Data(in_type=DataType.STATUS, data=status, session_id=session_id))

    def __bot_out_func(self, session_id, message):
        self.__stop_timer()
        self.__out_func(Data(in_type=DataType.STATUS, data=status, session_id=session_id))

    def __schedule_status_restore(self):
        def after():
            self.__send_status("waiting")

        self.__stop_timer()
        with self.__timer_lock:
            self.__status_timer = threading.Timer(5.0, after)
            self.__status_timer.start()

    def __stop_timer(self):
        with self.__timer_lock:
            if self.__status_timer:
                self.__status_timer.cancel()
                self.__status_timer = None
