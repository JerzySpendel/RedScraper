import asyncio
import aiohttp
import pytest
import pytest_asyncio.plugin
from .utils import TestingProcessor
from redscraper.scraper import CrawlersManager
from .utils import HttpServer


class TestHttpServerTestCase:

    def setup_method(self, method):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        f = self.loop.create_server(lambda: HttpServer(), '0.0.0.0', '8080')
        self.loop.run_until_complete(f)

    def test_http_server(self):

        @asyncio.coroutine
        def getter():
            res = yield from aiohttp.get('http://0.0.0.0:8080')
            res.close()
            res = yield from aiohttp.get('http://0.0.0.0:8080/close')
            res.close()

        asyncio.ensure_future(getter())
        self.loop.run_forever()

    def teardown_method(self, method):
        self.loop.stop()
