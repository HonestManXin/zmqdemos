#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer

sub_addr = "ipc:///tmp/pub_sub.sock"
pub_addr = "ipc:///tmp/pub_sub_proxy.sock"


class ProxyServer(BaseZmqServer):
    def __init__(self):
        super(ProxyServer, self).__init__()
        self.receiver = ZMQUtils.create_conn_sub(sub_addr)
        self.sender = ZMQUtils.create_bind_pub(pub_addr)
        # 必须要设置filter，否则收不到消息
        self.receiver.setsockopt(zmq.SUBSCRIBE, "B")

    def run(self):
        env, data = self.receiver.recv_multipart()
        print "proxy receive", data
        self.sender.send_multipart([env, data+":proxy"])


def main():
    s = ProxyServer()
    s.start()


main()