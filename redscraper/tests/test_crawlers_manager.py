import asyncio
from .utils import HttpServer
from .utils import TestingProcessor
from redscraper.scraper import CrawlersManager, Crawler
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

        self.loop.run_until_complete(self.cm.run())
        assert self.cm.state == 'running'
        self.loop.run_until_complete(self.cm.stop())
        assert self.cm.state == 'stopped'
        assert self.cm.concurrent == 0
        assert len(self.cm.crawlers) == 0

    def test__new_crawler(self):
        c = self.cm._new_crawler()
        assert isinstance(c, Crawler)

    def test_fire_one(self):
        c = self.cm.fire_one()
        assert len(c.future._callbacks) == 1

    def test_setting_url_constraint(self):
        c = lambda: True
        self.cm.set_url_constraint(c)
        assert self.cm.url_constraints == [c]

    def test_adding_url_constraints(self):
        c = lambda: True
        d = lambda: False
        self.cm.append_url_constraint(c)
        self.cm.append_url_constraint(d)
        assert self.cm.url_constraints == [c, d]

    def test_release(self):
        i = self.cm.concurrent
        self.cm.release()
        assert self.cm.concurrent == i - 1

    def test_acquire(self):
        i = self.cm.concurrent
        self.loop.run_until_complete(self.cm.acquire())
        assert self.cm.concurrent == i + 1

    def test_set_concurrent_crawlers(self):
        i = self.cm.CONCURRENT_MAX
        self.cm.set_concurrent_crawlers(i+1)
        assert self.cm.CONCURRENT_MAX == i + 1

    def teardown_method(self, method):
        self.loop.stop()
        self.srv.close()
        self.f.close()
        for task in asyncio.Task.all_tasks():
            task.cancel()
        self.loop.close()