import unittest
import aioredis
import asyncio
from scraper import RedisURLDispatcher
from scraper import URLDispatcher


class RedisURLDispatcherTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.loop = asyncio.get_event_loop()
        self.dispatcher = RedisURLDispatcher(self.loop, 'localhost')

    def test_add_to_visit(self):
        @asyncio.coroutine
        def wrapper():
            yield from self.dispatcher.init()
            yield from self.dispatcher.add_to_visited('http://')
            yield from self.dispatcher.add_to_visit('http://')
            self.assertTrue((yield from self.dispatcher.connection.execute('sismember', 'to_visit', 'http://')) == 0)
            self.dispatcher.connection.close()
        self.loop.run_until_complete(wrapper())


class URLDispatcherTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.url_dispatcher = URLDispatcher()
        self.loop = asyncio.get_event_loop()

    def test_adding_to_visit(self):
        url = 'http://dobreprogramy.pl'
        self.loop.run_until_complete(self.url_dispatcher.add_to_visit(url))
        self.loop.run_until_complete(self.url_dispatcher.get_url())
        self.loop.run_until_complete(self.url_dispatcher.add_to_visit(url))
        self.assertTrue( len(self.url_dispatcher.to_visit) == 0)
        self.assertTrue( len(self.url_dispatcher.visited) == 1)
