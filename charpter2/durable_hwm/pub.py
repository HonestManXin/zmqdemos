# -*- coding: utf-8 -*-
import time
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils

sync_addr = "ipc:///tmp/sync.sock"
pub_addr = "ipc:///tmp/pub.sock"

MAX_CLIENT = 1


class Server(object):
    def __init__(self):
        self.syncer = ZMQUtils.create_bind_pull(sync_addr)
        self.puber = ZMQUtils.create_bind_pub(pub_addr)
        # self.puber.setsockopt(zmq.HWM, 10)

    def run(self):
        self.syncer.recv()
        print "started"
        self._pub_message()

    def _pub_message(self):
        message_index = 0
        while message_index < 100:
            msg = str(message_index)
            self.puber.send(msg)
            message_index += 1
            time.sleep(1)

        self.puber.send("END")


s = Server()
s.run()
