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

    def _validate_response(self, resp):
        if 'text/html' not in resp.headers['Content-Type']:
            return False
        return True

    @asyncio.coroutine
    def download(self, timeout_happened=False):
        try:
            t = asyncio.Task(aiohttp.get(self.url, headers=self._headers()))
            r = yield from asyncio.wait_for(t, timeout=self.timeout)
            if not self._validate_response(r):
                raise BadResponse()
            return r
        except aiohttp.errors.ContentEncodingError:
            print('Bad response')
        except asyncio.TimeoutError:
            if timeout_happened:
                raise BadResponse()
            print('Timeout, second try')
            return (yield from self.download(timeout_happened=True))
