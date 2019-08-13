"""
A class overriding BytesIO to write every line added into a database
"""

from io import BytesIO
from stageitweb.stageit.models import History, Log

class FakeIO(BytesIO):
    def __init__(self, fkhistory):
        self.sequence = 1
        self.fkhistory = History.objects.get(pkid=fkhistory)
        self.buffer = BytesIO()

    def close(self):
        return self.buffer.close()

    def closed(self):
        return self.buffer.closed()

    def flush(self):
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

    #def seekable
    #def tell
    #def truncate
    #def writable
    def write(self, text):
        row = Log()
        row.fkhistory = self.fkhistory
        row.log = text.decode()
        row.sequence = self.sequence
        self.sequence += self.sequence
        row.save()
        return self.buffer.write(text)

    def writelines(self, *args):
        return self.buffer.writelines(*args)

