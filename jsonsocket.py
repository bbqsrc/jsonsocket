import asyncio

from pyyajl import YajlParser, YajlContentHandler
from collections import OrderedDict

class OrderedJSONHandler(YajlContentHandler):
    def __init__(self, cb):
        self.tokens = []
        self.cur = None
        self.key = None
        self.cb = cb

    def _add(self, v):
        if isinstance(self.cur, OrderedDict):
            self.cur[self.key] = v
        if isinstance(self.cur, list):
            self.cur.append(v)

    def boolean(self, v):
        self._add(v)

    def string(self, v):
        self._add(v.decode('utf-8'))

    def integer(self, v):
        self._add(v)

    def number(self, v):
        self._add(int(v))

    def start_map(self):
        self.tokens.append(OrderedDict())
        if self.key is not None:
            self._add(self.tokens[-1])
        self.cur = self.tokens[-1]

    def map_key(self, v):
        self.key = v.decode('utf-8')

    def end_map(self):
        x = self.tokens.pop()

        if len(self.tokens) == 0:
            self.cb(x)
            self.cur = None
        else:
            self.cur = self.tokens[-1]

    def start_array(self):
        self.tokens.append([])
        self.cur = self.tokens[-1]

    def end_array(self):
        self.tokens.pop()
        self.cur = self.tokens[-1]


class JSONServer(asyncio.Protocol):
    def connection_made(self, transport):
        self.parser = YajlParser(OrderedJSONHandler(self.on_json),
                allow_multiple_values=True)

    def data_received(self, data):
        self.parser.parse_chunk(data)

    def on_json(self, data):
        print(data)


loop = asyncio.get_event_loop()
coro = loop.create_server(JSONServer, '127.0.0.1', 8888)
server = loop.run_until_complete(coro)


try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    server.close()
    loop.close()
