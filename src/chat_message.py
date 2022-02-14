from enum import Enum
from datetime import datetime


class ChatType(Enum):
    DGG = 1
    TWITCH = 2
    YOUTUBE = 3


class ChatMessage:
    def __init__(self, sender, message, chat_type, timestamp=None):
        self.sender = sender
        self.message = message
        self.chat_type = chat_type
        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.timestamp(datetime.utcnow())
