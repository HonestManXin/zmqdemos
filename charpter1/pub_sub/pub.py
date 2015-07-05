#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer

addr = "ipc:///tmp/pub_sub.sock"


class PubServer(BaseZmqServer):
    def __init__(self):
        super(PubServer, self).__init__()
        self.sender = ZMQUtils.create_bind_pub(addr)

    def run(self):
        self.sender.send_multipart(["B", "weather info"])
        print "send one message"
        time.sleep(1)


def main():
    s = PubServer()
    s.start()

main()
