import aioredis
import asyncio
from settings import config


class RedisTransport:
    def __init__(self, loop=None):
        self.url = config['redis']['url']
        self.port = config['redis']['port']
        self.loop = loop or asyncio.get_event_loop()
        self.connection = None
        self.loop.run_until_complete(self.init())
        self.save_field = config['save']['member']

    @asyncio.coroutine
    def init(self):
        self.connection = \
            yield from aioredis.create_connection((self.url, self.port), loop=self.loop, encoding='utf-8')

    @asyncio.coroutine
    def get_connection(self):
        return self.connection

    @asyncio.coroutine
    def set_connection(self, connection):
        self.connection = connection

    @asyncio.coroutine
    def save(self, data_processor):
        for data_object in data_processor:
            yield from self.connection.execute('lpush', self.save_field, data_object)