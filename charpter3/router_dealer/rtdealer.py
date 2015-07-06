# -*- coding: utf-8 -*-

import time
import random
from threading import Thread
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils

"""
ROUTER套接字会移除第一帧，只将第二帧的内容传递给相应的DEALER。
当DEALER发送消息给ROUTER时，只会发送一帧，ROUTER会在外层包裹一个信封（添加第一帧），返回给我们。
如果你定义了一个非法的信封地址，ROUTER会直接丢弃该消息，不作任何提示。

可以用这种方式实现自定义路由。
"""


inproc = "inproc://example"


class DealerThread(Thread):
    def __init__(self, identify):
        super(DealerThread, self).__init__()
        self.identify = identify
        self.recver = ZMQUtils.create_conn_dealer(inproc, identify=identify)

    def run(self):
        msg_count = 0
        while True:
            msg = self.recver.recv()
            if msg == "END":
                break
            msg_count += 1
        print "%s recv %d" % (self.identify, msg_count)


class Server(object):
    def __init__(self):
        self.sender = ZMQUtils.create_bind_router(inproc)
        self.idents = ["A", "B"]
        self._create_thread()

    def _create_thread(self):
        for ident in self.idents:
            t = DealerThread(ident)
            t.start()

    def _get_send_ident(self):
        if random.randint(1, 3) < 3:
            return self.idents[0]
        return self.idents[1]

    def run(self):
        time.sleep(1)
        for _ in range(12):
            ident = self._get_send_ident()
            self.sender.send_multipart([ident, "A"])
        for ident in self.idents:
            self.sender.send_multipart([ident, "END"])


s = Server()
s.run()
