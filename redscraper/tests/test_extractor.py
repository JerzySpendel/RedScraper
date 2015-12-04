from .utils import TestingExtractor
import asyncio


class TestExtractor:
    test_data_field = 'test_data'

    def _create_test_data(self):
        coros = []
        for i in range(100):
            coros.append(self.extractor.connection.execute("sadd", self.test_data_field, str(i)))
        self.loop.run_until_complete(asyncio.wait(coros))

    def setup_method(self, method):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.extractor = TestingExtractor()
        self._create_test_data()

    def test_indexing(self):
        self.extractor.set_buffer(50)
        self.loop.run_until_complete(self.extractor.get_chunk())
        assert self.extractor.index == 50
        self.loop.run_until_complete(self.extractor.get_chunk())
        assert self.extractor.index == 100

    def teardown_method(self, method):
        self.loop.run_until_complete(self.extractor.connection.execute('del', self.test_data_field))
