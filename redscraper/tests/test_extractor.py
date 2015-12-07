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

    def test_get_chunk(self):

        @asyncio.coroutine
        def testing_coro(future):
            chunk = yield from self.extractor.get_chunk()
            future.set_result(len(chunk))

        for i in range(1, 4):
            self.extractor.set_buffer(i*10)
            future = asyncio.Future()
            asyncio.ensure_future(testing_coro(future))
            length = self.loop.run_until_complete(future)
            assert length == i*10

    def teardown_method(self, method):
        self.loop.run_until_complete(self.extractor.connection.execute('del', self.test_data_field))
