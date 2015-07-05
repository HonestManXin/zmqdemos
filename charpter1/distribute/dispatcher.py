# -*- coding: utf-8 -*-
import time
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer

addr = "tcp://127.0.0.1:5557"


class DispatchServer(BaseZmqServer):
    """
    原来push和pull既可以connect也可以bind
    """
    def __init__(self):
        super(DispatchServer, self).__init__()
        self.sender = ZMQUtils.create_bind_push(addr)
        self.counter = 1

    def run(self):
        self.sender.send(str(self.counter))
        self.counter += 1
        time.sleep(1)


def main():
    s = DispatchServer()
    s.start()


main()
