# -*- coding: utf-8 -*-

import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils


inproc = "inproc://example"


class IdentyServer(object):

    def __init__(self):
        self.router = ZMQUtils.create_bind_router(inproc)
        self.uuid_req = ZMQUtils.create_conn_req(inproc)
        self.dura_req = ZMQUtils.create_durable_req(inproc, "hello")

    def run(self):
        self.uuid_req.send("uuid")
        self._dump()

        self.dura_req.send("durable")
        self._dump()

    def _dump(self):
        msg = self.router.recv_multipart()
        print msg


s = IdentyServer()
s.run()
