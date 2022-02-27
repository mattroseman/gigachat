const MAX_MESSAGES = 20;

export default class Chat {

  constructor() {
    this.chat = $('#messages-container');
    this.numMessages = 0;
  }

  addMessage(message) {
    this.chat.append(this.formatMessage(message));
    this.numMessages++;

    // TODO remove the oldest message if limit has been reached
    if (this.numMessages > MAX_MESSAGES) {
      this.removeOldest();
    }
  }

  removeOldest() {
    this.chat.find('.chat-message').first().remove();
  }

  formatMessage(message) {
    return `<p class='chat-message'>${message.sender}: ${message.message}</p>`;
  }
}
