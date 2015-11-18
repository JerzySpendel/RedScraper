from redscraper.processor import DataProcessor
from redscraper.scraper import CrawlersManager
import asyncio
import re
from lxml import etree
from io import StringIO
import json


class TPBProcessor(DataProcessor):
    def process(self, data):
        parser = etree.HTMLParser()
        root = etree.parse(StringIO(data), parser=parser).getroot()
        yield from root.xpath('//a[@class="cellMainLink"]/text()')

    def serialize_data_object(self, data_object):
        return json.dumps(data_object)


def new_url(url):
    r = re.compile('.*new/\d+')
    if r.match(url):
        return True
    return False

cw = CrawlersManager(TPBProcessor())
cw.append_url_constraint(new_url)
asyncio.get_event_loop().run_until_complete(
    cw.run()
)
asyncio.get_event_loop().run_forever()
