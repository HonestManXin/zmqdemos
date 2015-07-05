# -*- coding: utf-8 -*-

import time
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils, ZmqThread
from utils.server import BaseZmqServer

addr = "ipc:///tmp/poll{%d}.sock"


class SendThread(ZmqThread):
    def __init__(self, index):
        super(SendThread, self).__init__()
        zmq_addr = addr % index
        self.sender = None
        self._init_zmq(zmq_addr)

    def _init_zmq(self, zmq_addr):
        self.sender = ZMQUtils.create_bind_push(zmq_addr)

    def run(self):
        index = 0
        while not self.stop_flag:
            msg = str(self.name) + ":" + str(index)
            print msg
            self.sender.send(msg)
            time.sleep(1)
            index += 1


class SendServer(BaseZmqServer):
    def __init__(self):
        super(SendServer, self).__init__()
        self._create_thread()

    @classmethod
    def _create_thread(cls):
        for index in range(2):
            th = SendThread(index)
            th.start()

    def run(self):
        time.sleep(1)

s = SendServer()
s.start()
