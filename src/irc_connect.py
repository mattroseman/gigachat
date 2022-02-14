import os
import socket
import re

from chat_message import ChatMessage, ChatType

# Constants
SERVER = 'irc.chat.twitch.tv'
PORT = 6667
NICKNAME = '<ENTER TWITCH USERNAME HERE>'
PASSWORD = '<ENTER OAUTH TOKEN FOR TWITCH DEVELOPER APPLICATION HERE>'


BUFFER_SIZE = 64

CHAT_MSG_REGEX = re.compile(r'^:(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.+)$')
CHAT_PING_REGEX = re.compile(r'PING (:tmi.twitch.tv)')


class IRCBadMessage(Exception):
    pass


class IRCConnection:
    """
    Used to connect to the twitch irc server and get messages, etc from
    different channels
    """

    current_dir = os.path.dirname(__file__)
    config_rel_path = '../config/irc.cfg'
    config_abs_path = os.path.join(current_dir, config_rel_path)

    section_name = 'Connection Authentication'

    def __init__(self):
        self.IRC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IRC.connect((SERVER, PORT))

        self._send_data('PASS %s' % PASSWORD)
        self._send_data('NICK %s' % NICKNAME)
        self._send_data('CAP REQ :twitch.tv/membership')

    def listen(self, channel, message_buffer):
        """
        listens for messages from the given channel, and yields messages as they come through
        """
        #  clear the IRC buffer
        readbuffer = self.IRC.recv(BUFFER_SIZE).decode('UTF-8', errors='ignore')

        #  join the IRC channel
        self._send_data('JOIN #{0}'.format(channel))

        while True:
            readbuffer += self.IRC.recv(BUFFER_SIZE).decode('UTF-8', errors='ignore')
            lines = readbuffer.split('\r\n')
            # copy the last line (that doesn't have the ending carriage return) into the next readbuffer
            readbuffer = lines.pop()

            for line in lines:
                if 'PRIVMSG' in line:
                    chat_message = self._parse_chat_message_line(line)
                    if chat_message:
                        message_buffer.enqueue(chat_message)

                if 'PING' in line:
                    response = 'PONG ' + CHAT_PING_REGEX.match(line).group(1)
                    self._send_data(response)

    def _send_data(self, command):
        """
        sends the given command to the IRC server
        """
        self.IRC.send(bytes(command + '\r\n', 'UTF-8'))

    def _parse_chat_message_line(self, line):
        """
        takes an irc message and if it's a chat message line, returns the sender and message
        @return: string representing the user, and string representing the message
        """
        match = CHAT_MSG_REGEX.match(line)

        if match:
            return ChatMessage(match.group(1), match.group(2), ChatType.TWITCH)
