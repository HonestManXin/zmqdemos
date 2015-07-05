# -*- coding: utf-8 -*-

import time
import os
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer

dispatcher_addr = "tcp://127.0.0.1:5557"
collector_addr = "ipc:///tmp/collect.sock"


class WorkerServer(BaseZmqServer):
    def __init__(self):
        super(WorkerServer, self).__init__()
        self.receiver = ZMQUtils.create_conn_pull(dispatcher_addr)
        self.sender = ZMQUtils.create_conn_push(collector_addr)
        self.count = 0

    def run(self):
        index = self.receiver.recv()
        index = int(index)
        index += 10
        self.sender.send(str(index))
        self.count += 1
        print os.getpid(), " receive data:", index
        time.sleep(1)
        if self.count == 5:
            sys.exit(0)


def main():
    s = WorkerServer()
    s.start()

main()
