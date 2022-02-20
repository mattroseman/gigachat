import asyncio
import websockets
import json
from datetime import datetime, timezone
import logging

# add project's root dir to sys path if file run as main
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import CONFIG
from connectors.base_connect import BaseConnection
from chat_message import ChatMessage, ChatType


class DGGConnection(BaseConnection):
    chat_type = ChatType.DGG

    def is_live(self):
        # DGG is always live
        return True

    def _listen(self):
        asyncio.run(self._listen_dgg())

    async def _listen_dgg(self):
        async with websockets.connect(CONFIG['DGG_CHAT_URL'], ping_interval=None) as ws:
            async for message in ws:
                pong_response = DGGConnection._parse_ping_message(message)
                if pong_response:
                    ws.send(f'PONG {pong_response}')
                    continue

                chat_message = DGGConnection._parse_chat_message(message)
                if chat_message:
                    self._publish_message(chat_message)

    @staticmethod
    def _parse_ping_message(raw_message):
        """
        parse a websocket packet into the ping message if it is one
        """
        msg_type, data = raw_message.split(' ', 1)

        if msg_type == 'PING':
            return data

    @staticmethod
    def _parse_chat_message(raw_message):
        """
        parse a websocket packet into a chat_message if it is one
        """
        msg_type, data = raw_message.split(' ', 1)

        if msg_type == 'MSG':
            data = json.loads(data)

            return ChatMessage(
                data['nick'],
                data['data'],
                ChatType.DGG,
                datetime.fromtimestamp(data['timestamp'] / 1000, timezone.utc)
            )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logging.getLogger('DGGConnection').setLevel(logging.DEBUG)

    dgg_connection = DGGConnection()
    dgg_connection.listen()
