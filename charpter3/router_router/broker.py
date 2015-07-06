# -*- coding: utf-8 -*-

from threading import Thread, Lock
import time
import zmq
import random
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils


front_addr = "ipc:///tmp/frontend.ipc"
back_addr = "ipc:///tmp/backend.ipc"
LOCK = Lock()

class ClientThread(Thread):
    def __init__(self):
        super(ClientThread, self).__init__()
        self.sender = ZMQUtils.create_conn_req(front_addr)

    def run(self):
        self.sender.send("HELLO")
        response = self.sender.recv()
        with LOCK:
            print "send get reply:", response

WORK_COUNT = 0

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
        self.workers = []

    def run(self):
        self._create_thread()
        time.sleep(1)
        msg_count = 0
        while True:
            sockets = self._get_ready_sockets()
            # 先处理backend，方便添加worker address
            if self.back in sockets:
                if self._handle_back_msg():
                    msg_count += 1

            if self.front in sockets:
                self._handle_front_msg()

            if msg_count == 10:
                break

    def _get_ready_sockets(self):
        self.poll = ZMQUtils.create_poller()
        if len(self.workers) == 0:
            self.poll.register(self.back, zmq.POLLIN)
        else:
            self.poll.register(self.back, zmq.POLLIN)
            self.poll.register(self.front, zmq.POLLIN)
        return dict(self.poll.poll())

    def _handle_front_msg(self):
        work_addr = self.workers[0]
        self.workers = self.workers[1:]
        msg = self.front.recv_multipart()
        back_msg = [work_addr, ""]
        back_msg.extend(msg)
        self.back.send_multipart(back_msg)

    def _handle_back_msg(self):
        parts = self.back.recv_multipart()
        client_addr = parts[2]
        self.workers.append(parts[0])
        if client_addr == "READY":
            return False
        self.front.send_multipart(parts[2:])
        return True

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
