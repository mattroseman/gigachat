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
        self.LOG = logging.getLogger(__name__)
        self.LOG.setLevel(CONFIG['LOGGING_LEVEL'])

        self.redis_connection = redis_connection
        self.debug_lines = CircularBuffer(CONFIG['DEBUG_MESSAGE_HISTORY'])

        Thread.__init__(self, daemon=True)

    @property
    @abstractmethod
    def chat_type(self):
        """
        chat_type should be a ChatType enum
        """
        pass

    @abstractmethod
    def is_live(self):
        pass

    def run(self):
        self.listen()

    def listen(self):
        while True:
            if self.is_live():
                self.LOG.info(f'Listening to {self.chat_type.name} chat')
                try:
                    self._listen()
                except AuthenticationError:
                    raise AuthenticationError
                except Exception:
                    self.LOG.error(self.debug_lines)
                    self.LOG.error(traceback.format_exc())

            cooldown_time = CONFIG['CONNECTION_RETRY_COOLDOWN']
            self.LOG.debug(f'{self.chat_type.name} chat connection failed, retrying in {cooldown_time} seconds')
            time.sleep(cooldown_time)

    def _publish_message(self, chat_message):
        """
        publish message to redis pub/sub
        """
        prefix = chat_message.get_chat_type_prefix()
        self.LOG.debug(f'{prefix} | {chat_message.sender}: {chat_message.message}')
        self.debug_lines.enqueue(chat_message)

        if self.redis_connection:
            self.redis_connection.publish(CONFIG['REDIS_CHANNEL'], chat_message.json())
