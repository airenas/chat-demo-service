import threading
import time

import socketio

from chat_demo.logger import logger


class BotConnection:
    def __init__(self, url, out_func):
        self.lock = threading.Lock()
        self.url = url
        self.sio = socketio.Client()
        self.session_id = None
        self.out_func = out_func
        sio = self.sio

        @sio.event
        def connect():
            logger.info(f'connected {self.url}')

        @sio.event
        def disconnect():
            logger.info('Disconnected from server')

        @sio.on('session_confirm')
        def on_session_init(data):
            logger.info(f'Received session: {data}')
            with self.lock:
                self.session_id = data

        @sio.on('bot_uttered')
        def on_message(data):
            logger.info(f'Received bot message: {data}')
            self.out_func(data)

        self.sio.connect(self.url)
        self.sio.emit('session_request',
                      {"session_id": None})  # Replace with your event name and data

        def wait():
            logger.info('started wait thread')
            self.sio.wait()
            logger.info('exit wait thread')

        thread = threading.Thread(target=wait, daemon=True)
        thread.start()
        while True:
            with self.lock:
                if self.session_id is not None:
                    break
            time.sleep(0.1)
        logger.info(f'bot ready: session_id: {self.session_id}')

    def send(self, txt):
        logger.info(f'send to bot: {txt}, {self.session_id}')
        with self.lock:
            self.sio.emit('user_uttered', {'message': txt, 'session_id': self.session_id})
