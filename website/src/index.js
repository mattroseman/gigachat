import Chat from './chat';

const websocket = new WebSocket('wss://chat.gigachat.dev');

websocket.onmessage = handleMessage;

const chat = new Chat();

function handleMessage(rawMessage) {
  const message = JSON.parse(rawMessage.data);

  chat.addMessage(message);
}
