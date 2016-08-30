from redscraper.processor import DataProcessor
from redscraper.scraper import CrawlersManager
import asyncio
import re
from lxml import etree
from io import StringIO
import json


class DPProcessor(DataProcessor):
    def process(self, data):
        parser = etree.HTMLParser()
        root = etree.parse(StringIO(data), parser=parser).getroot()
        data = root.xpath('//div[@class="clearfix"]/header/h4/a/text()')
        yield from data

    def serialize_data_object(self, data_object):
        return json.dumps(data_object)


def url_filter(url):
    r = re.compile('.*Najciekawsze,0,\d+.*?')
    if r.match(url):
        return True
    return False

cw = CrawlersManager(DPProcessor())
cw.append_url_constraint(url_filter)
asyncio.get_event_loop().run_until_complete(
    cw.run()
)
