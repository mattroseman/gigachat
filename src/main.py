import logging

# import redis

from twitch_connect import TwitchConnection
from dgg_connect import DGGConnection
from yt_connect import YTConnection


def main():
    logging.info('Setting up connections to all chats')

    twitch_connection = TwitchConnection()
    dgg_connection = DGGConnection()
    yt_connection = YTConnection()

    logging.info('Creating and starting threads to listen in on all chats')

    # redis_thread = threading.Thread(target=read_messages, args=(redis_connection,), daemon=True)

    twitch_connection.start()
    dgg_connection.start()
    yt_connection.start()

    # redis_thread.start()

    twitch_connection.join()
    dgg_connection.join()
    yt_connection.join()

    # redis_thread.join()


def read_messages(redis_connection):
    p = redis_connection.pubsub()
    p.subscribe('chat-messages')

    print('listening for messages through redis')
    for message in p.listen():
        print(message)

    p.unsubscribe()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    main()
