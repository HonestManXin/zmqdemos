#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import zmq
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer

addr = "ipc:///tmp/pub_sub_proxy.sock"


class SubServer(BaseZmqServer):
    def __init__(self):
        super(SubServer, self).__init__()
        self.receiver = ZMQUtils.create_conn_sub(addr)
        # 必须要设置filter，否则收不到消息
        self.receiver.setsockopt(zmq.SUBSCRIBE, "B")

    def run(self):
        env, data = self.receiver.recv_multipart()
        print data


def main():
    s = SubServer()
    s.start()


main()
