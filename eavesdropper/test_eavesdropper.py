import redis
import json

from config import CONFIG

pubsub = redis.Redis(
    host=CONFIG['REDIS_HOST'],
    port=CONFIG['REDIS_PORT'],
    password=CONFIG['REDIS_PASS']
).pubsub()

pubsub.subscribe(CONFIG['REDIS_CHANNEL'])

for msg in pubsub.listen():
    if msg['data'] == 1:
        continue

    data = json.loads(msg['data'])
    sender = data['sender']
    message = data['message']
    if data['chat-type'] == 'DGG':
        prefix = 'D'
    if data['chat-type'] == 'YOUTUBE':
        prefix = 'Y'
    if data['chat-type'] == 'TWITCH':
        prefix = 'T'

    print(f'{prefix} | {sender}: {message}')
