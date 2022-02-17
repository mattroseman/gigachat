import asyncio
import websockets
import json
from datetime import datetime, timezone
import logging

from config import CONFIG
from base_connect import BaseConnection
from chat_message import ChatMessage, ChatType


class DGGConnection(BaseConnection):
    def is_live(self):
        # DGG is always live
        return True

    def _listen(self):
        asyncio.run(self._listen_dgg())
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self._listen_dgg())

    async def _listen_dgg(self):
        async with websockets.connect(CONFIG['DGG_CHAT_URL'], ping_interval=None) as ws:
            async for message in ws:
                # TODO catch PING methods and PONG them

                chat_message = DGGConnection._parse_chat_message(message)
                if chat_message:
                    self._publish_message(chat_message)

    @staticmethod
    def _parse_chat_message(raw_message):
        """
        parse a websocket packet into a chat_message
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

    dgg_connection = DGGConnection()

    dgg_connection.listen()
