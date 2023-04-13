# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\steamemu\authserverv3.py
import threading, logging, struct, binascii, time, socket
from hashlib import sha1
import steam, config

class authserverv3(threading.Thread):

    def __init__(self, (socket, address)):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address

    def run(self):
        log = logging.getLogger('authsrv')
        clientid = str(self.address) + ': '
        log.info(clientid + 'Connected to Auth Server')
        command = self.socket.recv(13)
        if command[1:5] == '\x00\x00\x00\x04':
            self.socket.send('\x00' + socket.inet_aton(self.address[0]))
            command = self.socket.recv_withlen()
            if len(command) > 1 and len(command) < 256:
                users = {}
                with open('files/users/users.txt') as (f):
                    for line in f.readlines():
                        if line[-1:] == '\n':
                            line = line[:-1]
                        if line.find(':') != -1:
                            user, password = line.split(':')
                            users[user] = password

                usernamelen = struct.unpack('>H', command[1:3])[0]
                username = command[3:3 + usernamelen]
                if username not in users:
                    log.error('Invalid user!', username)
                self.socket.send('\x01#Eg\x89\xab\xcd\xef')
                command = self.socket.recv_withlen()
                key = sha1('\x01#Eg' + users[username] + '\x89\xab\xcd\xef').digest()[:16]
                IV = command[0:16]
                encrypted = command[20:36]
                log.info('Decoded message: ' + binascii.b2a_hex(crypto.aes_decrypt(key, IV, encrypted)))
                execdict = {}
                execfile('files/users/%s.py' % username, execdict)
                blob = steam.blob_serialize(execdict['user_registry'])
                innerkey = binascii.a2b_hex('10231230211281239191238542314233')
                innerIV = binascii.a2b_hex('12899c8312213a123321321321543344')
                blob_encrypted = struct.pack('<L', len(blob)) + innerIV + crypto.aes_encrypt(innerkey, innerIV, blob)
                blob_signature = crypto.sign_message(innerkey, blob_encrypted)
                blob_encrypted_len = 10 + len(blob_encrypted) + 20
                blob_encrypted = struct.pack('>L', blob_encrypted_len) + '\x01E' + struct.pack('<LL', blob_encrypted_len, 0) + blob_encrypted + blob_signature
                currtime = time.time()
                outerIV = binascii.a2b_hex('92183129534234231231312123123353')
                steamid = binascii.a2b_hex('00008080800000000000')
                servers = binascii.a2b_hex('451ca0939a69451ca0949a69')
                times = steamtime.from_unixtime(currtime) + steamtime.from_unixtime(currtime + 2419200)
                subheader = innerkey + steamid + servers + times
                subheader_encrypted = crypto.aes_encrypt(key, outerIV, subheader)
                subheader_encrypted = '\x00\x02' + outerIV + '\x006\x00@' + subheader_encrypted
                unknown_part = '\x01h' + '\xff' * 360
                ticket = subheader_encrypted + unknown_part + blob_encrypted
                ticket_signed = ticket + crypto.sign_message(innerkey, ticket)
                tgt_command = '\x00'
                stime = steamtime.from_unixtime(time.time())
                ticket_full = tgt_command + stime + '\x00\xd2Ik\x00\x00\x00\x00' + struct.pack('>L', len(ticket_signed)) + ticket_signed
                self.socket.send(ticket_full)
            elif len(command) >= 256:
                log.info(clientid + 'Ticket login')
                self.socket.send('\x01')
            elif len(command) == 1:
                if command == '\x1d':
                    log.info(clientid + 'command: Check username')
                elif command == '"':
                    log.info(clientid + 'command: Check email')
                elif command == '\x01':
                    log.info(clientid + 'command: Create user')
                elif command == '\x0e':
                    log.info(clientid + 'command: Lost password - username check')
                elif command == ' ':
                    log.info(clientid + 'command: Lost password - email check')
                elif command == '!':
                    log.info(clientid + 'command: Lost password - product check')
                BERstring = binascii.a2b_hex('30819d300d06092a864886f70d010101050003818b0030818702818100') + binascii.a2b_hex('bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059') + '\x02\x01\x11'
                signature = crypto.rsa_sign_message(crypto.main_key, BERstring)
                reply = struct.pack('>H', len(BERstring)) + BERstring + struct.pack('>H', len(signature)) + signature
                self.socket.send(reply)
                reply = self.socket.recv_withlen()
                RSAdata = reply[2:130]
                datalength = struct.unpack('>L', reply[130:134])[0]
                cryptedblob_signature = reply[134:136]
                cryptedblob_length = reply[136:140]
                cryptedblob_slack = reply[140:144]
                cryptedblob = reply[144:]
                key = crypto.get_aes_key(RSAdata, crypto.network_key)
                plaintext_length = struct.unpack('<L', cryptedblob[0:4])[0]
                IV = cryptedblob[4:20]
                ciphertext = cryptedblob[20:-20]
                plaintext = crypto.aes_decrypt(key, IV, ciphertext)
                plaintext = plaintext[0:plaintext_length]
                blob = Blob()
                blob.unserialize(plaintext)
                print blob.dump()
                self.socket.send('\x00')
            else:
                log.warning(clientid + 'Invalid command!')
        else:
            data = self.socket.recv(65535)
            log.warning(clientid + 'Invalid command!')
            log.warning(clientid + 'Extra data:', binascii.b2a_hex(data))
        self.socket.close()
        log.info(clientid + 'Disconnected from Auth Server')