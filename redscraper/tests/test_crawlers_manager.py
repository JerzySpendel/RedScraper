import asyncio
from .utils import HttpServer
from .utils import TestingProcessor
from redscraper.scraper import CrawlersManager
from redscraper.settings import config
import pytest

config['scraper']['start_url'] = 'http://0.0.0.0:8080'


class TestManagerCrawlers:

    def setup_method(self, method):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.f = self.loop.create_server(lambda: HttpServer(), '0.0.0.0', '8080')
        self.srv = self.loop.run_until_complete(self.f)
        self.cm = CrawlersManager(TestingProcessor())

    def test_run_and_stop(self):

        @asyncio.coroutine
        def cm():
            yield from self.cm.run()
            yield from self.cm.stop()

        self.loop.run_until_complete(cm())
        assert self.cm.state == 'stopped'

    def teardown_method(self, method):
        self.loop.stop()
        self.srv.close()
        self.f.close()
        for task in asyncio.Task.all_tasks():
            task.cancel()
        self.loop.close()