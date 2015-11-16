import aiohttp
import asyncio
from .settings import config
from .exceptions import BadResponse


class Request:
    timeout = int(config['scraper']['request_timeout'])

    def __init__(self, url):
        self.url = url

    def _headers(self):
        return {'User-Agent': 'Web Scrapper'}

    @asyncio.coroutine
    def download(self):
        try:
            t = asyncio.Task(aiohttp.get(self.url, headers=self._headers()))
            r = yield from asyncio.wait_for(t, timeout=self.timeout)
            if 'text/html' not in r.headers['Content-Type']:
                raise BadResponse()
            return r
        except aiohttp.errors.ContentEncodingError:
            print('Bad response')
        except asyncio.TimeoutError:
            print('Przedawnienie, jeszcze raz...')
            return (yield from self.download())
