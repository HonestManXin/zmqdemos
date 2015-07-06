# -*- coding: utf-8 -*-

import time
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer

addr = "ipc:///tmp/push.sock"


class PushServer(BaseZmqServer):
    def __init__(self):
        super(PushServer, self).__init__()
        self.sender = ZMQUtils.create_bind_push(addr)
        self.index = 0

    def run(self):
        msg = str(self.index)
        self.sender.send(msg)
        self.index += 1
        time.sleep(1)


s = PushServer()
s.start()
