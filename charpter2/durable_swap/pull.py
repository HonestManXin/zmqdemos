# -*- coding: utf-8 -*-
import os
import sys
import zmq
sys.path.append("../..")
from utils.zmqutils import ZMQUtils

sync_addr = "ipc:///tmp/sync.sock"
sub_addr = "ipc:///tmp/pub.sock"


"""
如果要为套接字设置标识，必须在连接或绑定至端点之前设置
// pub sub 设置durable貌似没反应(有待重新尝试)
"""


class Client(object):
    def __init__(self):
        self.recver = ZMQUtils.create_conn_pull(sub_addr)
        self.syncer = ZMQUtils.create_conn_push(sync_addr)

    def run(self):
        self.syncer.send("PING")
        print "connected"

        recv_count = 0
        while True:
            response = self.recver.recv()
            if response == "END":
                break
            recv_count += 1
            print "recv response:", response

        print "%d recv msg count: %d" % (os.getpid(), recv_count)


c = Client()
c.run()
