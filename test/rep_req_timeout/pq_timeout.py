# -*- coding: utf-8 -*-
import zmq
import time
import string
from threading import Thread, Lock
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer


addr = "ipc:///tmp/timeout.sock"


class RepThread(Thread):
    def __init__(self):
        super(RepThread, self).__init__()
        self.rep = ZMQUtils.create_bind_rep(addr)
        self.daemon = True

    def run(self):
        while True:
            msg = self.rep.recv()
            time.sleep(2.5)
            self.rep.send(msg)
            print "rep responsed:", msg


class ReqThread(Thread):
    def __init__(self):
        super(ReqThread, self).__init__()
        self.daemon = True
        self.req = None
        self._create_req()

    def _create_req(self):
        self.req = ZMQUtils.create_conn_req(addr)

    def run(self):
        index = 0
        while True:
            send_index = index
            print "send: %d" % send_index
            self.req.send(str(send_index))
            index += 1

            poll = ZMQUtils.create_poller()
            poll.register(self.req, zmq.POLLIN)
            result = dict(poll.poll(timeout=1000))
            if not result:
                self._create_req()
                continue
            response = self.req.recv()
            if response != str(send_index):
                print "wo kao"


class Server(object):

    @classmethod
    def run(cls):
        t = RepThread()
        t.start()

        t = ReqThread()
        t.start()

        t.join()


s = Server()
s.run()
