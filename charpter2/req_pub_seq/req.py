# -*- coding: utf-8 -*-
import time
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from threading import Thread
from Queue import Queue


addr = "ipc:///tmp/rep_req_proxy.sock"


class SendOneThread(Thread):
    run_index = 1

    def __init__(self, index, run_queue, next_queue):
        super(SendOneThread, self).__init__()
        self.index = index
        self.sender = ZMQUtils.create_conn_req(addr)
        self.run_queue = run_queue
        self.next_queue = next_queue
        self.daemon = True

    def run(self):
        self.run_queue.get()

        msg = "msg from %d" % self.index
        self.sender.send(msg)
        print "%d send msg" % self.index

        self.next_queue.put(None)
        self.run_queue.get()

        result = self.sender.recv()
        print "%d recv msg:%s" % (self.index, result)
        print "%d quit..." % self.index


class SendTwoThread(Thread):
    run_index = 1

    def __init__(self, index, run_queue, next_queue):
        super(SendTwoThread, self).__init__()
        self.index = index
        self.sender = ZMQUtils.create_conn_req(addr)
        self.run_queue = run_queue
        self.next_queue = next_queue
        self.daemon = True

    def run(self):
        self.run_queue.get()

        msg = "msg from %d" % self.index
        self.sender.send(msg)
        print "%d send msg" % self.index
        result = self.sender.recv()
        print "%d recv msg:%s" % (self.index, result)

        self.next_queue.put(None)
        print "%d quit..." % self.index


class ReqServer(object):
    def __init__(self):
        super(ReqServer, self).__init__()

    @classmethod
    def run(cls):
        one_run_queue = Queue()
        two_run_queue = Queue()
        thread1 = SendOneThread(1, one_run_queue, two_run_queue)
        thread2 = SendTwoThread(2, two_run_queue, one_run_queue)
        thread1.start()
        thread2.start()

        # start it
        one_run_queue.put(None)

        thread1.join()


def main():
    s = ReqServer()
    s.run()
    print "main process quit"

main()
