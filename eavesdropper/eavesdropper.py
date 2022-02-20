import logging

import redis

from config import CONFIG
from connectors.twitch_connect import TwitchConnection
from connectors.dgg_connect import DGGConnection
from connectors.yt_connect import YTConnection

logging.basicConfig(level=logging.INFO, format='%(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(CONFIG['LOGGING_LEVEL'])


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

    twitch_connection.start()
    dgg_connection.start()
    yt_connection.start()

    twitch_connection.join()
    dgg_connection.join()
    yt_connection.join()


if __name__ == '__main__':
    main()
