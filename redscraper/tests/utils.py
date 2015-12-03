from redscraper.processor import DataProcessor

import aiohttp
import asyncio
import aiohttp.server


template = '''
<html>
<body>
<p id="content">Content to be scrapped {identifier}</p>
{other_urls}
</body>
</html>
'''


def render(identifier):
    other = ''
    for i in range(20):
        other = other+'<a href="http://localhost:8080/{}">{}</a><br />'.format(i, i)
    return template.format(identifier=identifier, other_urls=other)


class HttpServer(aiohttp.server.ServerHttpProtocol):

    @asyncio.coroutine
    def handle_request(self, message, payload):
        response = aiohttp.Response(
            self.writer, 200, http_version=message.version
        )
        response.add_header('Content-Type', 'text/html')
        response.send_headers()
        if message.path == '/':
            response.write(render('main page').encode('utf-8'))
        elif message.path == '/close':
            asyncio.get_event_loop().stop()
        else:
            response.write(render(message.path[1:]).encode('utf-8'))
        yield from response.write_eof()


class TestingProcessor(DataProcessor):
    def process(self, data):
        return 1

    def serialize_data_object(self, data_object):
        return "1"
