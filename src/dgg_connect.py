import asyncio
import websockets
import json

from chat_message import ChatMessage, ChatType

DGG_CHAT_URL = 'wss://chat.destiny.gg/ws'


class DGGConnection:
    def __init__(self):
        pass

    async def listen(self, message_buffer):
        async with websockets.connect(DGG_CHAT_URL, ping_interval=None) as ws:
            async for message in ws:
                chat_message = self._parse_chat_message(message)
                if chat_message:
                    message_buffer.enqueue(chat_message)

    def _parse_chat_message(self, raw_message):
        msg_type, data = raw_message.split(' ', 1)

        if msg_type == 'MSG':
            data = json.loads(data)

            return ChatMessage(data['nick'], data['data'], ChatType.DGG, data['timestamp'])


if __name__ == '__main__':
    dgg_connection = DGGConnection()
    asyncio.run(dgg_connection.listen())
