import dotenv from 'dotenv';

dotenv.config({ path: '../secrets.env'});

export default {
  'REDIS_HOST': process.env.REDIS_HOST || '<replace with redis host>',
  'REDIS_PORT': process.env.REDIS_PORT || '<replace with redis port>',
  'REDIS_PASS': process.env.REDIS_PASS || '<replace with redis password>',
  'REDIS_CHANNEL': process.env.REDIS_CHANNEL || '<replace with redis channel>'
};
