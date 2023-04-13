# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\emulator.py
import sys, binascii, ConfigParser, threading, logging, socket, time, os, struct, steam, dirs, steamemu.logger, globalvars
from steamemu.converter import convertgcf
from steamemu.config import read_config
from steamemu.directoryserver import directoryserver
from steamemu.configserver import configserver
from steamemu.contentlistserver import contentlistserver
from steamemu.fileserver import fileserver
from steamemu.authserver import authserver
from steamemu.authserverv3 import authserverv3
from steamemu.udpserver import udpserver
from steamemu.masterhl import masterhl
from steamemu.masterhl2 import masterhl2
from steamemu.friends import friends
from steamemu.twosevenzeroonefour import twosevenzeroonefour
from Steam2.package import Package
from Steam2.neuter import neuter_file
print 'Steam 2004-2010 Server Emulator v0.55'
print '====================================='
print
config = read_config()
print '**************************'
print 'Server IP: ' + config['server_ip']
if config['public_ip'] != '0.0.0.0':
    print 'Public IP: ' + config['public_ip']
print '**************************'
print
log = logging.getLogger('emulator')
log.info('...Starting Steam Server...\n')
if config['server_ip'].startswith('10.'):
    globalvars.servernet = "('10."
elif config['server_ip'].startswith('172.16.'):
    globalvars.servernet = "('172.16."
elif config['server_ip'].startswith('172.17.'):
    globalvars.servernet = "('172.17."
elif config['server_ip'].startswith('172.18.'):
    globalvars.servernet = "('172.18."
elif config['server_ip'].startswith('172.19.'):
    globalvars.servernet = "('172.19."
elif config['server_ip'].startswith('172.20.'):
    globalvars.servernet = "('172.20."
elif config['server_ip'].startswith('172.21.'):
    globalvars.servernet = "('172.21."
elif config['server_ip'].startswith('172.22.'):
    globalvars.servernet = "('172.22."
elif config['server_ip'].startswith('172.23.'):
    globalvars.servernet = "('172.23."
elif config['server_ip'].startswith('172.24.'):
    globalvars.servernet = "('172.24."
elif config['server_ip'].startswith('172.25.'):
    globalvars.servernet = "('172.25."
elif config['server_ip'].startswith('172.26.'):
    globalvars.servernet = "('172.26."
elif config['server_ip'].startswith('172.27.'):
    globalvars.servernet = "('172.27."
elif config['server_ip'].startswith('172.28.'):
    globalvars.servernet = "('172.28."
elif config['server_ip'].startswith('172.29.'):
    globalvars.servernet = "('172.29."
elif config['server_ip'].startswith('172.30.'):
    globalvars.servernet = "('172.30."
elif config['server_ip'].startswith('172.31.'):
    globalvars.servernet = "('172.31."
elif config['server_ip'].startswith('192.168.'):
    globalvars.servernet = "('192.168."

class listener(threading.Thread):

    def __init__(self, port, serverobject, config):
        self.port = int(port)
        self.serverobject = serverobject
        self.config = config.copy()
        self.config['port'] = port
        threading.Thread.__init__(self)

    def run(self):
        serversocket = steam.ImpSocket()
        serversocket.bind((config['server_ip'], self.port))
        serversocket.listen(5)
        while True:
            clientsocket, address = serversocket.accept()
            self.serverobject((clientsocket, address), self.config).start()


class udplistener(threading.Thread):

    def __init__(self, port, serverobject, config):
        self.port = int(port)
        self.serverobject = serverobject
        self.config = config.copy()
        self.config['port'] = port
        threading.Thread.__init__(self)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serversocket = steam.ImpSocket(sock)
        serversocket.bind((config['server_ip'], self.port))
        while True:
            globalvars.data, globalvars.addr = serversocket.recvfrom(1280)
            if self.port == 27010:
                log = logging.getLogger('hl1mstr')
                clientid = str(globalvars.addr) + ': '
                log.info(clientid + 'Connected to HL Master Server')
                log.debug(clientid + 'Received message: %s, from %s' % (globalvars.data, globalvars.addr))
                if globalvars.data.startswith('1'):
                    i = 0
                    header = bytearray()
                    header += '\xff\xff\xff\xfff\n'
                    while i < 1000:
                        if not isinstance(globalvars.hl1serverlist[i], int):
                            print globalvars.hl1serverlist[i]
                            trueip = globalvars.hl1serverlist[i][0].split('.')
                            trueip_int = map(int, trueip)
                            header += struct.pack('>BBBB', trueip_int[0], trueip_int[1], trueip_int[2], trueip_int[3])
                            trueport_int_temp = int(globalvars.hl1serverlist[i][24])
                            if not len(str(trueport_int_temp)) == 5:
                                trueport_int = 27015
                            else:
                                trueport_int = trueport_int_temp
                            print str(trueport_int)
                            header += struct.pack('>H', trueport_int)
                        i += 1

                    nullip = struct.pack('>BBBB', 0, 0, 0, 0)
                    nullport = struct.pack('>H', 0)
                    serversocket.sendto(header + nullip + nullport, globalvars.addr)
                elif globalvars.data.startswith('q'):
                    header = '\xff\xff\xff\xffs\n'
                    challenge = struct.pack('I', globalvars.hl1challengenum + 1)
                    serversocket.sendto(header + challenge, globalvars.addr)
                    globalvars.hl1challengenum += 1
                elif globalvars.data.startswith('M'):
                    header = '\xff\xff\xff\xffN\n'
                    challenge = struct.pack('I', globalvars.hl1challengenum + 1)
                    serversocket.sendto(header + challenge, globalvars.addr)
                    globalvars.hl1challengenum += 1
                elif globalvars.data.startswith('0'):
                    serverdata1 = globalvars.data.split('\n')
                    serverdata2 = serverdata1[1]
                    ipstr = str(globalvars.addr)
                    ipstr1 = ipstr.split("'")
                    serverdata3 = ipstr1[1] + serverdata2
                    tempserverlist = serverdata3.split('\\')
                    globalvars.hl1serverlist[int(tempserverlist[4])] = tempserverlist
                    print 'This Challenge: %s' % tempserverlist[4]
                    print 'Current Challenge: %s' % globalvars.hl1challengenum
                elif globalvars.data.startswith('b'):
                    ipstr = str(globalvars.addr)
                    ipstr1 = ipstr.split("'")
                    ipactual = ipstr1[1]
                    portstr = ipstr1[2]
                    portstr1 = portstr.split(' ')
                    portstr2 = portstr1[1].split(')')
                    portactual_temp = portstr2[0]
                    if not str(len(portactual_temp)) == 5:
                        portactual = '27015'
                    else:
                        portactual = str(portactual_temp)
                    i = 0
                    running = 0
                    while i < 1000:
                        if not isinstance(globalvars.hl1serverlist[i], int):
                            running += 1
                            if globalvars.hl1serverlist[i][0] == ipactual and (str(globalvars.hl1serverlist[i][24]) == portactual or '27015' == portactual):
                                globalvars.hl1serverlist.pop(i)
                                print 'Removed game server: %s:%s' % (ipactual, portactual)
                                running -= 1
                        i += 1

                    print 'Running servers: %s' % str(running)
                else:
                    print 'UNKNOWN MASTER SERVER COMMAND'
            elif self.port == 27011:
                log = logging.getLogger('hl2mstr')
                clientid = str(globalvars.addr) + ': '
                log.info(clientid + 'Connected to HL2 Master Server')
                log.debug(clientid + 'Received message: %s, from %s' % (globalvars.data, globalvars.addr))
                if globalvars.data.startswith('1'):
                    i = 0
                    header = bytearray()
                    header += '\xff\xff\xff\xfff\n'
                    while i < 1000:
                        if not isinstance(globalvars.hl2serverlist[i], int):
                            print globalvars.hl2serverlist[i]
                            trueip = globalvars.hl2serverlist[i][0].split('.')
                            trueip_int = map(int, trueip)
                            header += struct.pack('>BBBB', trueip_int[0], trueip_int[1], trueip_int[2], trueip_int[3])
                            try:
                                trueport_int_temp = int(globalvars.hl2serverlist[i][24])
                            except:
                                trueport_int_temp = 1

                            if not len(str(trueport_int_temp)) == 5:
                                trueport_int = 27015
                            else:
                                trueport_int = trueport_int_temp
                            print str(trueport_int)
                            header += struct.pack('>H', trueport_int)
                        i += 1

                    nullip = struct.pack('>BBBB', 0, 0, 0, 0)
                    nullport = struct.pack('>H', 0)
                    serversocket.sendto(header + nullip + nullport, globalvars.addr)
                elif globalvars.data.startswith('q'):
                    header = '\xff\xff\xff\xffs\n'
                    challenge = struct.pack('I', globalvars.hl2challengenum + 1)
                    serversocket.sendto(header + challenge, globalvars.addr)
                    globalvars.hl2challengenum += 1
                elif globalvars.data.startswith('0'):
                    serverdata1 = globalvars.data.split('\n')
                    serverdata2 = serverdata1[1]
                    ipstr = str(globalvars.addr)
                    ipstr1 = ipstr.split("'")
                    serverdata3 = ipstr1[1] + serverdata2
                    tempserverlist = serverdata3.split('\\')
                    globalvars.hl2serverlist[int(tempserverlist[4])] = tempserverlist
                    print 'This Challenge: %s' % tempserverlist[4]
                    print 'Current Challenge: %s' % globalvars.hl2challengenum
                elif globalvars.data.startswith('b'):
                    ipstr = str(globalvars.addr)
                    ipstr1 = ipstr.split("'")
                    ipactual = ipstr1[1]
                    portstr = ipstr1[2]
                    portstr1 = portstr.split(' ')
                    portstr2 = portstr1[1].split(')')
                    portactual_temp = portstr2[0]
                    if not str(len(portactual_temp)) == 5:
                        portactual = '27015'
                    else:
                        portactual = str(portactual_temp)
                    i = 0
                    running = 0
                    while i < 1000:
                        if not isinstance(globalvars.hl2serverlist[i], int):
                            running += 1
                            if globalvars.hl2serverlist[i][0] == ipactual and (str(globalvars.hl2serverlist[i][24]) == portactual or '27015' == portactual):
                                globalvars.hl2serverlist.pop(i)
                                print 'Removed game server: %s:%s' % (ipactual, portactual)
                                running -= 1
                        i += 1

                    print 'Running servers: %s' % str(running)
                else:
                    print 'UNKNOWN MASTER SERVER COMMAND'
            elif self.port == 27013:
                log = logging.getLogger('csersrv')
                clientid = str(globalvars.addr) + ': '
                log.info(clientid + 'Connected to CSER Server')
                log.debug(clientid + 'Received message: %s, from %s' % (globalvars.data, globalvars.addr))
                ipstr = str(globalvars.addr)
                ipstr1 = ipstr.split("'")
                ipactual = ipstr1[1]
                if globalvars.data.startswith('e'):
                    message = binascii.b2a_hex(globalvars.data)
                    keylist = list(xrange(7))
                    vallist = list(xrange(7))
                    keylist[0] = 'SuccessCount'
                    keylist[1] = 'UnknownFailureCount'
                    keylist[2] = 'ShutdownFailureCount'
                    keylist[3] = 'UptimeCleanCounter'
                    keylist[4] = 'UptimeCleanTotal'
                    keylist[5] = 'UptimeFailureCounter'
                    keylist[6] = 'UptimeFailureTotal'
                    try:
                        os.mkdir('clientstats')
                    except OSError as error:
                        log.debug('Client stats dir already exists')

                    if message.startswith('650a01537465616d2e657865'):
                        vallist[0] = str(int(message[24:26], base=16))
                        vallist[1] = str(int(message[26:28], base=16))
                        vallist[2] = str(int(message[28:30], base=16))
                        vallist[3] = str(int(message[30:32], base=16))
                        vallist[4] = str(int(message[32:34], base=16))
                        vallist[5] = str(int(message[34:36], base=16))
                        vallist[6] = str(int(message[36:38], base=16))
                        f = open('clientstats\\' + str(ipactual) + '.steamexe.csv', 'w')
                        f.write(str(binascii.a2b_hex(message[6:24])))
                        f.write('\n')
                        f.write(keylist[0] + ',' + keylist[1] + ',' + keylist[2] + ',' + keylist[3] + ',' + keylist[4] + ',' + keylist[5] + ',' + keylist[6])
                        f.write('\n')
                        f.write(vallist[0] + ',' + vallist[1] + ',' + vallist[2] + ',' + vallist[3] + ',' + vallist[4] + ',' + vallist[5] + ',' + vallist[6])
                        f.close()
                        log.info(clientid + 'Received client stats')
                elif globalvars.data.startswith('c'):
                    message = binascii.b2a_hex(globalvars.data)
                    keylist = list(xrange(13))
                    vallist = list(xrange(13))
                    keylist[0] = 'Unknown1'
                    keylist[1] = 'Unknown2'
                    keylist[2] = 'ModuleName'
                    keylist[3] = 'FileName'
                    keylist[4] = 'CodeFile'
                    keylist[5] = 'ThrownAt'
                    keylist[6] = 'Unknown3'
                    keylist[7] = 'Unknown4'
                    keylist[8] = 'AssertPreCondition'
                    keylist[9] = 'Unknown5'
                    keylist[10] = 'OsCode'
                    keylist[11] = 'Unknown6'
                    keylist[12] = 'Message'
                    try:
                        os.mkdir('crashlogs')
                    except OSError as error:
                        log.debug('Client crash reports dir already exists')

                    templist = binascii.a2b_hex(message)
                    templist2 = templist.split('\x00')
                    try:
                        vallist[0] = str(int(binascii.b2a_hex(templist2[0][2:4]), base=16))
                        vallist[1] = str(int(binascii.b2a_hex(templist2[1]), base=16))
                        vallist[2] = str(templist2[2])
                        vallist[3] = str(templist2[3])
                        vallist[4] = str(templist2[4])
                        vallist[5] = str(int(binascii.b2a_hex(templist2[5]), base=16))
                        vallist[6] = str(int(binascii.b2a_hex(templist2[7]), base=16))
                        vallist[7] = str(int(binascii.b2a_hex(templist2[10]), base=16))
                        vallist[8] = str(templist2[13])
                        vallist[9] = str(int(binascii.b2a_hex(templist2[14]), base=16))
                        vallist[10] = str(int(binascii.b2a_hex(templist2[15]), base=16))
                        vallist[11] = str(int(binascii.b2a_hex(templist2[18]), base=16))
                        vallist[12] = str(templist2[23])
                        f = open('crashlogs\\' + str(ipactual) + '.csv', 'w')
                        f.write('SteamExceptionsData')
                        f.write('\n')
                        f.write(keylist[0] + ',' + keylist[1] + ',' + keylist[2] + ',' + keylist[3] + ',' + keylist[4] + ',' + keylist[5] + ',' + keylist[6] + ',' + keylist[7] + ',' + keylist[8] + ',' + keylist[9] + ',' + keylist[10] + ',' + keylist[11] + ',' + keylist[12])
                        f.write('\n')
                        f.write(vallist[0] + ',' + vallist[1] + ',' + vallist[2] + ',' + vallist[3] + ',' + vallist[4] + ',' + vallist[5] + ',' + vallist[6] + ',' + vallist[7] + ',' + vallist[8] + ',' + vallist[9] + ',' + vallist[10] + ',' + vallist[11] + ',' + vallist[12])
                        f.close()
                        log.info(clientid + 'Received client crash report')
                    except:
                        log.debug(clientid + 'Failed to receive client crash report')

                elif globalvars.data.startswith('q'):
                    print 'Received encrypted ICE client stats - INOP'
                elif globalvars.data.startswith('a'):
                    print 'Received app download stats - INOP'
                else:
                    print 'Unknown CSER command: %s' % globalvars.data
            elif self.port == 27014:
                log = logging.getLogger('27014')
                clientid = str(globalvars.addr) + ': '
                log.info(clientid + 'Connected to 27014')
                log.debug(clientid + 'Received message: %s, from %s' % (globalvars.data, globalvars.addr))
            elif self.port == 27017:
                log = logging.getLogger('friends')
                clientid = str(globalvars.addr) + ': '
                log.info(clientid + 'Connected to Chat Server')
                log.debug(clientid + 'Received message: %s, from %s' % (globalvars.data, globalvars.addr))
                message = binascii.b2a_hex(globalvars.data)
                if message.startswith('565330310000010000'):
                    friendsloginreply1 = 'VS01\x08\x00\x02\x00\x00\x00\x00\x00\x00\x02\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd6<\x10\xf0\xa4\x00\x00\x00'
                    serversocket.sendto(friendsloginreply1, globalvars.addr)
                elif message.startswith('5653303104000304'):
                    friendsloginreply2 = '56S01\x00\x00\x04\x04\x00\xeb\xb9\x14\x00\x02\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00'
                    serversocket.sendto(friendsloginreply2, globalvars.addr)
                    friendsloginreply3 = '56S01\x1c\x00\x06\x04\x00\xeb\xb9\x14\x00\x02\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00\x1c\x00\x00\x00\x17\x05\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x00\x00\x00\x01\x00\x00\x00'
                    serversocket.sendto(friendsloginreply3, globalvars.addr)
            else:
                print 'Who knows!'


config = read_config()
f = open(config['packagedir'] + config['steampkg'], 'rb')
pkg = Package(f.read())
f.close()
file = pkg.get_file('SteamNew.exe')
if config['public_ip'] != '0.0.0.0':
    file = neuter_file(file, config['public_ip'], config['dir_server_port'])
else:
    file = neuter_file(file, config['server_ip'], config['dir_server_port'])
f = open('client\\Steam.exe', 'wb')
f.write(file)
f.close()
if config['hldsupkg'] != '':
    g = open(config['packagedir'] + config['hldsupkg'], 'rb')
    pkg = Package(g.read())
    g.close()
    file = pkg.get_file('HldsUpdateToolNew.exe')
    if config['public_ip'] != '0.0.0.0':
        file = neuter_file(file, config['public_ip'], config['dir_server_port'])
    else:
        file = neuter_file(file, config['server_ip'], config['dir_server_port'])
    g = open('client\\HldsUpdateTool.exe', 'wb')
    g.write(file)
    g.close()
if os.path.isfile('Steam.exe'):
    os.remove('Steam.exe')
if os.path.isfile('HldsUpdateTool.exe'):
    os.remove('HldsUpdateTool.exe')
if os.path.isfile('log.txt'):
    os.remove('log.txt')
if os.path.isfile('library.zip'):
    os.remove('library.zip')
if os.path.isfile('MSVCR71.dll'):
    os.remove('MSVCR71.dll')
if os.path.isfile('python24.dll'):
    os.remove('python24.dll')
if os.path.isfile('python27.dll'):
    os.remove('python27.dll')
if os.path.isfile('Steam.cfg'):
    os.remove('Steam.cfg')
if os.path.isfile('w9xpopen.exe'):
    os.remove('w9xpopen.exe')
log.info('Checking for gcf files to convert...')
convertgcf()
time.sleep(0.2)
cserlistener = udplistener(27013, udpserver, config)
cserlistener.start()
log.info('CSER Server listening on port 27013')
time.sleep(0.2)
hlmasterlistener = udplistener(27010, masterhl, config)
hlmasterlistener.start()
log.info('Master HL1 Server listening on port 27010')
time.sleep(0.2)
hl2masterlistener = udplistener(27011, masterhl2, config)
hl2masterlistener.start()
log.info('Master HL2 Server listening on port 27011')
dirlistener = listener(config['dir_server_port'], directoryserver, config)
dirlistener.start()
log.info('Steam General Directory Server listening on port ' + str(config['dir_server_port']))
time.sleep(0.2)
configlistener = listener(config['conf_server_port'], configserver, config)
configlistener.start()
log.info('Steam Config Server listening on port ' + str(config['conf_server_port']))
time.sleep(0.2)
contentlistener = listener(config['contlist_server_port'], contentlistserver, config)
contentlistener.start()
log.info('Steam Content List Server listening on port ' + str(config['contlist_server_port']))
time.sleep(0.2)
filelistener = listener(config['file_server_port'], fileserver, config)
filelistener.start()
log.info('Steam File Server listening on port ' + str(config['file_server_port']))
time.sleep(0.2)
if config['steamver'] == 'v3':
    authlistener = listener(config['auth_server_port'], authserverv3, config)
else:
    authlistener = listener(config['auth_server_port'], authserver, config)
authlistener.start()
log.info('Steam Master Authentication Server listening on port ' + str(config['auth_server_port']))
time.sleep(0.2)
log.info('Steam Server ready.')
authlistener.join()