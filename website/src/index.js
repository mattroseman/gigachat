import Chat from './chat';

import './styles/global.scss';

const WEBSOCKET_URL = 'wss://chat.gigachat.dev';

let websocket;

function websocketConnect() {
  websocket = new WebSocket(WEBSOCKET_URL);

  websocket.onmessage = handleMessage;

  // attempt to reconnect on disconnect
  websocket.onclose = () => {
    websocketConnect();
  };
}

websocketConnect();

const chat = new Chat();
const messageQueue = [];

function handleMessage(rawMessage) {
  const message = JSON.parse(rawMessage.data);

  messageQueue.push(message);

  chat.addMessage(message);
}

setTimeout(() => {
  const message = messageQueue.shift();
  if (message) {
    chat.addMessage(message);
  }
}, 0);
