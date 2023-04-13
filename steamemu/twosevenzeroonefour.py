# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\steamemu\twosevenzeroonefour.py
import threading, logging, struct, binascii, steam, globalvars
from steamemu.config import read_config
config = read_config()

class twosevenzeroonefour(threading.Thread):

    def __init__(self, socket, config):
        threading.Thread.__init__(self)
        self.socket = socket
        self.config = config

    def run(self):
        log = logging.getLogger('27014')
        clientid = str(config['server_ip']) + ': '
        log.info(clientid + 'Connected to 27014 Server')
        log.info(clientid + 'Disconnected from 27014 Server')