# -*- coding: utf-8 -*-

import zmq
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer

addr = "ipc:///tmp/poll{%d}.sock"


class PollServer(BaseZmqServer):
    def __init__(self):
        super(PollServer, self).__init__()
        self.sockets = self._create_sock()
        self.poller = self._create_poll(self.sockets)

    @classmethod
    def _create_sock(cls):
        sockets = []
        for index in range(2):
            zmq_addr = addr % index
            sock = ZMQUtils.create_conn_pull(zmq_addr)
            sockets.append(sock)
        return sockets

    @classmethod
    def _create_poll(cls, sockets):
        poller = ZMQUtils.create_poller()
        for sock in sockets:
            poller.register(sock, zmq.POLLIN)
        return poller

    def run(self):
        event_sockets = dict(self.poller.poll())
        for sock in event_sockets:
            print sock.recv()

s = PollServer()
s.start()