import re
import time
from datetime import datetime, timedelta
import logging

import requests

# add project's root dir to sys path if file run as main
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import CONFIG
from connectors.base_connect import BaseConnection
from chat_message import ChatMessage, ChatType

DGG_LIVE_BROADCAST_ID_REGEX = re.compile(r'<link rel="canonical" href="https://www.youtube.com/watch\?v=([^&]+?)">')


class YTConnection(BaseConnection):
    chat_type = ChatType.YOUTUBE

    def __init__(self, redis_connection=None):
        super().__init__(redis_connection)

        self.live_chat_id = None
        self._initialize()

    def is_live(self):
        self._initialize()
        return self.live_chat_id is not None

    def _initialize(self):
        """
        queries for the live channel id needed to get chat messages
        """
        broadcast_id = YTConnection._get_live_broadcast_id(CONFIG['YOUTUBE_CHANNEL_ID'])

        if broadcast_id is None:
            return

        self.live_chat_id = YTConnection._get_live_chat_id(broadcast_id)
        return self.live_chat_id

    def _listen(self):
        params = {
            'liveChatId': self.live_chat_id,
            'part': 'snippet,authorDetails',
            'key': CONFIG['YOUTUBE_API_KEY'],
        }
        next_page_token = None

        # do a dry request to catch up to the latest messages, so the messages yielded aren't always behind
        response = requests.get(CONFIG['YOUTUBE_API_LIVE_CHAT_MESSAGE_URL'], params=params)
        if not response.ok:
            raise RuntimeError(f'Request failed to get live chat messages. Received a {response.status_code}\n{response.text}')
        next_page_token = response.json()['nextPageToken']
        time.sleep(response.json()['pollingIntervalMillis'] / 1000)

        while True:
            if next_page_token:
                params['pageToken'] = next_page_token

            last_request_time = datetime.utcnow()
            response = requests.get(CONFIG['YOUTUBE_API_LIVE_CHAT_MESSAGE_URL'], params=params)

            if not response.ok:
                raise RuntimeError(f'Request failed to get live chat messages. Received a {response.status_code}\n{response.text}')

            body = response.json()

            next_page_token = body['nextPageToken']

            for chat_message in YTConnection._parse_live_chat_messages(body['items']):
                self._publish_message(chat_message)

            # sleep what is required to catch up to the `pollingIntervalMillis` (recommended by the google-api response) before the next request
            time_since_last_request = datetime.utcnow() - last_request_time

            required_polling_interval = timedelta(microseconds=body['pollingIntervalMillis'] * 1000)
            polling_interval = max(required_polling_interval, timedelta(seconds=CONFIG['YOUTUBE_LIVE_CHAT_MIN_POLLING_INTERVAL']))

            time_to_sleep = max((polling_interval - time_since_last_request).total_seconds(), 0)
            time.sleep(time_to_sleep)

    @staticmethod
    def _get_live_broadcast_id(channel_id):
        """
        crawls youtube to guess if the channel with the given id is live, and if it is, gets its live broadcast id
        """
        live_channel_url = f'https://www.youtube.com/channel/{channel_id}/live'

        response = requests.get(live_channel_url)

        if not response.ok:
            raise RuntimeError(f'Request failed to get live broadcast id. Received a {response.status_code}\n{response.text}')

        # look for a canonical link in header, which will be present if broadcast is live
        match = DGG_LIVE_BROADCAST_ID_REGEX.search(response.text)

        if not match:
            return

        return match.group(1)

    @staticmethod
    def _get_live_chat_id(broadcast_id):
        response = requests.get(CONFIG['YOUTUBE_API_LIVE_BROADCAST_URL'], params={
            'id': broadcast_id,
            'part': 'liveStreamingDetails',
            'key': CONFIG['YOUTUBE_API_KEY']
        })

        if response.status_code != 200:
            raise RuntimeError(f'request failed to get live chat id\n{response.text}')

        return response.json()['items'][0]['liveStreamingDetails']['activeLiveChatId']

    @staticmethod
    def _parse_live_chat_messages(raw_messages):
        """
        parse the bulk google-api messages into chat_messages and yield with wait times between the messages matching the original times between users sending them
        """
        if len(raw_messages) == 0:
            return

        chat_messages = []
        for message in raw_messages:
            if message['kind'] != 'youtube#liveChatMessage':
                continue
            if message['snippet']['type'] != 'textMessageEvent':
                continue

            timestamp = datetime.strptime(message['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%S.%f%z')
            chat_messages.append(ChatMessage(
                message['authorDetails']['displayName'],
                message['snippet']['displayMessage'],
                ChatType.YOUTUBE,
                timestamp=timestamp
            ))

        if len(chat_messages) == 0:
            return

        previous_timestamp = chat_messages[0].timestamp
        for chat_message in chat_messages:
            # in order to simulate the flow of the original chat, wait between yielding the same amount of time between the original messages being sent
            wait_for_message = (chat_message.timestamp - previous_timestamp).total_seconds()
            time.sleep(max(wait_for_message, 0))

            yield chat_message

            previous_timestamp = chat_message.timestamp


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    yt_connection = YTConnection()

    yt_connection.listen()
