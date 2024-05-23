import queue

from chat_demo.logger import logger


class AudioSaver:
    def __init__(self, rate: int = 16000):
        logger.info("Init AudioSaver. rate %d" % rate)
        self.__audio_queue: queue.Queue[bytes] = queue.Queue(maxsize=500)
        self.rate = rate
        self.f = None

    def add(self, data: bytes):
        logger.debug("add play data of len %d" % len(data))
        self.__audio_queue.put(data)

    def event(self, data: str):
        if data == "AUDIO_START":
            self.f = open("foo.pcm", "wb")
        else:
            if self.f:
                self.f.close()
                self.f = None

    def start(self):
        while True:
            self.__play(self.__audio_queue.get())

    def __play(self, data: bytes):
        try:
            if self.f:
                self.f.write(data)
        except BaseException as err:
            logger.error(err)

    def stop(self):
        logger.debug("stopping player...")
        if self.f:
            self.f.close()
            self.f = None
