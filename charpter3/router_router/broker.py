# -*- coding: utf-8 -*-

from threading import Thread
import time
import zmq
import random
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils


front_addr = "ipc:///tmp/frontend.ipc"
back_addr = "ipc:///tmp/backend.ipc"


class ClientThread(Thread):
    def __init__(self):
        super(ClientThread, self).__init__()
        self.sender = ZMQUtils.create_conn_req(front_addr)

    def run(self):
        self.sender.send("HELLO")
        print "send get reply:", self.sender.recv()


class WorkerThread(Thread):
    def __init__(self):
        super(WorkerThread, self).__init__()
        self.recver = ZMQUtils.create_conn_req(back_addr)
        self.daemon = True

    def run(self):
        self.recver.send("READY")
        while True:
            request = self.recver.recv_multipart()
            request[2] = "RESPONSE"
            self.recver.send_multipart(request)


class BrokerServer(object):
    def __init__(self):
        super(BrokerServer, self).__init__()
        self.front = ZMQUtils.create_bind_router(front_addr)
        self.back = ZMQUtils.create_bind_router(back_addr)
        self.poll = ZMQUtils.create_poller()
        self.poll.register(self.front, zmq.POLLIN)
        self.poll.register(self.back, zmq.POLLIN)

    def run(self):
        self._create_thread()
        time.sleep(1)
        workers = set()
        while True:
            sockets = dict(self.poll.poll())
            # 先处理backend，方便添加worker address
            if self.back in sockets:
                self._handle_back_msg(workers)

            if self.front in sockets:
                self._handle_front_msg(workers)

    def _handle_front_msg(self, workers):
        pass

    def _handle_back_msg(self, workers):
        parts = self.back.recv_multipart()

    @classmethod
    def _create_thread(cls):
        for _ in xrange(3):
            t = WorkerThread()
            t.start()
        time.sleep(1)
        for _ in xrange(10):
            t = ClientThread()
            t.start()


s = BrokerServer()
s.run()
