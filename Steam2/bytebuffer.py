# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\Steam2\bytebuffer.py


class ByteBuffer:

    def __init__(self, data, position=0, fromEnd=False):
        self.data = data
        self.seekAbsolute(position, fromEnd)
        self.posDict = {}
        self.lastidx = 0

    def read(self, amount):
        if amount >= 0:
            data = self.data[self.position:self.position + amount]
        else:
            start = self.position + amount
            if start < 0:
                start = 0
            data = self.data[start:self.position]
        self.position += amount
        self._limitPosition()
        return data

    def readDelim(self, char, skipChar=False):
        target = self.data.index(char, self.position)
        data = self.read(target - self.position)
        if skipChar:
            self.seekRelative(len(char))
        return data

    def seekRelative(self, amount):
        self.position += amount
        self._limitPosition()

    def seekAbsolute(self, position, fromEnd=False):
        if fromEnd:
            self.position = len(self.data) - position
        else:
            self.position = position
        self._limitPosition()

    def _limitPosition(self):
        if self.position < 0:
            self.position = 0
        elif self.position > len(self.data):
            self.position = len(self.data)

    def save(self, idx):
        self.posDict[idx] = self.position
        self.lastidx = idx

    def load(self, idx):
        if self.lastidx == idx:
            return
        self.save(self.lastidx)
        self.lastidx = idx
        if idx in self.posDict:
            self.position = self.posDict[idx]
        else:
            self.position = 0

    def index(self):
        return self.position

    def eof(self):
        return self.position == len(self.data)