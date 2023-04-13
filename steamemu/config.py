# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\steamemu\config.py
import ConfigParser

def read_config():
    myDefaults = {'public_ip': '0.0.0.0', 'log_to_file': 'true', 'http_port': '', 'hldsupkg': '', 'steamver': 'v2', 'default_password': 'password', 'v2storagedir': 'files/v2storages/', 'v2manifestdir': 'files/v2manifests/'}
    c = ConfigParser.SafeConfigParser(myDefaults)
    c.read('emulator.ini')
    values = {}
    for name, value in c.items('config'):
        values[name] = value

    return values