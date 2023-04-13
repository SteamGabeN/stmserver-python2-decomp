# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\steamemu\configserver.py
import threading, logging, struct, binascii, socket, zlib, os, shutil
from Crypto.Hash import SHA
import steam, config, globalvars

class configserver(threading.Thread):

    def __init__(self, (socket, address), config):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.config = config

    def run(self):
        log = logging.getLogger('confsrv')
        clientid = str(self.address) + ': '
        log.info(clientid + 'Connected to Config Server')
        command = self.socket.recv(4)
        if command == '\x00\x00\x00\x03' or command == '\x00\x00\x00\x02':
            self.socket.send('\x01' + socket.inet_aton(self.address[0]))
            command = self.socket.recv_withlen()
            if len(command) == 1:
                if command == '\x01':
                    log.info(clientid + 'sending first blob')
                    if os.path.isfile('files/1stcdr.py'):
                        execdict = {}
                        execfile('files/1stcdr.py', execdict)
                        blob = steam.blob_serialize(execdict['blob'])
                    else:
                        f = open('files/firstblob.bin', 'rb')
                        blob = f.read()
                        f.close()
                    self.socket.send_withlen(blob)
                elif command == '\x04':
                    log.info(clientid + 'sending network key')
                    BERstring = binascii.a2b_hex('30819d300d06092a864886f70d010101050003818b0030818702818100') + binascii.a2b_hex('bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059') + '\x02\x01\x11'
                    signature = steam.rsa_sign_message_1024(steam.main_key_sign, BERstring)
                    reply = struct.pack('>H', len(BERstring)) + BERstring + struct.pack('>H', len(signature)) + signature
                    self.socket.send(reply)
                elif command == '\x05':
                    log.info(clientid + 'confserver command 5, unknown, sending zero reply')
                    self.socket.send('\x00')
                elif command == '\x06':
                    log.info(clientid + 'confserver command 6, unknown, sending zero reply')
                    self.socket.send('\x00')
                elif command == '\x07':
                    log.info(clientid + 'confserver command 7, unknown, sending recorded reply')
                    self.socket.send(binascii.a2b_hex('0001312d000000012c'))
                elif command == '\x08':
                    log.info(clientid + 'confserver command 8, unknown, sending zero reply')
                    self.socket.send('\x00')
                else:
                    log.warning(clientid + 'Invalid command: ' + binascii.b2a_hex(command))
                    self.socket.send('\x00')
            elif command[0] == '\x02' or command[0] == '\t':
                if command[0] == '\t':
                    self.socket.send(binascii.a2b_hex('00000001312d000000012c'))
                if os.path.isfile('files/cache/secondblob.bin'):
                    f = open('files/cache/secondblob.bin', 'rb')
                    blob = f.read()
                    f.close()
                else:
                    if os.path.isfile('files/2ndcdr.py'):
                        if not os.path.isfile('files/2ndcdr.orig'):
                            shutil.copy2('files/2ndcdr.py', 'files/2ndcdr.orig')
                        g = open('files/2ndcdr.py', 'r')
                        file = g.read()
                        g.close()
                        for search, replace, info in globalvars.replacestringsCDR:
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0:
                                print 'WARNING: Replacement text ' + replace + ' is too long! Not replaced!'
                            else:
                                fileold = file
                                file = file.replace(search, replace)
                                if search in fileold and replace in file:
                                    print 'Replaced ' + info + ' ' + search + ' with ' + replace

                        h = open('files/2ndcdr.py', 'w')
                        h.write(file)
                        h.close()
                        execdict = {}
                        execfile('files/2ndcdr.py', execdict)
                        blob = steam.blob_serialize(execdict['blob'])
                        if blob[0:2] == '\x01C':
                            blob = zlib.decompress(blob[20:])
                        start_search = 0
                        while True:
                            found = blob.find('0\x81\x9d0\r\x06\t*', start_search)
                            if found < 0:
                                break
                            BERstring = binascii.a2b_hex('30819d300d06092a864886f70d010101050003818b0030818702818100') + binascii.a2b_hex('bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059') + '\x02\x01\x11'
                            foundstring = blob[found:found + 160]
                            blob = blob.replace(foundstring, BERstring)
                            start_search = found + 160

                        compressed_blob = zlib.compress(blob, 9)
                        blob = '\x01C' + struct.pack('<QQH', len(compressed_blob) + 20, len(blob), 9) + compressed_blob
                        cache_option = self.config['use_cached_blob']
                        if cache_option == 'true':
                            f = open('files/cache/secondblob.bin', 'wb')
                            f.write(blob)
                            f.close()
                    else:
                        if not os.path.isfile('files/secondblob.orig'):
                            shutil.copy2('files/secondblob.bin', 'files/secondblob.orig')
                        f = open('files/secondblob.bin', 'rb')
                        blob = f.read()
                        f.close()
                        if blob[0:2] == '\x01C':
                            blob = zlib.decompress(blob[20:])
                        blob2 = steam.blob_unserialize(blob)
                        blob3 = steam.blob_dump(blob2)
                        file = 'blob = ' + blob3
                        for search, replace, info in globalvars.replacestringsCDR:
                            print 'Fixing CDR'
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0:
                                print 'WARNING: Replacement text ' + replace + ' is too long! Not replaced!'
                            else:
                                file = file.replace(search, replace)
                                print 'Replaced ' + info + ' ' + search + ' with ' + replace

                    execdict = {}
                    exec file in execdict
                    blob = steam.blob_serialize(execdict['blob'])
                    h = open('files/secondblob.bin', 'wb')
                    h.write(blob)
                    h.close()
                    g = open('files/secondblob.bin', 'rb')
                    blob = g.read()
                    g.close()
                    if blob[0:2] == '\x01C':
                        blob = zlib.decompress(blob[20:])
                    start_search = 0
                    while True:
                        found = blob.find('0\x81\x9d0\r\x06\t*', start_search)
                        if found < 0:
                            break
                        BERstring = binascii.a2b_hex('30819d300d06092a864886f70d010101050003818b0030818702818100') + binascii.a2b_hex('bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059') + '\x02\x01\x11'
                        foundstring = blob[found:found + 160]
                        blob = blob.replace(foundstring, BERstring)
                        start_search = found + 160

                compressed_blob = zlib.compress(blob, 9)
                blob = '\x01C' + struct.pack('<QQH', len(compressed_blob) + 20, len(blob), 9) + compressed_blob
                cache_option = self.config['use_cached_blob']
                if cache_option == 'true':
                    f = open('files/cache/secondblob.bin', 'wb')
                    f.write(blob)
                    f.close()
                checksum = SHA.new(blob).digest()
                if checksum == command[1:]:
                    log.info(clientid + 'Client has matching checksum for secondblob')
                    log.debug(clientid + 'We validate it: ' + binascii.b2a_hex(command))
                    self.socket.send('\x00\x00\x00\x00')
                else:
                    log.info(clientid + "Client didn't match our checksum for secondblob")
                    log.debug(clientid + 'Sending new blob: ' + binascii.b2a_hex(command))
                    self.socket.send_withlen(blob, False)
            else:
                log.info(clientid + 'Invalid message: ' + binascii.b2a_hex(command))
        else:
            log.info(clientid + 'Invalid head message: ' + binascii.b2a_hex(command))
        self.socket.close()
        log.info(clientid + 'disconnected from Config Server')