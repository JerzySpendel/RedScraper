import aiohttp
import aiohttp.http_exceptions
import asyncio
from .settings import config
from .exceptions import BadResponse


class Request:
    timeout = int(config['scraper']['request_timeout'])
    session = None

    def __init__(self, url):
        self.url = url

    def _headers(self):
        return {'User-Agent': 'Web Scrapper'}

    def _validate_response(self, resp):
        if 'text/html' not in resp.headers['Content-Type']:
            return False
        if not resp.status == 200:
            return False
        return True

    async def get_or_create_session(self):
        if self.session:
            return self.session

        async with aiohttp.ClientSession() as session:
            self.session = session

        return self.session

    @asyncio.coroutine
    def download(self, timeout_happened=False):
        try:
            request_task = aiohttp.request('get', self.url, headers=self._headers())
            r = yield from asyncio.wait_for(request_task, timeout=self.timeout)
            if not self._validate_response(r):
                raise BadResponse()
            text = yield from r.text()
            r.close()
            return text
        except aiohttp.http_exceptions.ContentEncodingError:
            print('Bad response')
        except asyncio.TimeoutError:
            if timeout_happened:
                raise BadResponse()
            print('Timeout, second try')
            return (yield from self.download(timeout_happened=True))
