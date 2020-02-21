"""
A class overriding BytesIO to write every line added into a database
"""

from io import BytesIO
import requests


class NetIO(BytesIO):
    def __init__(self, fkhistory, endpoint):
        self.sequence = 1
        self.fkhistory = fkhistory
        self.buffer = BytesIO()
        self.lastflush = self.buffer.tell()
        self.endpoint = endpoint
        super().__init__()

    def close(self):
        return self.buffer.close()

    def closed(self):
        return self.buffer.closed()

    def flush(self):
        if self.lastflush == self.buffer.tell():
            return self.buffer.flush()
        self.buffer.seek(self.lastflush)

        binlog = self.buffer.read()
        postdata = {'fkhistory': self.fkhistory,
                    'sequence': self.sequence,
                    'log': binlog}

        requests.post(self.endpoint + '/api/log/?format=json',
                      data=postdata)

        self.sequence += 1
        self.lastflush = self.buffer.tell()

        return self.buffer.flush()

    def getbuffer(self):
        return self.buffer.getbuffer()

    def getvalue(self):
        return self.buffer.getvalue()

    def read(self, *args):
        return self.buffer.read(*args)

    # def read1
    # def readable
    # def readinto
    # def readinto1
    def readline(self, *args):
        return self.buffer.readline(*args)

    def readlines(self, *args):
        return self.buffer.readlines(*args)

    def seek(self, *args):
        return self.buffer.seek(*args)

    # def seekable
    # def tell
    # def truncate
    # def writable
    def write(self, text):
        return self.buffer.write(text)

    def writelines(self, *args):
        return self.buffer.writelines(*args)
