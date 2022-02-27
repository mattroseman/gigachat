import WebSocket, { WebSocketServer } from 'ws';
import { createClient } from 'redis';

import CONFIG from './config.js';

const REDIS_URL = `redis://:${CONFIG.REDIS_PASS}@${CONFIG.REDIS_HOST}:${CONFIG.REDIS_PORT}`

const wss = new WebSocketServer({ port: 8080 });

console.log('WebSocket server running.');

wss.on('connection', (ws) => {
  console.log(`received connection: ${wss.clients.size} users connected`);
});

(async () => {
  const client = createClient({
    url: REDIS_URL
  });

  await client.connect();

  await client.subscribe(CONFIG.REDIS_CHANNEL, (msg) => {
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(msg);
      }
    });
  });
})();
