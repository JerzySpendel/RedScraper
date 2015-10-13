import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import time


regex = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
    r'localhost|' # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def download(url):
    t = asyncio.Task(aiohttp.get(url))
    return t


class URLDispatcher:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.to_visit = []
        self.visited = []

    @asyncio.coroutine
    def add_url_to_visit(self, url):
        with (yield from self.lock):
            if url not in self.to_visit and url not in self.visited:
                self.to_visit.append(url)

    @asyncio.coroutine
    def get_url(self):
        while len(self.to_visit) == 0:
            yield from asyncio.sleep(0.1)
        with (yield from self.lock):
            return self.to_visit.pop()

    @asyncio.coroutine
    def add_to_visited(self, url):
        with (yield from self.lock):
            self.visited.append(url)


class Crawler:
    domains = ['dobreprogramy.pl']

    def __init__(self, urldis):
        self.urldis = urldis

    @asyncio.coroutine
    def crawl(self, future):
        url = yield from self.urldis.get_url()
        print(url)
        site_downloader = download(url)
        d = yield from site_downloader
        html = yield from d.text()
        for url in self.get_urls(html):
            pass
        yield from self.urldis.add_to_visited(url)
        future.set_result(None)

    def get_urls(self, html):
        soup = BeautifulSoup(html, 'lxml')
        ass = soup.find_all('a')
        for i in range(len(ass)):
            try:
                href = ass[i].get('href')
                if not regex.match(href):
                    continue
                if not self.domains[0] in href:
                    continue
                yield from self.urldis.add_url_to_visit(href)
                yield urlparse(href).netloc
            except:
                pass


class DataProcessor:
    def __init__(self):
        self.data = []


class CrawlersManager:
    CONCURRENT_MAX = 100

    def __init__(self):
        self.url_dispatcher = URLDispatcher()
        self.semaphore = asyncio.Semaphore(value=100)
        self.control_lock = asyncio.Lock()
        self.url_dispatcher.to_visit.append('http://dobreprogramy.pl')
        self.concurrent = 0

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
            asyncio.Task(self.dispatch_control())

        future = asyncio.Future()
        asyncio.Task(Crawler(self.url_dispatcher).crawl(future))
        future.add_done_callback(lambda res: done_callback())
        return future

    @asyncio.coroutine
    def fire(self):
        future = self.fire_one()
        result = yield from future
        yield from asyncio.sleep(10000)

    @asyncio.coroutine
    def dispatch_control(self):
        with (yield from self.control_lock):
            while self.concurrent != self.CONCURRENT_MAX:
                yield from self.acquire()
                asyncio.Task(self.fire())


urldispatcher = URLDispatcher()
asyncio.get_event_loop().run_until_complete(CrawlersManager().dispatch_control())
asyncio.get_event_loop().run_forever()
