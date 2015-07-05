#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer

dealer_addr = "ipc:///tmp/dealer.sock"
router_addr = "ipc:///tmp/router.sock"


class ProxyServer(BaseZmqServer):
    def __init__(self):
        super(ProxyServer, self).__init__()
        self.router = ZMQUtils.create_bind_router(router_addr)
        self.dealer = ZMQUtils.create_bind_dealer(dealer_addr)
        self.poll = ZMQUtils.create_poller()
        self.poll.register(self.router, zmq.POLLIN)
        self.poll.register(self.dealer, zmq.POLLIN)

    def run(self):
        sockets = dict(self.poll.poll())
        print "poll return:", len(sockets)
        if self.router in sockets:
            requests = self.router.recv_multipart()
            print "proxy router recv msg:", requests
            self._write_to_dealer(requests)
        if self.dealer in sockets:
            # responses = self._recv_util_empty(self.dealer)
            responses = self.dealer.recv_multipart()
            print "proxy dealer recv msg:", responses
            self._write_to_router(responses)

    @classmethod
    def _recv_util_empty(cls, sock):
        msgs = []

        while True:
            try:
                msg = sock.recv_multipart(zmq.NOBLOCK)
                msgs.append(msg)
            except zmq.Again:
                break

        return msgs

    def _write_to_dealer(self, requests):
        # for request in requests:
        self.dealer.send_multipart(requests)

    def _write_to_router(self, responses):
        # for response in responses:
        self.router.send_multipart(responses)


def main():
    s = ProxyServer()
    s.start()


main()
