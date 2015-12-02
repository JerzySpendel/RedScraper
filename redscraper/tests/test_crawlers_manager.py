import asyncio
import aiohttp
from .utils import HttpServer


class TestHttpServerTestCase:
    """
    Testing that Http server for testing purposes
    serves 20-subpages with certain content
    """

    def setup_method(self, method):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.f = self.loop.create_server(lambda: HttpServer(), '0.0.0.0', '8080')
        self.srv = self.loop.run_until_complete(self.f)

    def test_http_server(self):

        @asyncio.coroutine
        def getter():
            res = yield from aiohttp.get('http://0.0.0.0:8080')
            res.close()
            res = yield from aiohttp.get('http://0.0.0.0:8080/close')
            res.close()

        asyncio.ensure_future(getter())
        self.loop.run_forever()

    def test_http_20_pages(self):
        template = 'Content to be scrapped {}'
        future = asyncio.Future()

        @asyncio.coroutine
        def getter(future):
            result = True
            for i in range(20):
                response = yield from aiohttp.get('http://0.0.0.0:8080/{}'.format(i))
                if template.format(i) not in (yield from response.text()):
                    result = False
                response.close()
            future.set_result(result)
            (yield from aiohttp.get('http://0.0.0.0:8080/close')).close()

        asyncio.ensure_future(getter(future))
        self.loop.run_forever()
        assert future.result()

    def teardown_method(self, method):
        self.srv.close()
        self.f.close()
        self.loop.stop()

