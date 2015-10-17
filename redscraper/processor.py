import asyncio
from transport import RedisTransport
from lxml import etree
import json
from io import StringIO


class DataProcessor:
    def __init__(self):
        self.buffer_size = 10
        self.data_objects = []
        self.transport = RedisTransport()

    def set_data_buffer(self, size):
        self.buffer_size = size

    def set_transport(self, transport):
        self.transport = transport

    @asyncio.coroutine
    def process(self, data):
        pass

    def serialize_data_object(self, data_object):
        pass

    @asyncio.coroutine
    def feed_with_data(self, data):
        processed = yield from self.process(data)
        if processed is not None:
            self.data_objects.append(processed)
            if len(self.data_objects) > self.buffer_size:
                yield from self.transport.save(self)
                self.data_objects = []

    def __iter__(self):
        for data_object in self.data_objects:
            yield self.serialize_data_object(data_object)


class CustomProcessor(DataProcessor):

    @asyncio.coroutine
    def process(self, data):
        parser = etree.HTMLParser()
        root = etree.parse(StringIO(data), parser=parser).getroot()
        return root.xpath('//h4[@class="text-h25 title-comments-padding font-serif"]//a//text()')

    def serialize_data_object(self, data_object):
        return json.dumps(data_object)

