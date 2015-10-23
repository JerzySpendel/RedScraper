import asyncio
from .transport import RedisStorage
from lxml import etree
import json
from io import StringIO
from .helpers import make_generator_if_needed


class DataProcessor:
    def __init__(self):
        self.buffer_size = 10
        self.data_objects = []
        self.storage = RedisStorage()

    def set_data_buffer(self, size):
        self.buffer_size = size

    def set_storage(self, transport):
        self.storage = transport

    def process(self, data):
        raise NotImplementedError()

    def serialize_data_object(self, data_object):
        raise NotImplementedError()

    @asyncio.coroutine
    def feed_with_data(self, data):
        processed = make_generator_if_needed(self.process(data))
        for data_processed in processed:
            if processed is not None:
                self.data_objects.append(data_processed)
                if len(self.data_objects) > self.buffer_size:
                    yield from self.storage.save(self)
                    self.data_objects = []

    def __iter__(self):
        for data_object in self.data_objects:
            yield self.serialize_data_object(data_object)


class CustomProcessor(DataProcessor):

    def process(self, data):
        parser = etree.HTMLParser()
        root = etree.parse(StringIO(data), parser=parser).getroot()
        return root.xpath('//h4[@class="text-h25 title-comments-padding font-serif"]//a//text()')

    def serialize_data_object(self, data_object):
        return json.dumps(data_object)

