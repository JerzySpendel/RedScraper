import aiohttp
import asyncio
from .settings import config


class Request:
    timeout = int(config['scraper']['request_timeout'])

    def __init__(self, url):
        self.url = url

    @asyncio.coroutine
    def download(self):
        try:
            t = asyncio.Task(aiohttp.get(self.url))
            return (yield from asyncio.wait_for(t, timeout=self.timeout))
        except aiohttp.ContentEncodingError:
            print('Bad response')
        except asyncio.TimeoutError:
            print('Przedawnienie, jeszcze raz...')
            return (yield from self.download())
