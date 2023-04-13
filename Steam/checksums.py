# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\Steam\checksums.py
import struct, zlib, logging, sys, os, globalvars
from Steam.gcf import GCF

class Checksums:

    def __init__(self, checksumdata=''):
        if len(checksumdata):
            self.checksumdata = checksumdata
            self.initialize()

    def load_from_file(self, filename):
        f = open(filename, 'rb')
        self.checksumdata = f.read()
        f.close()
        self.initialize()

    def initialize(self):
        dummy, dummy2, numfiles, totalchecksums = struct.unpack('<LLLL', self.checksumdata[:16])
        self.numfiles = numfiles
        self.totalchecksums = totalchecksums
        self.checksumliststart = numfiles * 8 + 16
        self.numchecksums = {}
        self.checksumstart = {}
        self.checksums = {}
        self.checksums_raw = {}
        for fileid in range(self.numfiles):
            checksumpointer = fileid * 8 + 16
            self.numchecksums[fileid], self.checksumstart[fileid] = struct.unpack('<LL', self.checksumdata[checksumpointer:checksumpointer + 8])
            filechecksums = []
            start = self.checksumliststart + self.checksumstart[fileid] * 4
            end = start + self.numchecksums[fileid] * 4
            self.checksums_raw[fileid] = self.checksumdata[start:end]
            for i in range(self.numchecksums[fileid]):
                checksum = struct.unpack('<i', self.checksumdata[start:start + 4])[0]
                filechecksums.append(checksum)
                start += 4

            self.checksums[fileid] = filechecksums

    def validate(self, fileid, file):
        if len(file) != self.numchecksums[fileid]:
            logging.error('Differing amount of chunks in file and checksum list. File: %s List: %s' % (len(file), self.numchecksums[fileid]))
            sys.exit()
        for chunkid in range(len(file)):
            result = self.validate_chunk(fileid, chunkid, file[chunkid])
            if result == False:
                return False

        return True

    def validate_chunk(self, fileid, chunkid, chunk, filename):
        try:
            stored_crc = self.checksums[fileid][chunkid]
        except IndexError:
            logging.error("Checksum error. Tried to check a chunkid that doesn't have a checksum. Chunk %s in file %s" % (chunkid, fileid))
            return False

        chunk_crc = zlib.adler32(chunk, 0) ^ zlib.crc32(chunk, 0)
        if stored_crc != chunk_crc:
            self.fix_crc(fileid, chunkid, chunk, filename)
            return False
        else:
            return True

    def fix_crc(self, fileid, chunkid, chunk, filename):
        f = open(filename, 'rb')
        checksumdata = f.read()
        f.close()
        stored_crc = self.checksums[fileid][chunkid]
        chunk_crc = zlib.adler32(chunk, 0) ^ zlib.crc32(chunk, 0)
        print 'Fixing CRC from ' + str(stored_crc) + ' to ' + str(chunk_crc) + ' on FileID ' + str(fileid)
        dummy, dummy2, numfiles, totalchecksums = struct.unpack('<LLLL', checksumdata[:16])
        numfiles = numfiles
        totalchecksums = totalchecksums
        checksumliststart = numfiles * 8 + 16
        numchecksums = {}
        checksumstart = {}
        checksums = {}
        checksums_raw = {}
        checksumpointer = fileid * 8 + 16
        numchecksums[fileid], checksumstart[fileid] = struct.unpack('<LL', checksumdata[checksumpointer:checksumpointer + 8])
        filechecksums = []
        start = checksumliststart + checksumstart[fileid] * 4
        end = start + numchecksums[fileid] * 4
        checksums_raw[fileid] = checksumdata[start:end]
        print len(checksumdata)
        print len(checksumdata[0:start])
        print len(checksumdata[start:start + 4])
        print len(checksumdata[start + 4:len(checksumdata)])
        checksumdatanew = checksumdata[0:start]
        print len(checksumdatanew)
        checksumdatanew_temp = ''
        print 'Checksum count: ' + str(range(numchecksums[fileid]))
        for i in range(numchecksums[fileid]):
            checksum = struct.unpack('<i', checksumdata[start:start + 4])[0]
            print struct.unpack('<i', checksumdata[start:start + 4])
            print 'Checksum: ' + str(checksum)
            if checksum == stored_crc:
                print 'CRC CHANGED!'
                checksumdatanew_temp = struct.pack('<i', chunk_crc)
                print struct.unpack('<i', checksumdatanew_temp)
                print len(checksumdatanew_temp)
                checksumdatanew = checksumdatanew + checksumdatanew_temp
                print len(checksumdatanew)
            else:
                print 'Stored only'
                checksumdatanew_temp = struct.pack('<i', checksum)
                print struct.unpack('<i', checksumdatanew_temp)
                print len(checksumdatanew_temp)
                checksumdatanew = checksumdatanew + checksumdatanew_temp
                print len(checksumdatanew)
            start += 4

        print len(checksumdatanew)
        print len(checksumdata[start:len(checksumdata)])
        checksumdatanew = checksumdatanew + checksumdata[start:len(checksumdata)]
        print len(checksumdatanew)
        for i in range(numchecksums[fileid]):
            checksum = struct.unpack('<i', checksumdatanew[start:start + 4])
            if checksum == chunk_crc:
                print 'Checksum validated'
            start += 4

        if len(checksumdata) != len(checksumdatanew):
            print 'Old and new checksums are different sizes: ' + str(len(checksumdata)) + ' to ' + str(len(checksumdatanew))
            sys.exit()
        else:
            print 'Old and new checksums are correct sizes.'
        f = open(filename, 'wb')
        f.write(checksumdatanew)
        f.close()