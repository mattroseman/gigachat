import os

from dotenv import load_dotenv

load_dotenv('../secrets.env')


CONFIG = {
    'LOGGING_LEVEL': os.environ.get('LOGGING_LEVEL', 'INFO'),
    'DEBUG_MESSAGE_HISTORY': int(os.environ.get('DEBUG_MESSAGE_HISTORY', '10')),
    'CONNECTION_RETRY_COOLDOWN': int(os.environ.get('CONNECTION_RETRY_COOLDOWN', '60')),

    'DGG_CHAT_URL': os.environ.get('DGG_CHAT_URL', 'wss://chat.destiny.gg/ws'),

    'TWITCH_CHAT_URL': os.environ.get('TWITCH_CHAT_URL', 'irc.chat.twitch.tv'),
    'TWITCH_CHAT_PORT': int(os.environ.get('TWITCH_CHAT_PORT', '6667')),
    'TWITCH_CHAT_NICK': os.environ.get('TWITCH_CHAT_NICK', '<replace with twitch username>'),
    'TWITCH_BUFFER_SIZE': int(os.environ.get('TWITCH_BUFFER_SIZE', '64')),
    'TWITCH_CHANNEL': os.environ.get('TWITCH_CHANNEL', 'destiny'),

    'YOUTUBE_API_LIVE_BROADCAST_URL': os.environ.get('YOUTUBE_API_LIVE_BROADCAST_URL', 'https://www.googleapis.com/youtube/v3/videos'),
    'YOUTUBE_API_LIVE_CHAT_MESSAGE_URL': os.environ.get('YOUTUBE_API_LIVE_CHAT_MESSAGE_URL', 'https://www.googleapis.com/youtube/v3/liveChat/messages'),
    'YOUTUBE_CHANNEL_ID': os.environ.get('YOUTUBE_CHANNEL_ID', 'UC1E-JS8L0j1Ei70D9VEFrPQ'),
    'YOUTUBE_LIVE_CHAT_MIN_POLLING_INTERVAL': float(os.environ.get('YOUTUBE_LIVE_CHAT_MIN_POLLING_INTERVAL', '18')),

    'TWITCH_API_KEY': os.environ.get('TWITCH_API_KEY', '<replace with twitch oauth key matching username>'),
    'YOUTUBE_API_KEY': os.environ.get('YOUTUBE_API_KEY', '<replace with youtube data API key>'),

    'REDIS_HOST': os.environ.get('REDIS_HOST', '<replace with redis host>'),
    'REDIS_PORT': os.environ.get('REDIS_PORT', '<replace with redis port>'),
    'REDIS_PASS': os.environ.get('REDIS_PASS', '<replace with redis password>'),
    'REDIS_CHANNEL': os.environ.get('REDIS_CHANNEL', '<replace with redis channel>')
}
