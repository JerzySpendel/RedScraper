import aioredis
import asyncio
import abc
from redscraper.settings import config


class BaseExtractor(metaclass=abc.ABCMeta):
    buffer_size = 100
    index = 0

    def __init__(self):
        self.url = config['redis']['url']
        self.port = config['redis']['port']
        self.save_field = config['save']['member']
        self.loop = asyncio.get_event_loop()
        self.connection = None
        self.loop.run_until_complete(self.init_connection())

    @asyncio.coroutine
    def init_connection(self):
        self.connection =\
            yield from aioredis.create_connection((self.url, self.port), loop=self.loop, encoding='utf-8')

    def set_buffer(self, buffer_size):
        self.buffer_size = buffer_size

    @asyncio.coroutine
    def get_chunk(self):
        chunk = yield from self.connection.execute("lrange", self.save_field, self.index, self.buffer_size+self.index-1)
        self.index += self.buffer_size
        return chunk

    @asyncio.coroutine
    def run(self):
        self.setup_extractor()
        chunk = yield from self.get_chunk()
        while chunk:
            self.process(chunk)
            chunk = yield from self.get_chunk()

    @abc.abstractmethod
    def setup_extractor(self):
        return

    @abc.abstractmethod
    def process(self, object):
        return
