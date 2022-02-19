import socket
import re
import logging

# add project's root dir to sys path if file run as main
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import CONFIG
from connectors.base_connect import BaseConnection, AuthenticationError
from chat_message import ChatMessage, ChatType

CHAT_AUTH_FAILED_REGEX = re.compile(r'^:tmi.twitch.tv NOTICE * :Login authentication failed$')
CHAT_MSG_REGEX = re.compile(r'^:(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.+)$')
CHAT_PING_REGEX = re.compile(r'PING (:tmi.twitch.tv)')


class TwitchConnection(BaseConnection):
    chat_type = ChatType.TWITCH

    def __init__(self, redis_connection=None):
        super().__init__(redis_connection)

        self.IRC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IRC.connect((CONFIG['TWITCH_CHAT_URL'], CONFIG['TWITCH_CHAT_PORT']))

        self._send_data('PASS %s' % CONFIG['TWITCH_API_KEY'])
        self._send_data('NICK %s' % CONFIG['TWITCH_CHAT_NICK'])
        self._send_data('CAP REQ :twitch.tv/membership')

    def is_live(self):
        # TODO write this
        return True

    def _listen(self):
        #  clear the IRC buffer
        readbuffer = self.IRC.recv(CONFIG['TWITCH_BUFFER_SIZE']).decode('UTF-8', errors='ignore')

        #  join the IRC channel
        self._send_data('JOIN #{0}'.format(CONFIG['TWITCH_CHANNEL']))

        while True:
            readbuffer += self.IRC.recv(CONFIG['TWITCH_BUFFER_SIZE']).decode('UTF-8', errors='ignore')
            lines = readbuffer.split('\r\n')

            # copy the last line (that doesn't have the ending carriage return) into the next readbuffer
            readbuffer = lines.pop()

            for line in lines:
                if CHAT_AUTH_FAILED_REGEX.match(line):
                    raise AuthenticationError('Twitch Authentication failed, check credentials.')

                chat_message = TwitchConnection._parse_chat_message(line)
                if chat_message:
                    self._publish_message(chat_message)

                if CHAT_PING_REGEX.match(line):
                    response = 'PONG ' + CHAT_PING_REGEX.match(line).group(1)
                    self._send_data(response)

    def _send_data(self, command):
        """
        sends the given command to the IRC server
        """
        self.IRC.send(bytes(command + '\r\n', 'UTF-8'))

    @staticmethod
    def _parse_chat_message(line):
        """
        takes an irc message and if it's a chat message line, returns the sender and message
        @return: chat_message isntance with sender, message, timestamp, and any other data
        """
        match = CHAT_MSG_REGEX.match(line)

        if match:
            return ChatMessage(match.group(1), match.group(2), ChatType.TWITCH)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    twitch_connection = TwitchConnection()

    twitch_connection.listen()
