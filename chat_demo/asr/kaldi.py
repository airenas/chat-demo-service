import json
import queue
import threading
from typing import List
from urllib.parse import urlencode

import websocket as websocket

from chat_demo.api.data import Data, DataType, Sender
from chat_demo.logger import logger


class SpeechSegment:
    def __init__(self, segment: int = 0, text: str = "", final: bool = True):
        self.segment = segment
        self.text = text
        self.final = final


class WsClient:
    def __init__(self, url, text_method, event_method):
        websocket.setdefaulttimeout(15)
        self.ws_conn = websocket.WebSocketApp(url,
                                              on_open=self.on_open,
                                              on_message=self.on_message,
                                              on_close=self.on_close,
                                              on_error=self.on_error)
        self.ws = None
        self.__audio_queue: queue.Queue[bytes] = queue.Queue(maxsize=500)
        self.__text_method = text_method
        self.__event_method = event_method
        self.hyps: List[SpeechSegment] = []
        self.failed = False

        def start_conn():
            self.ws_conn.run_forever()
            logger.debug("ws conn init exit")

        threading.Thread(target=start_conn).start()

    def on_message(self, ws, message):
        msg = str(message)
        response = json.loads(msg)
        if len(msg) > 200:
            msg = msg[:200]
        logger.debug("got from kaldi message: %s " % msg)
        if response['status'] == 0:
            old_updates = response.get("old-updates")
            if old_updates and len(old_updates) > 0:
                self.__update_hyps(old_updates)
            if 'result' in response and response['result'].get('hypotheses'):
                trans = response['result']['hypotheses'][0]['transcript']
                if response['result']['final']:
                    self.hyps.append(SpeechSegment(segment=response.get("segment", 0), text=trans, final=True))
                else:
                    txt = self.get_text(trans)
                    if txt:
                        self.__text_method(False, txt)
            if 'adaptation_state' in response:
                logger.debug("got adaptation, do nothing")
        else:
            logger.error("Received error from server (status %d)" % response['status'])
            if 'message' in response:
                logger.error("Error message:", response['message'])

    def on_error(self, ws, err):
        logger.error(f"Kaldi ws conn error: {err}")
        self.__event_method("failed")
        self.failed = True

    def on_open(self, ws):
        logger.info("connected to kaldi ws")
        self.ws = ws

        def send_data_to_ws():
            logger.debug("run send thread")
            while True:
                data = self.__audio_queue.get()
                if data is None:
                    break
                self.ws.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
            logger.debug("exit send thread")

        self.failed = False
        self.__event_method("listen")
        threading.Thread(target=send_data_to_ws).start()

    def on_close(self, ws, close_status_code, close_msg):
        logger.debug("closed ws kaldi connection")
        self.__audio_queue.put(None)
        if not self.failed:
            self.__event_method("stopped")
        txt = self.get_text("")
        if txt:
            self.__text_method(True, txt)

    def close(self):
        logger.info("closing")
        self.ws_conn.close()
        self.__audio_queue.put(None)

    def send(self, data):
        logger.debug("put data to kaldi queue")
        self.__audio_queue.put(data)

    def get_text(self, trans):
        str = []
        for hyp in self.hyps:
            if hyp.final:
                str.append(hyp.text)
        res = " ".join(str).strip() + " " + trans
        return res.strip()

    def __update_hyps(self, old_updates):
        for update in old_updates:
            found = False
            for hyp in self.hyps:
                if hyp.segment == update.get("segment"):
                    logger.debug(f"update hyp {hyp.segment}")
                    hyp.final = update.get("final", True)
                    hyp.text = update.get("transcript", "")
                    found = True
                    break
            if not found:
                logger.warning(f"update hyp failed, no segment {update.get('segment')}")


def get_url(url):
    content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1" % 16000
    return url + '?%s' % urlencode([("content-type", content_type)])


class Kaldi:
    def __init__(self, url, msg_func):
        logger.info("Init Kaldi wrapper")
        self.__audio_queue: queue.Queue[bytes] = queue.Queue(maxsize=500)
        self.__txt_queue: queue.Queue[tuple(bool, str)] = queue.Queue(maxsize=500)

        self.recognized_value = ""
        self.working = False
        self.last_gen_type = 0
        self.msg_func = msg_func
        self.next = None
        self.client = None
        self.cl_lock = threading.Lock()
        f_url = get_url(url)
        logger.info("WS URL: %s" % f_url)
        self.url = f_url

    def add(self, data: bytes):
        logger.debug("add play data of len %d" % len(data))
        self.__audio_queue.put(data)

    def event(self, data: str):
        if data == "AUDIO_START":
            self.last_gen_type = 0
            self.recognized_value = ""
            self.working = True
            with self.cl_lock:
                if self.client is not None:
                    self.client.close()
                try:
                    self.client = WsClient(url=self.url, text_method=self.__process_kaldi_msg,
                                           event_method=self.__process_events)
                except BaseException as err:
                    logger.error(err)
        elif data == "AUDIO_STOP":
            self.working = False
            with self.cl_lock:
                if self.client is not None:
                    self.client.send("EOS")

    def start(self):
        th = threading.Thread(target=self.__recognized, daemon=True)
        th.start()
        while True:
            data = self.__audio_queue.get()
            if data is None:
                break
            self.__process(data)
        th.join()
        logger.debug("Exit kaldi recognizer")

    def __recognized(self):
        while True:
            data = self.__txt_queue.get()
            if data is None:
                break
            self.__process_recognized(data)

    def __process(self, data: bytes):
        self.client.send(data)

    def __process_kaldi_msg(self, final, txt):
        self.__txt_queue.put((final, txt))

    def __process_events(self, event):
        self.msg_func(Data(in_type=DataType.EVENT, who=Sender.RECOGNIZER, data=event))

    def __process_recognized(self, data):
        try:
            final, txt = data
            logger.debug("Got from kaldi(%s) %s" % (final, txt))
            if final:
                self.msg_func(Data(in_type=DataType.TEXT, who=Sender.RECOGNIZER, data=""))
                self.msg_func(Data(in_type=DataType.TEXT_RESULT, who=Sender.RECOGNIZER, data=txt))
            else:
                self.msg_func(Data(in_type=DataType.TEXT, who=Sender.RECOGNIZER, data=txt + "..."))
        except BaseException as err:
            logger.error(err)

    def stop(self):
        logger.debug("stopping kaldi ...")
        self.__audio_queue.put(None)
        self.__txt_queue.put(None)
        with self.cl_lock:
            if self.client is not None:
                self.client.send("EOS")
