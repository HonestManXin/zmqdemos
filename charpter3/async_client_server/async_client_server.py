# -*- coding: utf-8 -*-
import zmq
import time
import string
from threading import Thread, Lock
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer


"""
在使用dealer-router方式时在标示符和msg之间没有添加空消息
貌似只有req-router方式时才会插入空消息
"""


dealer_addr = "ipc:///tmp/dealer.sock"
worker_addr = "ipc:///tmp/backend.sock"

identifies = string.letters[:10]
GLOCK = Lock()


class AsyncClient(Thread):
    def __init__(self, identify):
        super(AsyncClient, self).__init__()
        self.identify = identify
        self.dealer = ZMQUtils.create_durable_dealer(dealer_addr, identify)
        self.poll = ZMQUtils.create_poller()
        self.poll.register(self.dealer, zmq.POLLIN)

        self.daemon = True

    def run(self):
        count = 0
        while True:
            for i in xrange(10):
                sockets = dict(self.poll.poll(100))
                if self.dealer in sockets:
                    with GLOCK:
                        print "client %s recv: %s" % (self.identify, self.dealer.recv())

            msg = self.identify + str(count)
            self.dealer.send(msg)
            count += 1


class WorkerThread(Thread):

    def __init__(self):
        super(WorkerThread, self).__init__()
        self.recver = ZMQUtils.create_conn_dealer(worker_addr)

        self.daemon = True

    def run(self):

        while True:
            parts = self.recver.recv_multipart()
            raw_msg = parts[1]
            for i in xrange(1):
                msg = raw_msg + "_" + str(i)
                parts[1] = msg
                self.recver.send_multipart(parts)
                with GLOCK:
                    print "work send", parts


class Server(BaseZmqServer):

    def __init__(self):
        super(Server, self).__init__()
        self.front = ZMQUtils.create_bind_router(dealer_addr)
        self.back = ZMQUtils.create_bind_dealer(worker_addr)
        self.poll = ZMQUtils.create_poller()

        self.poll.register(self.front, zmq.POLLIN)
        self.poll.register(self.back, zmq.POLLIN)

        self._create_thread()

    @classmethod
    def _create_thread(cls):
        for ident in identifies:
            t = AsyncClient(ident)
            t.start()
        for _ in xrange(5):
            t = WorkerThread()
            t.start()
        time.sleep(1)

    def run(self):
        sockets = dict(self.poll.poll())
        if self.front in sockets:
            parts = self.front.recv_multipart()
            self.back.send_multipart(parts)

        if self.back in sockets:
            parts = self.back.recv_multipart()
            self.front.send_multipart(parts)

s = Server()
s.start()
