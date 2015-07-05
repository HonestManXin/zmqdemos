# -*- coding: utf-8 -*-
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils

sync_addr = "ipc:///tmp/sync.sock"
pub_addr = "ipc:///tmp/pub.sock"

MAX_CLIENT = 10


class Server(object):
    def __init__(self):
        self.syncer = ZMQUtils.create_bind_rep(sync_addr)
        self.puber = ZMQUtils.create_bind_pub(pub_addr)

    def run(self):
        self._wait_clients()
        self._pub_message()

    def _wait_clients(self):
        connected_clients = 0
        while connected_clients < MAX_CLIENT:
            self.syncer.recv()
            connected_clients += 1
            self.syncer.send("PONG")

    def _pub_message(self):
        message_index = 0
        while message_index < 100:
            msg = str(message_index)
            self.puber.send(msg)
            message_index += 1

        self.puber.send("END")


s = Server()
s.run()
