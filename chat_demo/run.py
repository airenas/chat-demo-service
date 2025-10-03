import argparse
import queue
import signal
import sys
import threading

from chat_demo.api.data import Data, DataType, Sender
from chat_demo.bot import DemoBot
from chat_demo.inout.audio_endpoint import AudioEndpoint
from chat_demo.inout.socket import SocketIO
from chat_demo.inout.terminal import TerminalInput, TerminalOutput
from chat_demo.inout.web import WebService
from chat_demo.langs.translator import Translator
from chat_demo.logger import logger
from chat_demo.sessions import Sessions, ChatSession
from chat_demo.tts.intelektika import IntelektikaTTS
from chat_demo.version import version


class Runner:
    def __init__(self, bot, sessions=None):
        logger.info("Init runner")
        self.__bot = bot
        self.__sessions = sessions
        self.__outputs = []
        self.__input_queue: queue.Queue[Data] = queue.Queue(maxsize=500)
        self.__output_queue: queue.Queue[Data] = queue.Queue(maxsize=500)

    def start(self):
        self.add_output_processor(self.resend_recognized)
        th_out = threading.Thread(target=self.start_output, daemon=True)
        th_out.start()
        while True:
            inp = self.__input_queue.get()
            if inp is None:
                break
            logger.info(f"input {inp.type}, {inp.id}, {inp.session_id}")
            if inp.type == DataType.TEXT and inp.who == Sender.REMOTE_BOT:
                self.__bot.process_remote(inp)
            elif inp.type == DataType.EVENT and inp.who == Sender.REMOTE_BOT:
                self.__bot.process_event(inp)
            elif inp.type == DataType.EVENT and inp.who == Sender.USER and inp.data == "disconnected":
                self.__sessions.drop(inp.session_id)
            elif inp.type == DataType.TEXT:
                self.__bot.process(inp)
            elif inp.type == DataType.AUDIO and inp.who == Sender.USER:
                logger.debug("got audio %d" % len(inp.data))
                chat = self.__sessions.get(inp.session_id)
                chat.process_msg(inp)
            elif inp.type == DataType.EVENT:
                logger.debug("got event %s" % inp.data)
                self.__bot.process_event(inp)
                if inp.who == Sender.USER and (inp.data == "AUDIO_START" or inp.data == "AUDIO_STOP"):
                    chat = self.__sessions.get(inp.session_id)
                    chat.process_msg(inp)
            else:
                logger.warning("Don't know what to do with %s - %s" % (inp.type, inp.data))
        th_out.join()
        logger.debug("Exit run loop")

    def start_output(self):
        while True:
            inp = self.__output_queue.get()
            if inp is None:
                break
            logger.info(f"output {inp.type}, {inp.id}, {inp.session_id}")
            for out_proc in self.__outputs:
                out_proc(inp)

    def add_input(self, d: Data):
        self.__input_queue.put(d)

    def add_output(self, d: Data):
        self.__output_queue.put(d)

    def add_output_processor(self, proc):
        self.__outputs.append(proc)

    def stop(self):
        self.__input_queue.put(None)
        self.__output_queue.put(None)

    def resend_recognized(self, d: Data):
        if d.type == DataType.TEXT_RESULT and d.who == Sender.RECOGNIZER:
            logger.debug("resend recognized text as user input")
            self.add_input(Data(in_type=DataType.TEXT, who=Sender.USER, data=d.data, session_id=d.session_id))
        if d.type == DataType.EVENT and d.who == Sender.RECOGNIZER:
            logger.debug("resend recognizer events")
            self.add_input(Data(in_type=DataType.EVENT, who=Sender.RECOGNIZER, data=d.data, session_id=d.session_id))


def main(param):
    parser = argparse.ArgumentParser(description="This app starts voice to voice bot",
                                     epilog="" + sys.argv[0] + "",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--tts_key", nargs='?', default='intelektika', help="TTS key")
    parser.add_argument("--use_audio_player", default=False, action=argparse.BooleanOptionalAction,
                        help="Use audio player for audio input data processing")
    parser.add_argument("--use_pc_player", default=False, action=argparse.BooleanOptionalAction,
                        help="output audio to PC instead of Audio2Face")
    parser.add_argument("--latex_url", nargs='?', default='http://localhost:5030/renderLatex',
                        help="URL of Latex equation maker")
    parser.add_argument("--kaldi_url", nargs='?', default='ws://localhost:9090/client/ws/speech',
                        help="URL of Kaldi Online wrapper")
    parser.add_argument("--number_to_text_url", nargs='?',
                        default='https://sinteze-test.intelektika.lt/number-replacer/num2text',
                        help="URL of Number Replace service")
    parser.add_argument("--tts_url", nargs='?',
                        default='https://sinteze.intelektika.lt/synthesis.service/prod/synthesize',
                        help="URL of TTS service")
    parser.add_argument("--a2f_url", nargs='?', default='localhost:50051', help="URL of Audio2Face GRPC server")
    parser.add_argument("--bot_url", nargs='?', required=True, help="Bot websocket URL")
    parser.add_argument("--a2f_name", nargs='?', default='SomeFace', help="Name of face instance for Audio2Face")
    parser.add_argument("--port", nargs='?', default=8007, help="Service port for socketio clients")
    parser.add_argument("--greet_on_connect", default=True, action=argparse.BooleanOptionalAction,
                        help="do greet client on connecting")
    parser.add_argument("--use_terminal_input", default=True, action=argparse.BooleanOptionalAction,
                        help="use terminal input")
    parser.add_argument("--translate_key", nargs='?', default='translate-key', help="VMU translate engine key")
    parser.add_argument("--translate_app", nargs='?', default='translate-app', help="VMU translate engine app name")
    args = parser.parse_args(args=param)

    def out_func(d: Data):
        runner.add_output(d)

    def in_func(d: Data):
        runner.add_input(d)

    translator = Translator(key=args.translate_key, app=args.translate_app)

    def session_factory(session_id: str):
        logger.info(f"Create session {session_id}")
        return ChatSession(session_id=session_id, out_func=out_func, in_func=in_func, bot_url=args.bot_url,
                           kaldi_url=args.kaldi_url,
                           translator=translator)

    sessions = Sessions(session_factory=session_factory)
    runner = Runner(
        bot=DemoBot(out_func=out_func, greet_on_connect=args.greet_on_connect, sessions=sessions), sessions=sessions)

    workers = []

    def start_thread(method):
        thread = threading.Thread(target=method, daemon=True)
        thread.start()
        workers.append(thread)

    if args.use_terminal_input:
        terminal = TerminalInput(msg_func=in_func)
        threading.Thread(target=terminal.start, daemon=True).start()

    terminal_out = TerminalOutput()
    runner.add_output_processor(terminal_out.process)

    ws = WebService(port=args.port)
    ws_service = SocketIO(msg_func=in_func, ws=ws)
    start_thread(ws.start)

    runner.add_output_processor(ws_service.process)

    tts = IntelektikaTTS(url=args.tts_url, key=args.tts_key,
                         voice="laimis")
    _ = AudioEndpoint(tts=tts, ws=ws, sessions=sessions)

    exit_c = 0

    def stop_runner(signum, frame):
        nonlocal exit_c
        if exit_c == 0:
            ws.stop()
            runner.stop()
        else:
            exit(1)
        exit_c = exit_c + 1

    signal.signal(signal.SIGINT, stop_runner)
    signal.signal(signal.SIGTERM, stop_runner)

    runner.start()
    for w in workers:
        w.join()
    logger.info("Exit demo-bot")


if __name__ == "__main__":
    logger.info(f"Starting demo-bot: {version}")
    main(sys.argv[1:])
