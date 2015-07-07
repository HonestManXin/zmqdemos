# -*- coding: utf-8 -*-
import zmq
import time
import random
import string
from threading import Thread
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils


dealer_addr = "ipc:///tmp/dealer.sock"
worker_addr = "inproc://backend"

identifies = string.letters[:5]


class AsyncClient(Thread):
    def __init__(self, identify):
        super(AsyncClient, self).__init__()
        self.identify = identify
        self.dealer = ZMQUtils.create_durable_dealer(dealer_addr, identify)
        self.poll = ZMQUtils.create_poller()
        self.poll.register(self.dealer, zmq.POLLIN)

    def run(self):
        count = 0
        while True:
            for i in xrange(100):
                sockets = dict(self.poll.poll(10))
                if self.dealer in sockets:
                    print "recv:", self.dealer.recv()

            msg = self.identify + str(count)
            self.dealer.send(msg)
            count += 1


class WorkerThread(Thread):

    def __init__(self):
        super(WorkerThread, self).__init__()
        self.recver = ZMQUtils.create_conn_dealer(worker_addr)

    def run(self):

        while True:
            parts = self.recver.recv_multipart()
            for i in xrange(random.randint(0, 4)):
                msg = parts[1]
                msg = msg + "_" + str(i)
                parts[1] = msg
                self.recver.send_multipart(parts)


class Server(object):

    def __init__(self):
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
        for _ in xrange(1):
            t = WorkerThread()
            t.start()

    def run(self):
        time.sleep(1)
        sockets = dict(self.poll.poll())
        if self.front in sockets:
            parts = self.front.recv_multipart()
            print parts
            self.back.send_multipart(parts)
        if self.back in sockets:
            parts = self.back.recv_multipart()
            self.front.send_multipart(parts)

s = Server()
s.run()
