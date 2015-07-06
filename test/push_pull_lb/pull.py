# -*- coding: utf-8 -*-

import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer

addr = "ipc:///tmp/push.sock"

"""
测试PUSH和PULL的load blance的能力
启动的时候启动多个pull, 然后随机的关闭其中的pull看看负载均衡情况
"""


class PullServer(BaseZmqServer):

    def __init__(self):
        super(PullServer, self).__init__()
        self.recver = ZMQUtils.create_conn_pull(addr)

    def run(self):
        msg = self.recver.recv()
        print msg


s = PullServer()
s.start()
