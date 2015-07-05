#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer

dealer_addr = "ipc:///tmp/dealer.sock"
router_addr = "ipc:///tmp/router.sock"


"""
queue device 主要用于 rep-req模式的代理
"""

class ProxyServer(BaseZmqServer):
    def __init__(self):
        super(ProxyServer, self).__init__()
        self.router = ZMQUtils.create_bind_router(router_addr)
        self.dealer = ZMQUtils.create_bind_dealer(dealer_addr)

    def run(self):
        ZMQUtils.create_queue_device(self.router, self.dealer)


def main():
    s = ProxyServer()
    s.start()


main()
