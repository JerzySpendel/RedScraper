import asyncio
import aiohttp
import aioredis
from bs4 import BeautifulSoup
import re
from .settings import config
from .processor import CustomProcessor
from .helpers import normalize_url
from .cli import args as cli_args
import signal
import sys


regex = re.compile(
    r'(^(\/\w+)+)|' #relative url support
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def download(url):
    try:
        return (yield from aiohttp.get(url))
    except aiohttp.errors.ContentEncodingError:
        print('During visiting {} ContentEncodingError ocurred'.format(url))


class URLDispatcher:
    '''
    Simple URL dispatcher storing URLs in-memory
    '''

    def __init__(self):
        self.to_visit = set()
        self.visited = set()

    @asyncio.coroutine
    def init(self):
        pass

    @asyncio.coroutine
    def add_to_visit(self, url):
        if url not in self.visited:
            self.to_visit.update([url])

    @asyncio.coroutine
    def get_url(self):
        while len(self.to_visit) == 0:
            yield from asyncio.sleep(0.1)
        url = self.to_visit.pop()
        yield from self.add_to_visited(url)
        return url

    @asyncio.coroutine
    def add_to_visited(self, url):
        self.visited.update([url])


class RedisURLDispatcher:
    '''
    Class responsible for feeding crawlers with URLs (stored in redis)
    to visit
    '''

    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.url = config['redis']['url']
        self.port = int(config['redis']['port'])
        self.connection = None
        self.to_visit, self.visited = config['redis']['to_visit'], \
            config['redis']['visited']

    @asyncio.coroutine
    def init(self):
        self.connection = yield from aioredis.create_connection((self.url, self.port), loop=self.loop, encoding='utf-8')
        yield from self.connection.execute('flushdb')

    @asyncio.coroutine
    def add_to_visit(self, url):
        in_visited = yield from self.connection.execute('sismember', self.visited, url)
        if not in_visited == 1:
            yield from self.connection.execute('sadd', self.to_visit, url)

    @asyncio.coroutine
    def get_url(self):
        url = yield from self.connection.execute('spop', self.to_visit)
        while url is None:
            yield from asyncio.sleep(0.1)
            url = yield from self.connection.execute('spop', self.to_visit)
        yield from self.add_to_visited(url)
        return url

    @asyncio.coroutine
    def add_to_visited(self, url):
        yield from self.connection.execute('sadd', self.visited, url)


class Crawler:
    def __init__(self, urldis, data_processor):
        self.urldis = urldis
        self.url_constraints = []
        self.data_processor = data_processor

    def set_url_constraint(self, constraint):
        self.url_constraints = [constraint]

    def append_url_constraint(self, constraint):
        self.url_constraints.append(constraint)

    @asyncio.coroutine
    def crawl(self, future):
        url = yield from self.urldis.get_url()
        site_downloader = download(url)
        try:
            d = yield from site_downloader
        except Exception as e:
            print('Exception ocurred')
            return
        html = yield from d.text()
        print(url)
        for g_url in self.get_urls(html):
            try:
                n_url = normalize_url(g_url, visited=url)
            except Exception as e:
                print(e)
                continue
            bad_url = False
            for constraint in self.url_constraints:
                if not constraint(n_url):
                    bad_url = True
            if bad_url:
                continue
            yield from self.urldis.add_to_visit(n_url)
        yield from self.data_processor.feed_with_data(html)
        future.set_result(None)

    def get_urls(self, html):
        soup = BeautifulSoup(html, 'lxml')
        ass = soup.find_all('a')
        for i in range(len(ass)):
            try:
                href = ass[i].get('href')
                if regex.match(href):
                    yield href
            except:
                pass


class CrawlersManager:
    CONCURRENT_MAX = 10
    url_constraints = []

    def __init__(self, data_processor=None):
        self.start_url = config['scraper']['start_url']
        self._parse_cli()
        self.loop = asyncio.get_event_loop()
        self.url_dispatcher = RedisURLDispatcher()
        self.semaphore = asyncio.Semaphore(value=self.CONCURRENT_MAX)
        self.cc_future = asyncio.Future()
        self.concurrent = 0
        self._do_some_init()
        self.data_processor = data_processor or CustomProcessor()
        signal.signal(signal.SIGINT, self._quit_handler)

    def _quit_handler(self, signal, frame):
        print('\nAll crawlers are being stopped')
        self.set_concurrent_crawlers(0)
        self.cc_future.set_result(None)
        output = sys.stdout
        sys.stdout = None #silence crawlers

        @asyncio.coroutine
        def closing_task():
            while self.concurrent != 0:
                yield from asyncio.sleep(0.5)
            sys.stdout = output
            self._close_connections()
            print('Crawlers and connections closed')
            self.loop.stop()
            print('Loop closed')

        asyncio.Task(closing_task())

    def _do_some_init(self):
        self.loop.run_until_complete(self.url_dispatcher.init())
        if self.start_url:
            self.loop.run_until_complete(self.url_dispatcher.add_to_visit(
                self.start_url))

    def _parse_cli(self):
        if cli_args.concurrent:
            self.CONCURRENT_MAX = cli_args.concurrent
        if cli_args.slave:
            self.start_url = None

    def _close_connections(self):
        self.url_dispatcher.connection.close()
        self.data_processor.transport.connection.close()

    def set_url_constraint(self, constraint):
        self.url_constraints = [constraint]

    def append_url_constraint(self, constraint):
        self.url_constraints.append(constraint)

    def set_concurrent_crawlers(self, n):
        self.CONCURRENT_MAX = n

    def _new_crawler(self):
        c = Crawler(self.url_dispatcher, self.data_processor)
        c.url_constraints = self.url_constraints
        return c

    @asyncio.coroutine
    def acquire(self):
        yield from self.semaphore.acquire()
        self.concurrent += 1

    def release(self):
        self.semaphore.release()
        self.concurrent -= 1

    def fire_one(self):

        def done_callback():
            self.release()
            asyncio.Task(self.crawler_done())

        future = asyncio.Future()
        asyncio.Task(self._new_crawler().crawl(future))
        future.add_done_callback(lambda res: done_callback())
        return future

    @asyncio.coroutine
    def fire(self):
        future = self.fire_one()
        result = yield from future

    @asyncio.coroutine
    def dispatch_control(self):
        asyncio.Task(self.constant_control(self.cc_future))

    @asyncio.coroutine
    def crawler_done(self):
        while self.concurrent < self.CONCURRENT_MAX:
            yield from self.acquire()
            asyncio.Task(self.fire())

    @asyncio.coroutine
    def constant_control(self, future):
        while not future.done():
            while self.concurrent < self.CONCURRENT_MAX:
                yield from self.acquire()
                asyncio.Task(self.fire())
            yield from asyncio.sleep(1)

if __name__ == '__main__':
    def url_con(url):
        r = re.compile('.*Aktualnosci,Najciekawsze,\d,\d{1,3}\.html$')
        if r.match(url):
            return True
        return False

    cw = CrawlersManager()
    cw.set_url_constraint(url_con)
    asyncio.get_event_loop().run_until_complete(
        cw.dispatch_control())
    asyncio.get_event_loop().run_forever()
