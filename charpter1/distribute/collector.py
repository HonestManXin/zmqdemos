# -*- coding: utf-8 -*-

import time
import zmq
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer

addr = "ipc:///tmp/collect.sock"


class CollectorServer(BaseZmqServer):

    def __init__(self):
        super(CollectorServer, self).__init__()
        self.receiver = ZMQUtils.create_bind_pull(addr)
        self.counter = 0
        self.acc = 0

    def run(self):
        data = self.receiver.recv()
        data = int(data)
        self.acc += data
        self.counter += 1
        print "receive:", data
        if self.counter == 10:
            print "result is:", self.acc
            sys.exit(0)


def main():
    s = CollectorServer()
    s.start()


main()
