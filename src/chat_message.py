from enum import Enum
from datetime import datetime
import json


class ChatType(Enum):
    DGG = 1
    TWITCH = 2
    YOUTUBE = 3


class ChatMessage:
    def __init__(self, sender, message, chat_type, timestamp=None):
        self.sender = sender
        self.message = message
        self.chat_type = chat_type
        if timestamp is not None:
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.utcnow()

    def __str__(self):
        return self.json()

    def json(self):
        return json.dumps({
            'sender': self.sender,
            'message': self.message,
            'chat-type': self.chat_type.name,
            'timestamp': self.timestamp.isoformat()
        })

    def get_chat_type_prefix(self):
        if self.chat_type == ChatType.DGG:
            return 'D'

        if self.chat_type == ChatType.YOUTUBE:
            return 'Y'

        if self.chat_type == ChatType.TWITCH:
            return 'T'
