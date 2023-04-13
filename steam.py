# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\steam.py
import binascii, socket, struct, zlib, os, sys, logging
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Cipher import AES
from steamemu.config import read_config
config = read_config()
main_key_sign = RSA.construct((
 16972286244849771984622451367228102174501719320240653652662330551811042672286869215561928929175827402752178598753445713908601088303475414633015321035251571211566978795872136026380777563265395267739035345972002870926699475330208864762370786289338571780113370443705220053580642621034990905081765661421515793197322286229310533378663925641599451069026309189868652973825372527822995378307658254979118985781849587869182040447299629997994344818433422788110169038839718660945475305838947440389938769132300261658746306829589651102747347903636404092182462550116241824059779050479962155170547507469291673134785087525867735462771L,
 998369779108810116742497139248711892617748195308273744274254738341826039546286424444819348775048670750128152867849747876976534606086789096059724766779504188915704635051302119198869268427376192219943255645411933583923498548835815574257105075843445398830198261394424709034155448296175935593045038907147987835121276143092265929765857522003315234046704493380086236406227181752690639773759910381564885451567942201551660793531581412046961847318500202889539128927129171613072773956837051742450320264942416013004138711897082646106738944678776002164289048233329862454552712571702039963458146099156364834927612038865038435329L,
 17L))
network_key = RSA.construct((
 134539629474386922037791973580118887976202262513059806716070824872604019001549619717043869049820865778686338042804246699105615306763509624582695524159630542063424520740697096695065917367798513676047684857537002873465544160954589243833288573668688641279313120835560801603892833928651320394652562952389632548953L,
 17L,
 55398670960041673780267283238872483284318578681848155706617398476954596059461608118782769608749768261812021547037042758455253361608503963063462862889259625398654146184924437001549904434764958250148333879602146773194545846894891569844887509155520581612255537741780582148990843840620079165238381404172781505181L))
network_key_sign = RSA.construct((
 134539629474386922037791973580118887976202262513059806716070824872604019001549619717043869049820865778686338042804246699105615306763509624582695524159630542063424520740697096695065917367798513676047684857537002873465544160954589243833288573668688641279313120835560801603892833928651320394652562952389632548953L,
 55398670960041673780267283238872483284318578681848155706617398476954596059461608118782769608749768261812021547037042758455253361608503963063462862889259625398654146184924437001549904434764958250148333879602146773194545846894891569844887509155520581612255537741780582148990843840620079165238381404172781505181L,
 17L))

def decodeIP(string):
    oct1, oct2, oct3, oct4, port = struct.unpack('<BBBBH', string)
    ip = '%d.%d.%d.%d' % (oct1, oct2, oct3, oct4)
    return (ip, port)


def encodeIP((ip, port)):
    if type(port) == str:
        port = int(port)
    oct = ip.split('.')
    string = struct.pack('<BBBBH', int(oct[0]), int(oct[1]), int(oct[2]), int(oct[3]), port)
    return string


def blob_unserialize(blobtext):
    blobdict = {}
    totalsize, slack = struct.unpack('<LL', blobtext[2:10])
    if slack:
        blobdict['__slack__'] = blobtext[-slack:]
    if totalsize + slack != len(blobtext):
        raise NameError, 'Blob not correct length including slack space!'
    index = 10
    while index < totalsize:
        namestart = index + 6
        namesize, datasize = struct.unpack('<HL', blobtext[index:namestart])
        datastart = namestart + namesize
        name = blobtext[namestart:datastart]
        dataend = datastart + datasize
        data = blobtext[datastart:dataend]
        if len(data) > 1 and data[0] == chr(1) and data[1] == chr(80):
            sub_blob = blob_unserialize(data)
            blobdict[name] = sub_blob
        else:
            blobdict[name] = data
        index = index + 6 + namesize + datasize

    return blobdict


def blob_serialize(blobdict):
    blobtext = ''
    for name, data in blobdict.iteritems():
        if name == '__slack__':
            continue
        if type(data) == dict:
            data = blob_serialize(data)
        namesize = len(name)
        datasize = len(data)
        subtext = struct.pack('<HL', namesize, datasize)
        subtext = subtext + name + data
        blobtext = blobtext + subtext

    if blobdict.has_key('__slack__'):
        slack = blobdict['__slack__']
    else:
        slack = ''
    totalsize = len(blobtext) + 10
    sizetext = struct.pack('<LL', totalsize, len(slack))
    blobtext = chr(1) + chr(80) + sizetext + blobtext + slack
    return blobtext


def steam_download_package(fileserver, filename, outfilename):
    s = ImpSocket()
    s.connect(fileserver)
    s.send('\x00\x00\x00\x03')
    s.recv(1)
    message = struct.pack('>LLL', 0, 0, len(filename)) + filename + '\x00\x00\x00\x05'
    s.send_withlen(message)
    response = s.recv(8)
    datalen = struct.unpack('>LL', response)[0]
    f = open(outfilename, 'wb')
    while datalen:
        reply = s.recv(datalen)
        datalen = datalen - len(reply)
        f.write(reply)

    f.close()
    s.close()


def steam_get_fileservers(contentserver, app, ver, numservers):
    command = '\x00\x00\x01' + struct.pack('>LLHL', app, ver, numservers, 0) + '\xff\xff\xff\xff\xff\xff\xff\xff'
    s = ImpSocket()
    s.connect(contentserver)
    s.send('\x00\x00\x00\x02')
    s.recv(1)
    s.send_withlen(command)
    reply = s.recv_withlen()
    s.close()
    numadds = struct.unpack('>H', reply[:2])[0]
    addresses = []
    for i in range(numadds):
        start = i * 16 + 2
        serverid = struct.unpack('>L', reply[start:start + 4])[0]
        server1 = decodeIP(reply[start + 4:start + 10])
        server2 = decodeIP(reply[start + 10:start + 16])
        addresses.append((serverid, server1, server2))

    return addresses


def steam_get_authserver(dirserver, namehash):
    s = ImpSocket()
    s.connect(dirserver)
    s.send('\x00\x00\x00\x02')
    s.recv(1)
    s.send_withlen('\x00' + namehash)
    reply = s.recv_withlen()
    s.close()
    numadds = struct.unpack('>H', reply[:2])[0]
    addresses = []
    for i in range(numadds):
        start = i * 6 + 2
        server = decodeIP(reply[start:start + 6])
        addresses.append(server)

    return addresses


def package_unpack(infilename, outpath):
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    infile = open(infilename, 'rb')
    package = infile.read()
    infile.close()
    header = package[-9:]
    pkg_ver, compress_level, numfiles = struct.unpack('<BLL', package[-9:])
    index = len(package) - 25
    for i in range(numfiles):
        unpacked_size, packed_size, file_start, filename_len = struct.unpack('<LLLL', package[index:index + 16])
        filename = package[index - filename_len:index - 1]
        filepath, basename = os.path.split(filename)
        index = index - (filename_len + 16)
        file = ''
        while packed_size > 0:
            compressed_len = struct.unpack('<L', package[file_start:file_start + 4])[0]
            compressed_start = file_start + 4
            compressed_end = compressed_start + compressed_len
            compressed_data = package[compressed_start:compressed_end]
            file = file + zlib.decompress(compressed_data)
            file_start = compressed_end
            packed_size = packed_size - compressed_len

        outsubpath = os.path.join(outpath, filepath)
        if not os.path.exists(outsubpath):
            os.makedirs(outsubpath)
        outfullfilename = os.path.join(outpath, filename)
        outfile = open(outfullfilename, 'wb')
        outfile.write(file)
        outfile.close()


def package_pack(directory, outfilename):
    filenames = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            if directory != root[0:len(directory)]:
                print 'ERROR!!!!!!'
                sys.exit()
            filename = os.path.join(root, name)
            filename = filename[len(directory):]
            filenames.append(filename)

    outfileoffset = 0
    datasection = ''
    indexsection = ''
    numberoffiles = 0
    for filename in filenames:
        infile = open(directory + filename, 'rb')
        filedata = infile.read()
        infile.close()
        index = 0
        packedbytes = 0
        for i in range(0, len(filedata), 32768):
            chunk = filedata[i:i + 32768]
            packedchunk = zlib.compress(chunk, 9)
            packedlen = len(packedchunk)
            datasection = datasection + struct.pack('<L', packedlen) + packedchunk
            packedbytes = packedbytes + packedlen

        indexsection = indexsection + filename + '\x00' + struct.pack('<LLLL', len(filedata), packedbytes, outfileoffset, len(filename) + 1)
        outfileoffset = len(datasection)
        numberoffiles = numberoffiles + 1

    fulloutfile = datasection + indexsection + struct.pack('<BLL', 0, 9, numberoffiles)
    outfile = open(outfilename, 'wb')
    outfile.write(fulloutfile)
    outfile.close()


def readindexes(filename):
    indexes = {}
    filemodes = {}
    if os.path.isfile(filename):
        f = open(filename, 'rb')
        indexdata = f.read()
        f.close()
        indexptr = 0
        while indexptr < len(indexdata):
            fileid, indexlen, filemode = struct.unpack('>QQQ', indexdata[indexptr:indexptr + 24])
            if indexlen:
                indexes[fileid] = indexdata[indexptr + 24:indexptr + 24 + indexlen]
                filemodes[fileid] = filemode
            indexptr = indexptr + 24 + indexlen

    return (
     indexes, filemodes)


def readindexes_old(filename):
    indexes = {}
    filemodes = {}
    if os.path.isfile(filename):
        f = open(filename, 'rb')
        indexdata = f.read()
        f.close()
        indexptr = 0
        while indexptr < len(indexdata):
            fileid, indexlen, filemode = struct.unpack('>LLL', indexdata[indexptr:indexptr + 12])
            if indexlen:
                indexes[fileid] = indexdata[indexptr + 12:indexptr + 12 + indexlen]
                filemodes[fileid] = filemode
            indexptr = indexptr + 12 + indexlen

    return (
     indexes, filemodes)


class Storage():

    def __init__(self, storagename, path, version):
        self.name = str(storagename)
        self.ver = str(version)
        if path.endswith('storages/'):
            manifestpathnew = config['manifestdir']
            manifestpathold = config['v2manifestdir']
        if os.path.isfile('files/cache/' + self.name + '_' + self.ver + '/' + self.name + '_' + self.ver + '.manifest'):
            self.indexfile = 'files/cache/' + self.name + '_' + self.ver + '/' + self.name + '.index'
            self.datafile = 'files/cache/' + self.name + '_' + self.ver + '/' + self.name + '.data'
            self.indexes, self.filemodes = readindexes(self.indexfile)
            self.new = True
        elif os.path.isfile(manifestpathold + self.name + '_' + self.ver + '.manifest'):
            self.indexfile = config['v2storagedir'] + self.name + '.index'
            self.datafile = config['v2storagedir'] + self.name + '.data'
            self.indexes, self.filemodes = readindexes_old(self.indexfile)
            self.new = False
        else:
            self.indexfile = config['storagedir'] + self.name + '.index'
            self.datafile = config['storagedir'] + self.name + '.data'
            self.indexes, self.filemodes = readindexes(self.indexfile)
            self.new = True
        self.f = False

    def readchunk(self, fileid, chunkid):
        index = self.indexes[fileid]
        if not self.f:
            self.f = open(self.datafile, 'rb')
        pos = chunkid * 16
        start, length = struct.unpack('>QQ', index[pos:pos + 16])
        self.f.seek(start)
        file = self.f.read(length)
        return (
         file, self.filemodes[fileid])

    def readchunks(self, fileid, chunkid, maxchunks):
        if self.new:
            filechunks = []
            index = self.indexes[fileid]
            if not self.f:
                self.f = open(self.datafile, 'rb')
            indexstart = chunkid * 16
            for pos in range(indexstart, len(index), 16):
                start, length = struct.unpack('>QQ', index[pos:pos + 16])
                self.f.seek(start)
                filechunks.append(self.f.read(length))
                maxchunks = maxchunks - 1
                if maxchunks == 0:
                    break

            return (
             filechunks, self.filemodes[fileid])
        else:
            filechunks = []
            index = self.indexes[fileid]
            f = open(self.datafile, 'rb')
            indexstart = chunkid * 8
            for pos in range(indexstart, len(index), 8):
                start, length = struct.unpack('>LL', index[pos:pos + 8])
                f.seek(start)
                filechunks.append(f.read(length))
                maxchunks = maxchunks - 1
                if maxchunks == 0:
                    break

            return (
             filechunks, self.filemodes[fileid])

    def readfile(self, fileid):
        filechunks = []
        index = self.indexes[fileid]
        if not self.f:
            self.f = open(self.datafile, 'rb')
        for pos in range(0, len(index), 16):
            start, length = struct.unpack('>QQ', index[pos:pos + 16])
            self.f.seek(start)
            filechunks.append(self.f.read(length))

        return (filechunks, self.filemodes[fileid])

    def writefile(self, fileid, filechunks, filemode):
        if self.indexes.has_key(fileid):
            print 'FileID already exists!'
            sys.exit()
        if self.f:
            self.f.close()
            self.f = False
        f = open(self.datafile, 'a+b')
        fi = open(self.indexfile, 'ab')
        f.seek(0, 2)
        outindex = struct.pack('>QQQ', fileid, len(filechunks) * 16, filemode)
        for chunk in filechunks:
            outfilepos = f.tell()
            outindex = outindex + struct.pack('>QQ', outfilepos, len(chunk))
            f.write(chunk)

        fi.write(outindex)
        f.close()
        fi.close()
        self.indexes[fileid] = outindex[24:]
        self.filemodes[fileid] = filemode

    def close(self):
        if self.f:
            self.f.close()
            self.f = False


class Checksum():

    def __init__(self, checksumdata=''):
        self.checksumdata = checksumdata
        if len(checksumdata):
            self.initialize()

    def loadfromfile(self, filename):
        f = open(filename, 'rb')
        self.checksumdata = f.read()
        f.close()
        self.initialize()

    def initialize(self):
        dummy, dummy2, numfiles, totalchecksums = struct.unpack('<LLLL', self.checksumdata[:16])
        self.numfiles = numfiles
        self.totalchecksums = totalchecksums
        self.checksumliststart = numfiles * 8 + 16

    def numchecksums(self, fileid):
        checksumpointer = fileid * 8 + 16
        numchecksums, checksumstart = struct.unpack('<LL', self.checksumdata[checksumpointer:checksumpointer + 8])
        return numchecksums

    def getchecksum(self, fileid, chunkid):
        checksumpointer = fileid * 8 + 16
        numchecksums, checksumstart = struct.unpack('<LL', self.checksumdata[checksumpointer:checksumpointer + 8])
        start = self.checksumliststart + (checksumstart + chunkid) * 4
        crc = struct.unpack('<i', self.checksumdata[start:start + 4])[0]
        return crc

    def validate(self, fileid, chunkid, chunk):
        crc = self.getchecksum(fileid, chunkid)
        crcb = valvecrc.crc(chunk, 0) ^ zlib.crc32(chunk, 0)
        if crc != crcb:
            logging.warning('CRC error: %i %s %s' % (fileid, hex(crc), hex(crcb)))
            return False
        else:
            return True


class ImpSocket():
    """improved socket class - this is REALLY braindead because the socket class doesn't let me override some methods, so I have to build from scratch"""

    def __init__(self, sock=None):
        if sock is None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.s = sock
        return

    def accept(self):
        returnedsocket, address = self.s.accept()
        newsocket = ImpSocket(returnedsocket)
        newsocket.address = address
        return (
         newsocket, address)

    def bind(self, address):
        self.address = address
        self.s.bind(address)

    def connect(self, address):
        self.address = address
        self.s.connect(address)
        logging.debug(str(self.address) + ': Connecting to address')

    def close(self):
        self.s.close()

    def listen(self, connections):
        self.s.listen(connections)

    def send(self, data, log=True):
        sentbytes = self.s.send(data)
        if log:
            logging.debug(str(self.address) + ': Sent data - ' + binascii.b2a_hex(data))
        if sentbytes != len(data):
            logging.warning("NOTICE!!! Number of bytes sent doesn't match what we tried to send " + str(sentbytes) + ' ' + str(len(data)))
        return sentbytes

    def sendto(self, data, address, log=True):
        sentbytes = self.s.sendto(data, address)
        if log:
            logging.debug(str(address) + ': sendto Sent data - ' + binascii.b2a_hex(data))
        if sentbytes != len(data):
            logging.warning("NOTICE!!! Number of bytes sent doesn't match what we tried to send " + str(sentbytes) + ' ' + str(len(data)))
        return sentbytes

    def send_withlen(self, data, log=True):
        lengthstr = struct.pack('>L', len(data))
        if log:
            logging.debug(str(self.address) + ': Sent data with length - ' + binascii.b2a_hex(lengthstr) + ' ' + binascii.b2a_hex(data))
        totaldata = lengthstr + data
        totalsent = 0
        while totalsent < len(totaldata):
            sent = self.send(totaldata, False)
            if sent == 0:
                raise RuntimeError, 'socket connection broken'
            totalsent = totalsent + sent

    def recv(self, length, log=True):
        data = self.s.recv(length)
        if log:
            logging.debug(str(self.address) + ': Received data - ' + binascii.b2a_hex(data))
        return data

    def recvfrom(self, length, log=True):
        data, address = self.s.recvfrom(length)
        if log:
            logging.debug(str(address) + ': recvfrom Received data - ' + binascii.b2a_hex(data))
        return (data, address)

    def recv_all(self, length, log=True):
        data = ''
        while len(data) < length:
            chunk = self.recv(length - len(data), False)
            if chunk == '':
                raise RuntimeError, 'socket connection broken'
            data = data + chunk

        if log:
            logging.debug(str(self.address) + ': Received all data - ' + binascii.b2a_hex(data))
        return data

    def recv_withlen(self, log=True):
        lengthstr = self.recv(4, False)
        if len(lengthstr) != 4:
            print 'HEADER NOT LONG ENOUGH, SHOULD BE 4, IS ' + str(len(lengthstr))
        length = struct.unpack('>L', lengthstr)[0]
        data = self.recv_all(length, False)
        if log:
            logging.debug(str(self.address) + ': Received data with length  - ' + binascii.b2a_hex(lengthstr) + ' ' + binascii.b2a_hex(data))
        return data


def get_aes_key(encryptedstring, rsakey):
    decryptedstring = rsakey.decrypt(encryptedstring)
    if len(decryptedstring) != 127:
        raise NameError, 'RSAdecrypted string not the correct length!' + str(len(decryptedstring))
    firstpasschecksum = SHA.new(decryptedstring[20:127] + '\x00\x00\x00\x00').digest()
    secondpasskey = binaryxor(firstpasschecksum, decryptedstring[0:20])
    secondpasschecksum0 = SHA.new(secondpasskey + '\x00\x00\x00\x00').digest()
    secondpasschecksum1 = SHA.new(secondpasskey + '\x00\x00\x00\x01').digest()
    secondpasschecksum2 = SHA.new(secondpasskey + '\x00\x00\x00\x02').digest()
    secondpasschecksum3 = SHA.new(secondpasskey + '\x00\x00\x00\x03').digest()
    secondpasschecksum4 = SHA.new(secondpasskey + '\x00\x00\x00\x04').digest()
    secondpasschecksum5 = SHA.new(secondpasskey + '\x00\x00\x00\x05').digest()
    secondpasstotalchecksum = secondpasschecksum0 + secondpasschecksum1 + secondpasschecksum2 + secondpasschecksum3 + secondpasschecksum4 + secondpasschecksum5
    finishedkey = binaryxor(secondpasstotalchecksum[0:107], decryptedstring[20:127])
    controlchecksum = SHA.new('').digest()
    if finishedkey[0:20] != controlchecksum:
        raise NameError, "Control checksum didn't match!"
    return finishedkey[-16:]


def verify_message(key, message):
    key = key + '\x00' * 48
    xor_a = '6' * 64
    xor_b = '\\' * 64
    key_a = binaryxor(key, xor_a)
    key_b = binaryxor(key, xor_b)
    phrase_a = key_a + message[:-20]
    checksum_a = SHA.new(phrase_a).digest()
    phrase_b = key_b + checksum_a
    checksum_b = SHA.new(phrase_b).digest()
    if checksum_b == message[-20:]:
        return True
    else:
        return False


def sign_message(key, message):
    key = key + '\x00' * 48
    xor_a = '6' * 64
    xor_b = '\\' * 64
    key_a = binaryxor(key, xor_a)
    key_b = binaryxor(key, xor_b)
    phrase_a = key_a + message
    checksum_a = SHA.new(phrase_a).digest()
    phrase_b = key_b + checksum_a
    checksum_b = SHA.new(phrase_b).digest()
    return checksum_b


def rsa_sign_message(rsakey, message):
    digest = SHA.new(message).digest()
    fulldigest = '\x00\x01' + '\xff' * 90 + '\x000!0\t\x06\x05+\x0e\x03\x02\x1a\x05\x00\x04\x14' + digest
    signature = rsakey.encrypt(fulldigest, 0)[0]
    signature = signature.rjust(128, '\x00')
    return signature


def rsa_sign_message_1024(rsakey, message):
    digest = SHA.new(message).digest()
    fulldigest = '\x00\x01' + '\xff' * 218 + '\x000!0\t\x06\x05+\x0e\x03\x02\x1a\x05\x00\x04\x14' + digest
    signature = rsakey.encrypt(fulldigest, 0)[0]
    signature = signature.rjust(256, '\x00')
    return signature


def aes_decrypt(key, IV, message):
    decrypted = ''
    cryptobj = AES.new(key, AES.MODE_CBC, IV)
    i = 0
    while i < len(message):
        cipher = message[i:i + 16]
        decrypted = decrypted + cryptobj.decrypt(cipher)
        i = i + 16

    return decrypted


def aes_encrypt(key, IV, message):
    overflow = len(message) % 16
    message = message + (16 - overflow) * chr(16 - overflow)
    encrypted = ''
    cryptobj = AES.new(key, AES.MODE_CBC, IV)
    i = 0
    while i < len(message):
        cipher = message[i:i + 16]
        encrypted = encrypted + cryptobj.encrypt(cipher)
        i = i + 16

    return encrypted


def binaryxor(stringA, stringB):
    if len(stringA) != len(stringB):
        print "binaryxor: string lengths doesn't match!!"
        sys.exit()
    outString = ''
    for i in range(len(stringA)):
        valA = ord(stringA[i])
        valB = ord(stringB[i])
        valC = valA ^ valB
        outString = outString + chr(valC)

    return outString


class Application():
    """Empty class that acts as a placeholder"""
    pass


def chunk_aes_decrypt(key, chunk):
    cryptobj = AES.new(key, AES.MODE_ECB)
    output = ''
    lastblock = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    for i in range(0, len(chunk), 16):
        block = chunk[i:i + 16]
        block = block.ljust(16)
        key2 = cryptobj.encrypt(lastblock)
        output += binaryxor(block, key2)
        lastblock = block

    return output[:len(chunk)]


def get_apps_list(blob):
    subblob = blob['\x01\x00\x00\x00']
    apps = {}
    for appblob in subblob:
        app = Application()
        app.binid = appblob
        app.id = struct.unpack('<L', appblob)[0]
        app.version = struct.unpack('<L', subblob[appblob]['\x0b\x00\x00\x00'])[0]
        app.size = struct.unpack('<L', subblob[appblob]['\x05\x00\x00\x00'])[0]
        app.name = subblob[appblob]['\x02\x00\x00\x00']
        apps[app.id] = app

    return apps


class Fileserver_Client():

    def __init__(self, ipport):
        self.ipport = ipport
        self.connid = 0
        self.messageid = 0
        self.s = ImpSocket()
        self.s.connect(ipport)

    def setmode_storage(self):
        self.s.send('\x00\x00\x00\x07')
        self.s.recv(1)
        self.s.send_withlen('\x00\x00\x00\x00\x05')
        self.s.recv(16384)

    def open_storage(self, app, version):
        self.app = app
        self.version = version
        command = '\t' + struct.pack('>LLLL', self.connid, self.messageid, app, version)
        self.s.send_withlen(command)
        reply = self.s.recv(9)
        s_connid, s_messageid, s_dummy1 = struct.unpack('>LLb', reply)
        if s_dummy1 != 0:
            logging.error('Content server did not have app %i %i' % (app, version))
            return -1
        reply = self.s.recv(8)
        s_storageid, s_checksum = struct.unpack('>LL', reply)
        if s_messageid != self.messageid:
            logging.error("MessageID doesn't match up: %i %i" % (s_messageid, self.messageid))
            return
        logging.debug('Connection IDs: %s %s' % (hex(self.connid), hex(s_connid)))
        logging.debug('Dummy1: %s  Checksum %s' % (hex(s_dummy1), hex(s_checksum)))
        self.messageid = self.messageid + 1
        self.connid = self.connid + 1
        return s_storageid

    def open_storage_withlogin(self, app, version, loginpacket):
        self.app = app
        self.version = version
        command = '\n' + struct.pack('>LLLL', self.connid, self.messageid, app, version) + loginpacket
        self.s.send_withlen(command)
        reply = self.s.recv(9)
        s_connid, s_messageid, s_dummy1 = struct.unpack('>LLb', reply)
        if s_dummy1 != 0:
            logging.error('Content server did not have app %i %i' % (app, version))
            return -1
        reply = self.s.recv(8)
        s_storageid, s_checksum = struct.unpack('>LL', reply)
        if s_messageid != self.messageid:
            logging.error("MessageID doesn't match up: %i %i" % (s_messageid, self.messageid))
            return
        logging.debug('Connection IDs: %s %s' % (hex(self.connid), hex(s_connid)))
        logging.debug('Dummy1: %s  Checksum %s' % (hex(s_dummy1), hex(s_checksum)))
        self.messageid = self.messageid + 1
        self.connid = self.connid + 1
        return s_storageid

    def close_storage(self, storageid):
        command = '\x03' + struct.pack('>LL', storageid, self.messageid)
        self.s.send_withlen(command)
        reply = self.s.recv(9)
        s_storageid, s_messageid, dummy1 = struct.unpack('>LLb', reply)
        logging.debug('Dummy1: %s' % hex(dummy1))
        if s_storageid != storageid:
            logging.error("StorageID doesn't match up: %i %i" % (s_storageid, storageid))
            return
        if s_messageid != self.messageid:
            logging.error("MessageID doesn't match up: %i %i" % (s_messageid, self.messageid))
            return
        self.messageid = self.messageid + 1

    def disconnect(self):
        self.s.close()

    def get_metadata(self, storageid, commandbyte):
        command = commandbyte + struct.pack('>LL', storageid, self.messageid)
        self.s.send_withlen(command)
        reply = self.s.recv(13)
        s_storageid, s_messageid, dummy1, fullsize = struct.unpack('>LLbL', reply)
        if s_storageid != storageid:
            logging.error("StorageID doesn't match up: %i %i" % (s_storageid, storageid))
            return
        if s_messageid != self.messageid:
            logging.error("MessageID doesn't match up: %i %i" % (s_messageid, self.messageid))
            return
        logging.debug('Dummy1: %s' % hex(dummy1))
        data = ''
        while len(data) < fullsize:
            reply = self.s.recv(12)
            s_storageid, s_messageid, partsize = struct.unpack('>LLL', reply)
            if s_storageid != storageid:
                logging.error("StorageID doesn't match up: %i %i" % (s_storageid, storageid))
                return
            if s_messageid != self.messageid:
                logging.error("MessageID doesn't match up: %i %i" % (s_messageid, self.messageid))
                return
            package = self.s.recv_all(partsize, False)
            data = data + package

        self.messageid = self.messageid + 1
        return data

    def get_file(self, storageid, fileid, totalparts):
        chunks_per_call = 1
        file = []
        for i in range(0, totalparts, chunks_per_call):
            print '%i' % i,
            chunks = self.get_chunks(storageid, fileid, i, chunks_per_call)
            file.extend(chunks)

        return file

    def get_file_with_flag(self, storageid, fileid, totalparts):
        chunks_per_call = 1
        file = []
        filemode = 255
        for i in range(0, totalparts, chunks_per_call):
            print '%i' % i,
            newfilemode, chunks = self.get_chunks_with_flag(storageid, fileid, i, chunks_per_call)
            if filemode == 255:
                filemode = newfilemode
            if filemode != newfilemode:
                logging.error("Filemodes don't match up on the same file: %i %i" % (filemode, newfilemode))
            file.extend(chunks)

        return (filemode, file)

    def get_chunks(self, storageid, fileid, filepart, numparts):
        command = '\x07' + struct.pack('>LLLLLB', storageid, self.messageid, fileid, filepart, numparts, 0)
        self.s.send_withlen(command)
        reply = self.s.recv(17)
        s_storageid, s_messageid, dummy1, replyparts, filemode = struct.unpack('>LLbLL', reply)
        logging.debug('Dummy1: %s   Filemode: %s' % (hex(dummy1), hex(filemode)))
        if filemode != 1:
            foobar = open('filemodes.bin', 'ab')
            foobar.write(struct.pack('>LLLLb', self.app, self.version, fileid, filepart, filemode))
            foobar.close()
        if s_storageid != storageid:
            logging.error("StorageID doesn't match up: %i %i" % (s_storageid, storageid))
            return
        if s_messageid != self.messageid:
            logging.error("MessageID doesn't match up: %i %i" % (s_messageid, self.messageid))
            return
        chunks = []
        for i in range(replyparts):
            try:
                reply = self.s.recv(12)
            except socket.error:
                reply = struct.pack('>LLL', storageid, self.messageid, 0)

            s_storageid, s_messageid, fullsize = struct.unpack('>LLL', reply)
            if s_storageid != storageid:
                logging.error("StorageID doesn't match up: %i %i" % (s_storageid, storageid))
                return
            if s_messageid != self.messageid:
                logging.error("MessageID doesn't match up: %i %i" % (s_messageid, self.messageid))
                return
            data = ''
            while len(data) < fullsize:
                reply = self.s.recv(12)
                s_storageid, s_messageid, partsize = struct.unpack('>LLL', reply)
                if s_storageid != storageid:
                    logging.error("StorageID doesn't match up: %i %i" % (s_storageid, storageid))
                    return
                if s_messageid != self.messageid:
                    logging.error("MessageID doesn't match up: %i %i" % (s_messageid, self.messageid))
                    return
                package = self.s.recv_all(partsize, False)
                data = data + package

            chunks.append(data)

        self.messageid = self.messageid + 1
        return chunks

    def get_chunks_with_flag(self, storageid, fileid, filepart, numparts):
        command = '\x07' + struct.pack('>LLLLLB', storageid, self.messageid, fileid, filepart, numparts, 0)
        self.s.send_withlen(command)
        reply = self.s.recv(17)
        s_storageid, s_messageid, dummy1, replyparts, filemode = struct.unpack('>LLbLL', reply)
        logging.debug('Dummy1: %s   Filemode: %s' % (hex(dummy1), hex(filemode)))
        if filemode != 1:
            foobar = open('filemodes.bin', 'ab')
            foobar.write(struct.pack('>LLLLb', self.app, self.version, fileid, filepart, filemode))
            foobar.close()
        if s_storageid != storageid:
            logging.error("StorageID doesn't match up: %i %i" % (s_storageid, storageid))
            return
        if s_messageid != self.messageid:
            logging.error("MessageID doesn't match up: %i %i" % (s_messageid, self.messageid))
            return
        chunks = []
        for i in range(replyparts):
            try:
                reply = self.s.recv(12)
            except socket.error:
                reply = struct.pack('>LLL', storageid, self.messageid, 0)

            s_storageid, s_messageid, fullsize = struct.unpack('>LLL', reply)
            if s_storageid != storageid:
                logging.error("StorageID doesn't match up: %i %i" % (s_storageid, storageid))
                return
            if s_messageid != self.messageid:
                logging.error("MessageID doesn't match up: %i %i" % (s_messageid, self.messageid))
                return
            data = ''
            while len(data) < fullsize:
                reply = self.s.recv(12)
                s_storageid, s_messageid, partsize = struct.unpack('>LLL', reply)
                if s_storageid != storageid:
                    logging.error("StorageID doesn't match up: %i %i" % (s_storageid, storageid))
                    return
                if s_messageid != self.messageid:
                    logging.error("MessageID doesn't match up: %i %i" % (s_messageid, self.messageid))
                    return
                package = self.s.recv_all(partsize, False)
                data = data + package

            chunks.append(data)

        self.messageid = self.messageid + 1
        return (
         filemode, chunks)


def steamtime_to_unixtime(steamtime_bin):
    steamtime = struct.unpack('<Q', steamtime_bin)[0]
    unixtime = steamtime / 1000000 - 62135596800L
    return unixtime


def unixtime_to_steamtime(unixtime):
    steamtime = (unixtime + 62135596800L) * 1000000
    steamtime_bin = struct.pack('<Q', steamtime)
    return steamtime_bin


def sortfunc(x, y):
    if len(x) == 4 and x[2] == '\x00':
        if len(y) == 4 and y[2] == '\x00':
            numx = struct.unpack('<L', x)[0]
            numy = struct.unpack('<L', y)[0]
            return cmp(numx, numy)
        else:
            return -1

    else:
        if len(y) == 4 and y[2] == '\x00':
            return 1
        else:
            return cmp(x, y)


def formatstring(text):
    if len(text) == 4 and text[2] == '\x00':
        return "'\\x%02x\\x%02x\\x%02x\\x%02x'" % (ord(text[0]), ord(text[1]), ord(text[2]), ord(text[3]))
    else:
        return repr(text)


def blob_dump(blob, spacer=''):
    text = spacer + '{'
    spacer2 = spacer + '    '
    blobkeys = blob.keys()
    blobkeys.sort(sortfunc)
    first = True
    for key in blobkeys:
        data = blob[key]
        if type(data) == str:
            if first:
                text = text + '\n' + spacer2 + formatstring(key) + ': ' + formatstring(data)
                first = False
            else:
                text = text + ',\n' + spacer2 + formatstring(key) + ': ' + formatstring(data)
        elif first:
            text = text + '\n' + spacer2 + formatstring(key) + ':\n' + blob_dump(data, spacer2)
            first = False
        else:
            text = text + ',\n' + spacer2 + formatstring(key) + ':\n' + blob_dump(data, spacer2)

    text = text + '\n' + spacer + '}'
    return text