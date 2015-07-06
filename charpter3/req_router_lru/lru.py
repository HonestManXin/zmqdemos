# -*- coding: utf-8 -*-

import time
import random
from threading import Thread
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils

"""
在将消息路由给REQ套接字时，需要注意一定的格式，即地址-空帧-消息

"""

addr = "inproc://example"
END = "END"
WORKER = 10


class ReqThread(Thread):
    def __init__(self, index):
        super(ReqThread, self).__init__()
        self.sender = ZMQUtils.create_conn_req(addr)
        self.index = index

    def run(self):
        count = 0
        while True:
            self.sender.send("READY")
            msg = self.sender.recv()
            if msg == END:
                break
            count += 1
            time.sleep(random.random())
        print "%d handle %d tasks" % (self.index, count)


class LruServer(object):
    def __init__(self):
        super(LruServer, self).__init__()
        self.recver = ZMQUtils.create_bind_router(addr)

    def run(self):
        self._create_thread()
        time.sleep(1)
        self._dispatch_task()

    @classmethod
    def _create_thread(cls):
        for i in xrange(WORKER):
            t = ReqThread(i)
            t.start()

    def _dispatch_task(self):
        for index in xrange(WORKER * 10):
            client = self.recver.recv_multipart()
            client[2] = str(index)
            self.recver.send_multipart(client)
        for _ in xrange(WORKER):
            client = self.recver.recv_multipart()
            client[2] = END
            self.recver.send_multipart(client)


s = LruServer()
s.run()
