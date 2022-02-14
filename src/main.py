import asyncio
import threading

from irc_connect import IRCConnection
from dgg_connect import DGGConnection
from chat_message import ChatType

from utils.circular_buffer import CircularBuffer

MSG_BUFFER_SIZE = 10


async def main():
    irc_connection = IRCConnection()
    dgg_connection = DGGConnection()

    message_buffer = CircularBuffer(MSG_BUFFER_SIZE)

    twitch_thread = threading.Thread(target=irc_connection.listen, args=('destiny', message_buffer), daemon=True)
    dgg_thread = threading.Thread(target=asyncio.run, args=(dgg_connection.listen(message_buffer),), daemon=True)

    twitch_thread.start()
    dgg_thread.start()

    for chat_message in message_buffer.listen():
        chat_type_prefix = 'D' if chat_message.chat_type == ChatType.DGG else 'T'
        print(f'{chat_type_prefix} | {chat_message.sender}: {chat_message.message}')

    twitch_thread.join()
    dgg_thread.join()


if __name__ == '__main__':
    asyncio.run(main())
