# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\Steam\manifest.py
import struct

class DirectoryEntry:
    pass


class Manifest:

    def __init__(self, manifestdata=''):
        if len(manifestdata):
            self.manifestdata = manifestdata
            self.initialize()

    def load_from_file(self, filename):
        f = open(filename, 'rb')
        self.manifestdata = f.read()
        f.close()
        self.initialize()

    def initialize(self):
        self.dummy1, self.stored_appid, self.stored_appver, self.num_items, self.num_files, self.blocksize, self.dirsize, self.dirnamesize, self.info1count, self.copycount, self.localcount, self.dummy2, self.dummy3, self.checksum = struct.unpack('<LLLLLLLLLLLLLL', self.manifestdata[0:56])
        self.dirnames_start = 56 + self.num_items * 28
        self.dir_entries = {}
        for i in range(self.num_items):
            index = 56 + i * 28
            d = DirectoryEntry()
            d.nameoffset, d.itemsize, d.fileid, d.dirtype, d.parentindex, d.nextindex, d.firstindex = struct.unpack('<LLLLLLL', self.manifestdata[index:index + 28])
            filename_start = self.dirnames_start + d.nameoffset
            filename_end = self.manifestdata.index('\x00', filename_start)
            d.filename = self.manifestdata[filename_start:filename_end]
            self.dir_entries[i] = d

        for i in range(self.num_items):
            d = self.dir_entries[i]
            fullfilename = d.filename
            while d.parentindex != 4294967295L:
                d = self.dir_entries[d.parentindex]
                fullfilename = d.filename + '/' + fullfilename

            d = self.dir_entries[i]
            d.fullfilename = fullfilename

    def make_encrypted(self, filename):
        f = open(filename, 'rb')
        self.manifestdata = f.read()
        f.close()
        print len(self.manifestdata)
        self.dummy1, self.stored_appid, self.stored_appver, self.num_items, self.num_files, self.blocksize, self.dirsize, self.dirnamesize, self.info1count, self.copycount, self.localcount, self.dummy2, self.dummy3, self.checksum = struct.unpack('<LLLLLLLLLLLLLL', self.manifestdata[0:56])
        manifestdatanew = self.manifestdata[0:56]
        self.dirnames_start = 56 + self.num_items * 28
        print len(self.manifestdata[0:56])
        print len(self.manifestdata[56:len(self.manifestdata)])
        self.dir_entries = {}
        for i in range(self.num_items):
            index = 56 + i * 28
            print str(index)
            d = DirectoryEntry()
            d.nameoffset, d.itemsize, d.fileid, d.dirtype, d.parentindex, d.nextindex, d.firstindex = struct.unpack('<LLLLLLL', self.manifestdata[index:index + 28])
            if len(hex(d.dirtype)) == 6:
                dirtypenew = d.dirtype + 256
                manifestdatanew_temp = struct.pack('<LLLLLLL', d.nameoffset, d.itemsize, d.fileid, dirtypenew, d.parentindex, d.nextindex, d.firstindex)
            else:
                manifestdatanew_temp = struct.pack('<LLLLLLL', d.nameoffset, d.itemsize, d.fileid, d.dirtype, d.parentindex, d.nextindex, d.firstindex)
            manifestdatanew = manifestdatanew + manifestdatanew_temp

        manifestdatanew = manifestdatanew + self.manifestdata[len(manifestdatanew):len(self.manifestdata)]
        print len(self.manifestdata[0:56])
        print len(self.manifestdata[56:len(self.manifestdata)])
        print len(self.manifestdata)
        print len(manifestdatanew)
        g = open(filename + 'enc.manifest', 'wb')
        g.write(manifestdatanew)
        g.close()