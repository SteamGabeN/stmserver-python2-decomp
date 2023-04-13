# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\steamemu\converter.py
import os, ConfigParser, threading, logging, socket, time, globalvars
from gcf_to_storage import gcf2storage
from Steam.manifest import Manifest
from Steam2.neuter import neuter_file
from steamemu.config import read_config
config = read_config()

def convertgcf():
    log = logging.getLogger('converter')
    makeenc = Manifest()
    for filename in os.listdir('files/convert/'):
        if str(filename.endswith('.gcf')):
            dirname = filename[0:-4]
            if not os.path.isfile('files/cache/' + dirname + '/' + dirname + '.manifest'):
                log.info('Found ' + filename + ' to convert')
                log.info('Fixing files in ' + dirname)
                print '****************************************'
                g = open('files/convert/' + dirname + '.gcf', 'rb')
                file = g.read()
                g.close()
                if filename.startswith('0_') or filename.startswith('3_') or filename.startswith('5_') or filename.startswith('212_'):
                    if config['public_ip'] != '0.0.0.0':
                        for search, replace, info in globalvars.replacestrings2003ext:
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0:
                                print 'WARNING: Replacement text ' + replace + ' is too long! Not replaced!'
                            elif missinglength == 0:
                                file = file.replace(search, replace)
                                print 'Replaced ' + info + ' ' + search + ' with ' + replace
                            else:
                                file = file.replace(search, replace + '\x00' * missinglength)
                                print 'Replaced ' + info + ' ' + search + ' with ' + replace

                    else:
                        for search, replace, info in globalvars.replacestrings2003:
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0:
                                print 'WARNING: Replacement text ' + replace + ' is too long! Not replaced!'
                            elif missinglength == 0:
                                file = file.replace(search, replace)
                                print 'Replaced ' + info + ' ' + search + ' with ' + replace
                            else:
                                file = file.replace(search, replace + '\x00' * missinglength)
                                print 'Replaced ' + info + ' ' + search + ' with ' + replace

                else:
                    if config['public_ip'] != '0.0.0.0':
                        for search, replace, info in globalvars.replacestringsext:
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0:
                                print 'WARNING: Replacement text ' + replace + ' is too long! Not replaced!'
                            elif missinglength == 0:
                                file = file.replace(search, replace)
                                print 'Replaced ' + info + ' ' + search + ' with ' + replace
                            else:
                                file = file.replace(search, replace + '\x00' * missinglength)
                                print 'Replaced ' + info + ' ' + search + ' with ' + replace

                    else:
                        for search, replace, info in globalvars.replacestrings:
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0:
                                print 'WARNING: Replacement text ' + replace + ' is too long! Not replaced!'
                            elif missinglength == 0:
                                file = file.replace(search, replace)
                                print 'Replaced ' + info + ' ' + search + ' with ' + replace
                            else:
                                file = file.replace(search, replace + '\x00' * missinglength)
                                print 'Replaced ' + info + ' ' + search + ' with ' + replace

                        search = '207.173.177.11:27030 207.173.177.12:27030 69.28.151.178:27038 69.28.153.82:27038 68.142.88.34:27038 68.142.72.250:27038'
                        if config['public_ip'] != '0.0.0.0':
                            ip = config['public_ip'] + ':' + config['dir_server_port'] + ' ' + config['server_ip'] + ':' + config['dir_server_port'] + ' '
                        else:
                            ip = config['server_ip'] + ':' + config['dir_server_port'] + ' '
                        searchlength = len(search)
                        iplength = len(ip)
                        numtoreplace = searchlength // iplength
                        ips = ip * numtoreplace
                        replace = ips.ljust(searchlength, '\x00')
                        if file.find(search) != -1:
                            file = file.replace(search, replace)
                            print 'Replaced directory server IP group 1'
                        search = '207.173.177.11:27030 207.173.177.12:27030'
                        if config['public_ip'] != '0.0.0.0':
                            ip = config['public_ip'] + ':' + config['dir_server_port'] + ' ' + config['server_ip'] + ':' + config['dir_server_port'] + ' '
                        else:
                            ip = config['server_ip'] + ':' + config['dir_server_port'] + ' '
                        searchlength = len(search)
                        iplength = len(ip)
                        numtoreplace = searchlength // iplength
                        ips = ip * numtoreplace
                        replace = ips.ljust(searchlength, '\x00')
                        if file.find(search) != -1:
                            file = file.replace(search, replace)
                            print 'Replaced directory server IP group 5'
                        search = 'hlmaster1.hlauth.net:27010'
                        if config['public_ip'] != '0.0.0.0':
                            ip = config['public_ip'] + ':27010'
                        else:
                            ip = config['server_ip'] + ':27010'
                        searchlength = len(search)
                        iplength = len(ip)
                        numtoreplace = searchlength // iplength
                        ips = ip * numtoreplace
                        replace = ips.ljust(searchlength, '\x00')
                        if file.find(search) != -1:
                            file = file.replace(search, replace)
                            print 'Replaced default HL Master server'
                        for extraip in globalvars.extraips:
                            loc = file.find(extraip)
                            if loc != -1:
                                if config['public_ip'] != '0.0.0.0':
                                    server_ip = config['public_ip']
                                    replace_ip = server_ip.ljust(16, '\x00')
                                    file = file[:loc] + replace_ip + file[loc + 16:]
                                    print 'Found and replaced IP %s at location %08x' % (extraip, loc)
                                else:
                                    server_ip = config['server_ip']
                                    replace_ip = server_ip.ljust(16, '\x00')
                                    file = file[:loc] + replace_ip + file[loc + 16:]
                                    print 'Found and replaced IP %s at location %08x' % (extraip, loc)

                    for ip in globalvars.ip_addresses:
                        loc = file.find(ip)
                        if loc != -1:
                            if config['public_ip'] != '0.0.0.0':
                                server_ip = config['public_ip']
                                replace_ip = server_ip.ljust(16, '\x00')
                                file = file[:loc] + replace_ip + file[loc + 16:]
                                print 'Found and replaced IP %16s at location %08x' % (ip, loc)
                            else:
                                server_ip = config['server_ip']
                                replace_ip = server_ip.ljust(16, '\x00')
                                file = file[:loc] + replace_ip + file[loc + 16:]
                                print 'Found and replaced IP %16s at location %08x' % (ip, loc)

                time.sleep(1)
                h = open('files/temp/' + dirname + '.neutered.gcf', 'wb')
                h.write(file)
                h.close()
                time.sleep(1)
                gcf2storage('files/temp/' + dirname + '.neutered.gcf')
                time.sleep(1)
                os.remove('files/temp/' + dirname + '.neutered.gcf')
                print '****************************************'