# -*- coding: utf-8 -*-
import time
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer


addr = "ipc:///tmp/rep_req_proxy.sock"


class ReqServer(BaseZmqServer):
    def __init__(self):
        super(ReqServer, self).__init__()
        self.sender = ZMQUtils.create_conn_req(addr)

    def run(self):
        self.sender.send("hahaha")
        response = self.sender.recv()
        print response
        time.sleep(1)


def main():
    s = ReqServer()
    s.start()

main()
