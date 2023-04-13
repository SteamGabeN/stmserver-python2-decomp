# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\steamemu\directoryserver.py
import threading, logging, struct, binascii, steam, globalvars

class directoryserver(threading.Thread):

    def __init__(self, (socket, address), config):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.config = config

    def run(self):
        log = logging.getLogger('dirsrv')
        clientid = str(self.address) + ': '
        log.info(clientid + 'Connected to Directory Server')
        msg = self.socket.recv(4)
        log.debug(binascii.b2a_hex(msg))
        if msg == '\x00\x00\x00\x01':
            self.socket.send('\x01')
            msg = self.socket.recv_withlen()
            command = msg[0]
            log.debug(binascii.b2a_hex(command))
            if command == '\x00':
                log.info(clientid + 'Sending out specific auth server: ' + binascii.b2a_hex(command))
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], self.config['auth_server_port']))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], self.config['auth_server_port']))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], self.config['auth_server_port']))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x03':
                log.info(clientid + 'Sending out list of config servers')
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], self.config['conf_server_port']))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], self.config['conf_server_port']))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], self.config['conf_server_port']))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x06':
                log.info(clientid + 'Sending out list of content list servers')
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], self.config['contlist_server_port']))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], self.config['contlist_server_port']))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], self.config['contlist_server_port']))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x0f':
                log.info(clientid + 'Requesting HL Master Server')
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], self.config['hlmaster_server_port']))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], self.config['hlmaster_server_port']))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], self.config['hlmaster_server_port']))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x12':
                log.info(clientid + 'Sending out list of account retrieval servers')
                reply = '\x00\x00'
            elif command == '\x14':
                log.info(clientid + 'Sending out list of CSER(?) servers')
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], 27013))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], 27013))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], 27013))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x18':
                log.info(clientid + 'Requesting Source Master Server')
                bin_ip = steam.encodeIP(('172.20.0.23', '27011'))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x1e':
                log.info(clientid + 'Requesting RDKF Master Server')
                bin_ip = steam.encodeIP(('172.20.0.23', '27012'))
                reply = struct.pack('>H', 1) + bin_ip
            else:
                log.info(clientid + 'Invalid/not implemented command: ' + binascii.b2a_hex(msg))
                reply = '\x00\x00'
            self.socket.send_withlen(reply)
        elif msg == '\x00\x00\x00\x02':
            self.socket.send('\x01')
            msg = self.socket.recv_withlen()
            command = msg[0]
            log.debug(binascii.b2a_hex(command))
            if command == '\x00' and len(msg) == 5:
                log.info(clientid + 'Sending out auth server for a specific username: ' + binascii.b2a_hex(command))
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], self.config['auth_server_port']))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], self.config['auth_server_port']))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], self.config['auth_server_port']))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x03':
                log.info(clientid + 'Sending out list of config servers')
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], self.config['conf_server_port']))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], self.config['conf_server_port']))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], self.config['conf_server_port']))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x06':
                log.info(clientid + 'Sending out list of content list servers')
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], self.config['contlist_server_port']))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], self.config['contlist_server_port']))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], self.config['contlist_server_port']))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x0b':
                log.info(clientid + 'Sending out auth server for a specific username: ' + binascii.b2a_hex(command))
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], self.config['auth_server_port']))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], self.config['auth_server_port']))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], self.config['auth_server_port']))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x0f':
                log.info(clientid + 'Requesting HL Master Server')
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], 27010))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], 27010))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], 27010))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x12':
                log.info(clientid + 'Sending out list of account retrieval servers')
                reply = '\x00\x00'
            elif command == '\x14':
                log.info(clientid + 'Sending out list of CSER servers')
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], 27013))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], 27013))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], 27013))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x18':
                log.info(clientid + 'Requesting Source Master Server')
                if self.config['public_ip'] != '0.0.0.0':
                    if clientid.startswith(globalvars.servernet):
                        bin_ip = steam.encodeIP((self.config['server_ip'], 27011))
                    else:
                        bin_ip = steam.encodeIP((self.config['public_ip'], 27011))
                else:
                    bin_ip = steam.encodeIP((self.config['server_ip'], 27011))
                reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x1c':
                if binascii.b2a_hex(msg) == '1c600f2d40':
                    if self.config['public_ip'] != '0.0.0.0':
                        if clientid.startswith(globalvars.servernet):
                            bin_ip = steam.encodeIP((self.config['server_ip'], self.config['file_server_port']))
                        else:
                            bin_ip = steam.encodeIP((self.config['public_ip'], self.config['file_server_port']))
                    else:
                        bin_ip = steam.encodeIP((self.config['server_ip'], self.config['file_server_port']))
                    reply = struct.pack('>H', 1) + bin_ip
            elif command == '\x1e':
                log.info(clientid + 'Requesting RDKF Master Server')
                bin_ip = steam.encodeIP(('172.20.0.23', '27012'))
                reply = struct.pack('>H', 1) + bin_ip
            else:
                log.info(clientid + 'Invalid/not implemented command: ' + binascii.b2a_hex(msg))
                reply = '\x00\x00'
            self.socket.send_withlen(reply)
        else:
            log.error(clientid + 'Invalid version message: ' + binascii.b2a_hex(command))
        self.socket.close()
        log.info(clientid + 'disconnected from Directory Server')