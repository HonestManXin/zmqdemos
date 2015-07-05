#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Thread
from Queue import Queue
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils

addr = "ipc:///tmp/router.sock"


class ThreadOne(Thread):
    def __init__(self, start_queue, next_queue, index):
        super(ThreadOne, self).__init__()
        self.start_queue = start_queue
        self.next_queue = next_queue
        self.index = index
        self.sender = ZMQUtils.create_conn_req(addr)

    def run(self):
        self.start_queue.get()

        msg = str(self.index)
        self.sender.send(msg)
        print "thread one send msg:", msg

        self.next_queue.put(None)
        self.start_queue.get()

        result = self.sender.recv()
        print "thread one recv msg", result
        assert str(result) == str(self.index)


class ThreadTwo(Thread):
    def __init__(self, start_queue, next_queue, index):
        super(ThreadTwo, self).__init__()
        self.start_queue = start_queue
        self.next_queue = next_queue
        self.index = index
        self.sender = ZMQUtils.create_conn_req(addr)

    def run(self):
        self.start_queue.get()

        msg = str(self.index)
        self.sender.send(msg)
        print "thread two send msg:", msg
        result = self.sender.recv()
        print "thread two recv msg", result
        assert str(result) == str(self.index)

        self.next_queue.put(None)


class ReqServer(object):
    def __init__(self):
        super(ReqServer, self).__init__()

    @classmethod
    def run(cls):
        queue1 = Queue()
        queue2 = Queue()
        thread_one = ThreadOne(queue1, queue2, 1)
        thread_two = ThreadTwo(queue2, queue1, 2)

        thread_one.start()
        thread_two.start()

        queue1.put(None)

        thread_one.join()


def main():
    s = ReqServer()
    s.run()


main()
