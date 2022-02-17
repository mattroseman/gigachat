import time
from abc import ABC, abstractmethod
import logging
import traceback
from threading import Thread

from config import CONFIG
from utils.circular_buffer import CircularBuffer


class AuthenticationError(Exception):
    pass


class BaseConnection(ABC, Thread):
    def __init__(self, redis_connection=None):
        self.redis_connection = redis_connection
        self.debug_lines = CircularBuffer(CONFIG['DEBUG_MESSAGE_HISTORY'])

        Thread.__init__(self, daemon=True)

    @abstractmethod
    def is_live(self):
        pass

    def run(self):
        self.listen()

    def listen(self):
        while True:
            if self.is_live():
                try:
                    self._listen()
                except AuthenticationError:
                    raise AuthenticationError
                except Exception:
                    logging.error(self.debug_lines)
                    logging.error(traceback.format_exc())

            time.sleep(CONFIG['CONNECTION_RETRY_COOLDOWN'])

    def _publish_message(self, chat_message):
        """
        publish message to redis pub/sub
        """
        prefix = chat_message.get_chat_type_prefix()
        logging.info(f'{prefix} | {chat_message.sender}: {chat_message.message}')
        self.debug_lines.enqueue(chat_message)

        if self.redis_connection:
            self.redis_connection.publish(CONFIG['REDIS_CHANNEL'], chat_message.json())
