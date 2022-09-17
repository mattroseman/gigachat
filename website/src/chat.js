import './styles/chat.scss';

const MAX_MESSAGES = 100;

const EMOTE_INFO_URL = '/assets/emotes/emote_info.json';

export default class Chat {
  constructor() {
    this.chat = $('#messages-container');

    this.numMessages = 0;

    this.emoteInfo = {};
    fetch(EMOTE_INFO_URL)
      .then(response => response.json())
      .then(data => {this.emoteInfo = data});
  }

  addMessage(messageData) {
    const shouldPin = this.scrollAtBottom();

    this.chat.append(this.formatMessage(messageData));
    this.numMessages++;

    if (shouldPin) {
      this.scrollToBottom();
    }

    if (this.numMessages > MAX_MESSAGES) {
      this.removeOldest();
    }
  }

  scrollAtBottom() {
    return this.chat.scrollTop() + this.chat.height() >= this.chat.prop('scrollHeight') - 30;
  }

  scrollToBottom() {
    this.chat.scrollTop(this.chat.prop('scrollHeight'));
  }

  removeOldest() {
    this.chat.find('.chat-message').first().remove();
  }

  formatMessage(messageData) {
    const chatType = messageData['chat-type'];
    let chatPrefix = 'D';
    const sender = messageData.sender;
    let message = messageData.message;

    if (chatType == 'DGG') {
      chatPrefix = 'D';
      message = formatDGGMessage(message)
    }
    if (chatType == 'TWITCH') {
      chatPrefix = 'T';
    }
    if (chatType == 'YOUTUBE') {
      chatPrefix = 'Y';
    }

    message = this.replaceEmotes(message, chatType);

    // TODO detect links and make them links
    // TODO add indication of what chat the message comes from
    return `<div class='chat-message'>${chatPrefix} | ${sender}: ${message}</div>`;
  }

  formatDGGMessage(message) {
    message = this.replaceDGGEmotes(message);
    return `<div class='msg-chat'>${message}</div>`;
  }


  replaceDGGEmotes(message) {
    for (const emote of this.emoteInfo.dgg) {
      const emoteRegex = new RegExp(`(?:^|\\s)(${emote.name})(?:\\s|$)`, 'g');
      /*
      for (const match of message.matchAll(emoteRegex)) {
        message = message.substr(0, match.group
      }
      */
      message = message.replace(emoteRegex, ` <div class="emote ${emote.name}"><img src="${emote.url}" height=${emote.height} width=${emote.width} /></div> `);
    }

    return message
  }
}
