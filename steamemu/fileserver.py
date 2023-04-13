# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\steamemu\fileserver.py
import threading, logging, struct, binascii, os.path, zlib, os, steam, config, globalvars
from Steam2.manifest import *
from Steam2.neuter import neuter
from Steam2.manifest2 import Manifest2
from Steam2.checksum2 import Checksum2
from Steam2.checksum3 import Checksum3
from gcf_to_storage import gcf2storage
from time import sleep

class fileserver(threading.Thread):

    def __init__(self, (socket, address), config):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.config = config

    def run(self):
        log = logging.getLogger('filesrv')
        clientid = str(self.address) + ': '
        log.info(clientid + 'Connected to File Server')
        msg = self.socket.recv(4)
        if len(msg) == 0:
            log.info(clientid + 'Got simple handshake. Closing connection.')
        elif msg == '\x00\x00\x00\x03':
            log.info(clientid + 'Package mode entered')
            self.socket.send('\x01')
            while True:
                msg = self.socket.recv_withlen()
                if not msg:
                    log.info(clientid + 'no message received')
                    break
                command = struct.unpack('>L', msg[:4])[0]
                if command == 2:
                    self.socket.send('\x00\x00\x00\x02')
                    break
                elif command == 3:
                    log.info(clientid + 'Exiting package mode')
                    break
                elif command == 0:
                    dummy1, filenamelength = struct.unpack('>LL', msg[4:12])
                    filename = msg[12:12 + filenamelength]
                    dummy2 = struct.unpack('>L', msg[12 + filenamelength:])[0]
                    if len(msg) != filenamelength + 16:
                        log.warning(clientid + 'There is extra data in the request')
                    log.info(clientid + filename)
                    if filename[-14:] == '_rsa_signature':
                        newfilename = filename[:-14]
                        if self.config['public_ip'] != '0.0.0.0':
                            try:
                                os.mkdir('files/cache/external')
                            except OSError as error:
                                log.debug(clientid + 'External pkg dir already exists')

                            try:
                                os.mkdir('files/cache/internal')
                            except OSError as error:
                                log.debug(clientid + 'Internal pkg dir already exists')

                            if clientid.startswith(globalvars.servernet):
                                if not os.path.isfile('files/cache/internal/' + newfilename):
                                    neuter(self.config['packagedir'] + newfilename, 'files/cache/internal/' + newfilename, self.config['server_ip'], self.config['dir_server_port'])
                                f = open('files/cache/internal/' + newfilename, 'rb')
                            else:
                                if not os.path.isfile('files/cache/external/' + newfilename):
                                    neuter(self.config['packagedir'] + newfilename, 'files/cache/external/' + newfilename, self.config['public_ip'], self.config['dir_server_port'])
                                f = open('files/cache/external/' + newfilename, 'rb')
                        else:
                            if not os.path.isfile('files/cache/' + newfilename):
                                neuter(self.config['packagedir'] + newfilename, 'files/cache/' + newfilename, self.config['server_ip'], self.config['dir_server_port'])
                            f = open('files/cache/' + newfilename, 'rb')
                        file = f.read()
                        f.close()
                        signature = steam.rsa_sign_message(steam.network_key_sign, file)
                        reply = struct.pack('>LL', len(signature), len(signature)) + signature
                        self.socket.send(reply)
                    else:
                        if self.config['public_ip'] != '0.0.0.0':
                            try:
                                os.mkdir('files/cache/external')
                            except OSError as error:
                                log.debug(clientid + 'External pkg dir already exists')

                            try:
                                os.mkdir('files/cache/internal')
                            except OSError as error:
                                log.debug(clientid + 'Internal pkg dir already exists')

                            if clientid.startswith(globalvars.servernet):
                                if not os.path.isfile('files/cache/internal/' + filename):
                                    neuter(self.config['packagedir'] + filename, 'files/cache/internal/' + filename, self.config['server_ip'], self.config['dir_server_port'])
                                f = open('files/cache/internal/' + filename, 'rb')
                            else:
                                if not os.path.isfile('files/cache/external/' + filename):
                                    neuter(self.config['packagedir'] + filename, 'files/cache/external/' + filename, self.config['public_ip'], self.config['dir_server_port'])
                                f = open('files/cache/external/' + filename, 'rb')
                        else:
                            if not os.path.isfile('files/cache/' + filename):
                                neuter(self.config['packagedir'] + filename, 'files/cache/' + filename, self.config['server_ip'], self.config['dir_server_port'])
                            f = open('files/cache/' + filename, 'rb')
                        file = f.read()
                        f.close()
                        reply = struct.pack('>LL', len(file), len(file))
                        self.socket.send(reply)
                        self.socket.send(file, False)
                else:
                    log.warning(clientid + 'invalid Command')

        elif msg == '\x00\x00\x00\x07':
            log.info(clientid + 'Storage mode entered')
            storagesopen = 0
            storages = {}
            self.socket.send('\x01')
            while True:
                command = self.socket.recv_withlen()
                if command[0] == '\x00':
                    log.info('Banner message: ' + binascii.b2a_hex(command))
                    if len(command) > 1:
                        url = 'http://' + self.config['http_ip'] + self.config['http_port'] + self.config['banner_url']
                        reply = struct.pack('>cH', '\x01', len(url)) + url
                        self.socket.send(reply)
                    else:
                        self.socket.send('')
                elif command[0] == '\t' or command[0] == '\n':
                    if command[0] == '\n':
                        log.info('Login packet used')
                    connid, messageid, app, version = struct.unpack('>xLLLL', command[0:17])
                    log.info(clientid + 'Opening application %d %d' % (app, version))
                    connid = pow(2, 31) + connid
                    try:
                        s = steam.Storage(app, self.config['storagedir'], version)
                    except Exception:
                        log.error('Application not installed! %d %d' % (app, version))
                        reply = struct.pack('>LLc', connid, messageid, '\x01')
                        self.socket.send(reply)
                        break

                    storageid = storagesopen
                    storagesopen = storagesopen + 1
                    storages[storageid] = s
                    storages[storageid].app = app
                    storages[storageid].version = version
                    if str(app) == '3' or str(app) == '7':
                        if not os.path.isfile('files/cache/' + str(app) + '_' + str(version) + '/' + str(app) + '_' + str(version) + '.manifest'):
                            if os.path.isfile('files/convert/' + str(app) + '_' + str(version) + '.gcf'):
                                log.info('Fixing files in app ' + str(app) + ' version ' + str(version))
                                g = open('files/convert/' + str(app) + '_' + str(version) + '.gcf', 'rb')
                                file = g.read()
                                g.close()
                                for search, replace, info in globalvars.replacestrings:
                                    fulllength = len(search)
                                    newlength = len(replace)
                                    missinglength = fulllength - newlength
                                    if missinglength < 0:
                                        print 'WARNING: Replacement text ' + replace + ' is too long! Not replaced!'
                                    elif missinglength == 0:
                                        file = file.replace(search, replace)
                                        print 'Replaced', info
                                    else:
                                        file = file.replace(search, replace + '\x00' * missinglength)
                                        print 'Replaced', info

                                h = open('files/temp/' + str(app) + '_' + str(version) + '.neutered.gcf', 'wb')
                                h.write(file)
                                h.close()
                                gcf2storage('files/temp/' + str(app) + '_' + str(version) + '.neutered.gcf')
                                sleep(1)
                                os.remove('files/temp/' + str(app) + '_' + str(version) + '.neutered.gcf')
                    if os.path.isfile('files/cache/' + str(app) + '_' + str(version) + '/' + str(app) + '_' + str(version) + '.manifest'):
                        f = open('files/cache/' + str(app) + '_' + str(version) + '/' + str(app) + '_' + str(version) + '.manifest', 'rb')
                        log.info(clientid + str(app) + '_' + str(version) + ' is a cached depot')
                    elif os.path.isfile(self.config['v2manifestdir'] + str(app) + '_' + str(version) + '.manifest'):
                        f = open(self.config['v2manifestdir'] + str(app) + '_' + str(version) + '.manifest', 'rb')
                        log.info(clientid + str(app) + '_' + str(version) + ' is a v0.2 depot')
                    else:
                        f = open(self.config['manifestdir'] + str(app) + '_' + str(version) + '.manifest', 'rb')
                        log.info(clientid + str(app) + '_' + str(version) + ' is a v0.3 depot')
                    manifest = f.read()
                    f.close()
                    globalvars.converting = '0'
                    fingerprint = manifest[48:52]
                    oldchecksum = manifest[52:56]
                    manifest = manifest[:48] + '\x00\x00\x00\x00\x00\x00\x00\x00' + manifest[56:]
                    checksum = struct.pack('<i', zlib.adler32(manifest, 0))
                    manifest = manifest[:48] + fingerprint + checksum + manifest[56:]
                    log.debug('Checksum fixed from ' + binascii.b2a_hex(oldchecksum) + ' to ' + binascii.b2a_hex(checksum))
                    storages[storageid].manifest = manifest
                    checksum = struct.unpack('<L', manifest[48:52])[0]
                    reply = struct.pack('>LLcLL', connid, messageid, '\x00', storageid, checksum)
                    self.socket.send(reply)
                elif command[0] == '\x01':
                    self.socket.send('')
                    break
                elif command[0] == '\x03':
                    storageid, messageid = struct.unpack('>xLL', command)
                    del storages[storageid]
                    reply = struct.pack('>LLc', storageid, messageid, '\x00')
                    log.info(clientid + 'Closing down storage %d' % storageid)
                    self.socket.send(reply)
                elif command[0] == '\x04':
                    log.info(clientid + 'Sending manifest')
                    storageid, messageid = struct.unpack('>xLL', command)
                    manifest = storages[storageid].manifest
                    reply = struct.pack('>LLcL', storageid, messageid, '\x00', len(manifest))
                    self.socket.send(reply)
                    reply = struct.pack('>LLL', storageid, messageid, len(manifest))
                    self.socket.send(reply + manifest, False)
                elif command[0] == '\x05':
                    log.info(clientid + 'Sending app update information')
                    storageid, messageid, oldversion = struct.unpack('>xLLL', command)
                    appid = storages[storageid].app
                    version = storages[storageid].version
                    log.info('Old GCF version: ' + str(appid) + '_' + str(oldversion))
                    log.info('New GCF version: ' + str(appid) + '_' + str(version))
                    manifestNew = Manifest2(appid, version)
                    manifestOld = Manifest2(appid, oldversion)
                    if os.path.isfile(self.config['v2manifestdir'] + str(appid) + '_' + str(version) + '.manifest'):
                        checksumNew = Checksum3(appid)
                    else:
                        checksumNew = Checksum2(appid, version)
                    if os.path.isfile(self.config['v2manifestdir'] + str(appid) + '_' + str(oldversion) + '.manifest'):
                        checksumOld = Checksum3(appid)
                    else:
                        checksumOld = Checksum2(appid, version)
                    filesOld = {}
                    filesNew = {}
                    for n in manifestOld.nodes.values():
                        if n.fileId != 4294967295L:
                            n.checksum = checksumOld.getchecksums_raw(n.fileId)
                            filesOld[n.fullFilename] = n

                    for n in manifestNew.nodes.values():
                        if n.fileId != 4294967295L:
                            n.checksum = checksumNew.getchecksums_raw(n.fileId)
                            filesNew[n.fullFilename] = n

                    del manifestNew
                    del manifestOld
                    changedFiles = []
                    for filename in filesOld:
                        if filename in filesNew and filesOld[filename].checksum != filesNew[filename].checksum:
                            changedFiles.append(filesOld[filename].fileId)
                            log.debug('Changed file: ' + str(filename) + ' : ' + str(filesOld[filename].fileId))
                        if filename not in filesNew:
                            changedFiles.append(filesOld[filename].fileId)
                            log.debug('Deleted file: ' + str(filename) + ' : ' + str(filesOld[filename].fileId))

                    for x in range(len(changedFiles)):
                        log.debug(changedFiles[x])

                    count = len(changedFiles)
                    log.info('Number of changed files: ' + str(count))
                    if count == 0:
                        reply = struct.pack('>LLcL', storageid, messageid, '\x01', 0)
                        self.socket.send(reply)
                    else:
                        reply = struct.pack('>LLcL', storageid, messageid, '\x02', count)
                        self.socket.send(reply)
                        changedFilesTmp = []
                        for fileid in changedFiles:
                            changedFilesTmp.append(struct.pack('<L', fileid))

                        updatefiles = ('').join(changedFilesTmp)
                        reply = struct.pack('>LL', storageid, messageid)
                        self.socket.send(reply)
                        self.socket.send_withlen(updatefiles)
                elif command[0] == '\x06':
                    log.info(clientid + 'Sending checksums')
                    storageid, messageid = struct.unpack('>xLL', command)
                    if os.path.isfile('files/cache/' + str(storages[storageid].app) + '_' + str(storages[storageid].version) + '/' + str(storages[storageid].app) + '_' + str(storages[storageid].version) + '.manifest'):
                        filename = 'files/cache/' + str(storages[storageid].app) + '_' + str(storages[storageid].version) + '/' + str(storages[storageid].app) + '.checksums'
                    elif os.path.isfile(self.config['v2manifestdir'] + str(storages[storageid].app) + '_' + str(storages[storageid].version) + '.manifest'):
                        filename = self.config['v2storagedir'] + str(storages[storageid].app) + '.checksums'
                    else:
                        filename = self.config['storagedir'] + str(storages[storageid].app) + '.checksums'
                    f = open(filename, 'rb')
                    file = f.read()
                    f.close()
                    file = file[0:-128]
                    signature = steam.rsa_sign_message(steam.network_key_sign, file)
                    file = file + signature
                    reply = struct.pack('>LLcL', storageid, messageid, '\x00', len(file))
                    self.socket.send(reply)
                    reply = struct.pack('>LLL', storageid, messageid, len(file))
                    self.socket.send(reply + file, False)
                elif command[0] == '\x07':
                    storageid, messageid, fileid, filepart, numparts, dummy2 = struct.unpack('>xLLLLLB', command)
                    chunks, filemode = storages[storageid].readchunks(fileid, filepart, numparts)
                    reply = struct.pack('>LLcLL', storageid, messageid, '\x00', len(chunks), filemode)
                    self.socket.send(reply)
                    for chunk in chunks:
                        reply = struct.pack('>LLL', storageid, messageid, len(chunk))
                        self.socket.send(reply)
                        reply = struct.pack('>LLL', storageid, messageid, len(chunk))
                        self.socket.send(reply)
                        self.socket.send(chunk, False)

                elif command[0] == '\x08':
                    log.warning('08 - Invalid Command!')
                    self.socket.send('\x01')
                elif command[0] == '\t':
                    log.warning('09 - Invalid Command!')
                    self.socket.send('\x01')
                elif command[0] == '\x10':
                    log.warning('10 - Invalid Command!')
                    self.socket.send('\x01')
                else:
                    log.warning(binascii.b2a_hex(command[0]) + ' - Invalid Command!')
                    self.socket.send('\x01')
                    break

        elif msg == '\x03\x00\x00\x00':
            log.info(clientid + 'Unknown mode entered')
            self.socket.send('\x00')
        else:
            log.warning('Invalid Command: ' + binascii.b2a_hex(msg))
        self.socket.close()
        log.info(clientid + 'Disconnected from File Server')