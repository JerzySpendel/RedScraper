import unittest
import asyncio
from .scraper import RedisURLDispatcher
from .scraper import URLDispatcher
from .scraper import CrawlersManager
from .helpers import normalize_url
from .helpers import is_relative
from .balancer import LoadBalancer
import random
import time


class RedisURLDispatcherTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.loop = asyncio.get_event_loop()
        self.dispatcher = RedisURLDispatcher()

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
        self.assertTrue(len(self.url_dispatcher.to_visit) == 0)
        self.assertTrue(len(self.url_dispatcher.visited) == 1)


class HelpersTestCase(unittest.TestCase):
    def test_normalize_url(self):
        self.assertTrue(normalize_url('http://dobreprogramy.pl') == 'http://dobreprogramy.pl')
        self.assertTrue(normalize_url('/asdf/', 'http://dobreprogramy.pl') == 'http://dobreprogramy.pl/asdf/')

    def test_is_relative(self):
        self.assertTrue(is_relative('/asdf/'))
        self.assertTrue(not is_relative('http://dobreprogramy.pl'))


class CrawlersManagerTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.loop = asyncio.get_event_loop()
        self.cm = CrawlersManager()

    def test_semaphore(self):
        self.assertEqual(self.cm.concurrent, 0)
        self.loop.run_until_complete(self.cm.acquire())
        self.assertEqual(self.cm.concurrent, 1)

    def tearDown(self):
        self.cm._close_connections()


class LoadBalancerConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.balancer = LoadBalancer()

    def test_set_max_requests_per_minute(self):
        self.balancer.set_requests_limit(10, LoadBalancer.MINUTE)
        self.assertEqual(self.balancer.get_requests_limit(), (10, LoadBalancer.MINUTE))

    def test_set_max_requests_per_second(self):
        self.balancer.set_requests_limit(10, LoadBalancer.SECOND)
        self.assertEqual(self.balancer.get_requests_limit(), (10, LoadBalancer.SECOND))


class LoadBalancerTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.loop = asyncio.get_event_loop()
        self.balancer = LoadBalancer()
        self.balancer.set_requests_limit(60)

    def test_simple_asking(self):

        @asyncio.coroutine
        def tester(future):
            t = time.time()
            yield from self.balancer.ask()
            future.set_result(time.time() - t)

        future = asyncio.Future()
        self.loop.run_until_complete(tester(future))
        self.assertLess(future.result(), 0.1)

    def test_balancer_time_limit(self):
        request_time = 0.1

        @asyncio.coroutine
        def request_faker():
            yield from self.balancer.ask()
            yield from asyncio.sleep(request_time)

        @asyncio.coroutine
        def testing_coroutine(future):
            coro_list = []
            t = time.time()
            for i in range(61):
                task = asyncio.Task(request_faker())
                coro_list.append(task)
            yield from asyncio.wait(coro_list)
            future.set_result(time.time() - t)

        future = asyncio.Future()
        self.loop.run_until_complete(testing_coroutine(future))
        self.assertGreater(future.result(), request_time)
