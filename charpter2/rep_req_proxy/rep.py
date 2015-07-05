#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
from Queue import Queue
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils

addr = "ipc:///tmp/dealer.sock"


"""
通过这个例子看起来本质上用router和dealer不能实现并发
"""

class ThreadOne(Thread):
    def __init__(self, start_queue, next_queue):
        super(ThreadOne, self).__init__()
        self.start_queue = start_queue
        self.next_queue = next_queue
        self.recver = ZMQUtils.create_conn_rep(addr)
        self.daemon = True

    def run(self):
        while True:
            # self.start_queue.get()

            msg = self.recver.recv()
            print "thread one recv: ", msg

            # self.next_queue.put(None)
            # self.start_queue.get()

            self.recver.send(msg)
            print "thread one send msg"


class ThreadTwo(Thread):
    def __init__(self, start_queue, next_queue):
        super(ThreadTwo, self).__init__()
        self.start_queue = start_queue
        self.next_queue = next_queue
        self.recver = ZMQUtils.create_conn_rep(addr)
        self.daemon = True

    def run(self):
        while True:
            # self.start_queue.get()

            msg = self.recver.recv()
            print "thread two recv:", msg
            self.recver.send(msg)
            print "thread two recv msg"

            # self.next_queue.put(None)
            # self.next_queue.put(None)


class RepServer(object):
    def __init__(self):
        super(RepServer, self).__init__()

    @classmethod
    def run(cls):
        queue1 = Queue()
        queue2 = Queue()
        thread_one = ThreadOne(queue1, queue2)
        thread_two = ThreadTwo(queue2, queue1)
        thread_one.start()
        thread_two.start()
        queue1.put(None)

        thread_one.join()


def main():
    s = RepServer()
    s.run()

main()
