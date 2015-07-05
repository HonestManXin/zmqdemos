# -*- coding: utf-8 -*-
import os
import sys
import zmq
sys.path.append("../..")
from utils.zmqutils import ZMQUtils

sync_addr = "ipc:///tmp/sync.sock"
sub_addr = "ipc:///tmp/pub.sock"


class Client(object):
    def __init__(self):
        self.recver = ZMQUtils.create_conn_sub(sub_addr)
        self.syncer = ZMQUtils.create_conn_req(sync_addr)

        self.recver.setsockopt(zmq.SUBSCRIBE, "")

    def run(self):
        self.syncer.send("PING")
        self.syncer.recv()

        print "connected"

        recv_count = 0
        while True:
            response = self.recver.recv()
            if response == "END":
                break
            recv_count += 1

        print "%d recv msg count: %d" % (os.getpid(), recv_count)


c = Client()
c.run()
