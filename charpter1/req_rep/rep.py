# -*- coding: utf-8 -*-
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer


addr = "ipc:///tmp/rep_req_proxy.sock"


class RepServer(BaseZmqServer):

    def __init__(self):
        super(RepServer, self).__init__()
        self.receiver = ZMQUtils.create_bind_rep(addr)
        self.index = 1

    def run(self):
        data = self.receiver.recv()
        self.receiver.send(data + str(self.index))
        self.index += 1
        print data


def main():
    s = RepServer()
    s.start()


main()
