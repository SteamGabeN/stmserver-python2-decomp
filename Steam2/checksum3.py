# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\Steam2\checksum3.py
import struct, zlib, os.path, logging
from steamemu.config import read_config
config = read_config()

class Checksum3:

    def __init__(self, arg):
        if type(arg) == int:
            appId = arg
            with open(self.filename(appId), 'rb') as (f):
                self.checksumdata = f.read()
        else:
            self.checksumdata = arg
        formatcode, dummy, numfiles, totalchecksums = struct.unpack('<LLLL', self.checksumdata[:16])
        self.numfiles = numfiles
        self.totalchecksums = totalchecksums
        self.checksumliststart = numfiles * 8 + 16

    def numchecksums(self, fileid):
        checksumpointer = fileid * 8 + 16
        return struct.unpack('<L', self.checksumdata[checksumpointer:checksumpointer + 4])[0]

    def getchecksum(self, fileid, chunkid):
        checksumpointer = fileid * 8 + 16
        checksumstart = struct.unpack('<L', self.checksumdata[checksumpointer + 4:checksumpointer + 8])[0]
        start = self.checksumliststart + (checksumstart + chunkid) * 4
        return struct.unpack('<i', self.checksumdata[start:start + 4])[0]

    def getchecksums_raw(self, fileid):
        checksumpointer = fileid * 8 + 16
        numchecksums, checksumstart = struct.unpack('<LL', self.checksumdata[checksumpointer:checksumpointer + 8])
        start = self.checksumliststart + checksumstart * 4
        return self.checksumdata[start:start + numchecksums * 4]

    def validate(self, fileid, chunkid, chunk):
        crc = self.getchecksum(fileid, chunkid)
        crcb = zlib.adler32(chunk, 0) ^ zlib.crc32(chunk, 0)
        if crc != crcb:
            logging.warning('CRC error: %i %s %s' % (fileid, hex(crc), hex(crcb)))
            return False
        else:
            return True

    @classmethod
    def filename(cls, appId):
        return os.path.join(config['v2storagedir'], '%i.checksums' % appId)