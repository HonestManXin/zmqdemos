# -*- coding: utf-8 -*-

import time
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils


"""
client有一条消息，将来会通过另一个ROUTER将该消息发送回去。这条信息包含了两个地址、一个空帧、以及消息内容；
client将该条消息发送给了ROUTER，并指定了REP的地址；
ROUTER将该地址移去，并以此决定其下哪个REP可以获得该消息；
REP收到该条包含地址、空帧、以及内容的消息；
REP将空帧之前的所有内容移去，交给worker去处理消息；
worker处理完成后将回复交给REP；
REP将之前保存好的信封包裹住该条回复，并发送给ROUTER；
ROUTER在该条回复上又添加了一个注明REP的地址的帧。
"""


addr = "ipc:///tmp/routing.ipc"


class RouteServer(object):
    def __init__(self):
        super(RouteServer, self).__init__()
        self.route = ZMQUtils.create_bind_router(addr)
        self.rep = ZMQUtils.create_durable_rep(addr, "A")

    def run(self):
        time.sleep(1)
        #  注意multipart的倒数第二个必须是空字符串
        self.route.send_multipart(["A", "A1", "A2", "A3", "", "request"])
        print self.rep.recv_multipart()
        self.rep.send("reply")
        print self.route.recv_multipart()


s = RouteServer()
s.run()
