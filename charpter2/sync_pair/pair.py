#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils


step2_addr = "inproc://step2"
step3_addr = "inproc://step3"


class ThreadOne(Thread):
    def __init__(self):
        super(ThreadOne, self).__init__()
        self.sender = ZMQUtils.create_conn_pair(step2_addr)
        self.daemon = True

    def run(self):
        print "thread one done"
        self.sender.send("DONE")


class ThreadTwo(Thread):
    def __init__(self):
        super(ThreadTwo, self).__init__()
        self.recver = ZMQUtils.create_bind_pair(step2_addr)
        self.sender = ZMQUtils.create_conn_pair(step3_addr)
        self.daemon = True
        t = ThreadOne()
        t.start()

    def run(self):
        self.recver.recv()
        print "thread two done"
        self.sender.send("DONE")


class ThreadThree(Thread):
    def __init__(self):
        super(ThreadThree, self).__init__()
        self.recver = ZMQUtils.create_bind_pair(step3_addr)
        self.daemon = True
        t = ThreadTwo()
        t.start()

    def run(self):
        self.recver.recv()
        print "thread three done"


class SyncServer(object):

    def __init__(self):
        pass

    @classmethod
    def run(cls):

        thread = ThreadThree()
        thread.start()

        thread.join()

s = SyncServer()
s.run()
