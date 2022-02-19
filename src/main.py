import logging
import threading

import redis

from config import CONFIG
from connectors.twitch_connect import TwitchConnection
from connectors.dgg_connect import DGGConnection
from connectors.yt_connect import YTConnection

LOG = logging.getLogger(__name__)


def main():
    LOG.info('Setting up connection to redis')

    redis_connection = redis.Redis(
        host=CONFIG['REDIS_HOST'],
        port=CONFIG['REDIS_PORT'],
        password=CONFIG['REDIS_PASS']
    )

    LOG.info('Setting up connections to all chats')

    twitch_connection = TwitchConnection(redis_connection)
    dgg_connection = DGGConnection(redis_connection)
    yt_connection = YTConnection(redis_connection)

    LOG.info('Creating and starting threads to listen in on all chats')

    redis_thread = threading.Thread(target=read_messages, args=(redis_connection,), daemon=True)

    twitch_connection.start()
    dgg_connection.start()
    yt_connection.start()

    redis_thread.start()

    twitch_connection.join()
    dgg_connection.join()
    yt_connection.join()

    redis_thread.join()


def read_messages(redis_connection):
    p = redis_connection.pubsub()
    p.subscribe(CONFIG['REDIS_CHANNEL'])

    print('listening for messages through redis')
    for message in p.listen():
        print(message)

    p.unsubscribe()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    main()
