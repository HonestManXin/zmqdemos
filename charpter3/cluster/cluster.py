# -*- coding: utf-8 -*-

from threading import Thread, Lock
import time
import random
import zmq
import sys
sys.path.append("../..")
from utils.zmqutils import ZMQUtils
from utils.server import BaseZmqServer


"""
ROUTER会丢弃无法路由的消息。需要等待大家连上来。
ROUTER-ROUTER套接字会在消息无法路由的情况下直接丢弃
"""


state_addr = "ipc:///tmp/idc%s-state.ipc"
local_front_addr = "ipc:///tmp/idc%s-localfront.ipc"
local_back_addr = "ipc:///tmp/idc%s-localback.ipc"
cloud_addr = "ipc:///tmp/idc%s-cloud.ipc"
# cloud_back_addr = "ipc:///tmp/idc%s-cloudback.ipc"

local_identify = "local_%s"
cloud_identify = "cloud_%s"

CLIENTS = 1
WORKS = 1

GLOCK = Lock()


def print_msg(msg):
    with GLOCK:
        print msg


def run_with_lock(func):
    with GLOCK:
        func()


class ClientThread(Thread):
    def __init__(self, front_addr, index):
        super(ClientThread, self).__init__()
        self.req = ZMQUtils.create_conn_req(front_addr)
        self.daemon = True
        self.index = index

    def run(self):
        while True:
            self.req.send('HELLO')
            print_msg("Client %d send request" % self.index)
            reply = self.req.recv()
            if reply == "END" or reply is None:
                break
            print_msg("Client %d recv msg: %s" % (self.index, reply))
            time.sleep(1)


class WorkerThread(Thread):
    def __init__(self, back_addr, index):
        super(WorkerThread, self).__init__()
        self.req = ZMQUtils.create_conn_req(back_addr)
        self.index = index
        self.daemon = True

    def run(self):
        self.req.send("READY")
        print_msg("worker %d send ready signal" % self.index)
        while True:
            request = self.req.recv_multipart()
            msg = "worker %d recv request: %s" % (self.index, request[-1])
            print_msg(msg)
            request[-1] = "OK_RESPONSE"
            self.req.send_multipart(request)
            print_msg("worker %d send response: %s" % (self.index, request))


class Server(BaseZmqServer):
    def __init__(self, index, number):
        super(Server, self).__init__()
        self.index = index
        self.peer_addrs = []
        self.peer_identifies = []
        self._create_state_sock(index, number)
        self._create_cloud_sock(index, number)
        self._create_local_sock(index)
        self.worker = []

        self._create_thread()
        print_msg("peer identify: %s" % self.peer_identifies)
        run_with_lock(lambda: raw_input("所有cluster准备好了吗?"))

    def _create_thread(self):
        back_addr = local_back_addr % self.index
        for i in xrange(WORKS):
            t = WorkerThread(back_addr, i)
            t.start()
        front_addr = local_front_addr % self.index
        for i in xrange(CLIENTS):
            t = ClientThread(front_addr, i)
            t.start()

    def _create_state_sock(self, index, number):
        back_state_addr = state_addr % index
        self.back_state = ZMQUtils.create_bind_pub(back_state_addr)

        front_statr_addrs = []
        for i in xrange(number):
            if i == index:
                continue
            addr = state_addr % i
            front_statr_addrs.append(addr)
        self.front_state = ZMQUtils.create_conn_sub(front_statr_addrs)
        self.front_state.setsockopt(zmq.SUBSCRIBE, "")

    def _create_cloud_sock(self, index, number):
        cloud_zmq_addr = cloud_addr % index
        self_identify = cloud_identify % index
        self.front_cloud = ZMQUtils.create_bind_router(cloud_zmq_addr, identify=self_identify)

        peer_cloud_addrs = []
        peer_cloud_idents = []
        for i in xrange(number):
            if i == index:
                continue
            peer_addr = cloud_addr % i
            peer_ident = cloud_identify % i
            peer_cloud_addrs.append(peer_addr)
            peer_cloud_idents.append(peer_ident)
        self.back_cloud = ZMQUtils.create_durable_router(peer_cloud_addrs, self_identify)
        self.peer_addrs = peer_cloud_addrs
        self.peer_identifies = peer_cloud_idents

    def _create_local_sock(self, index):
        front_addr = local_front_addr % index
        back_addr = local_back_addr % index
        self.front_local = ZMQUtils.create_bind_router(front_addr)
        self.back_local = ZMQUtils.create_bind_router(back_addr)

    def _state_loop(self):
        poll = ZMQUtils.create_poller()
        sockets = dict(poll.poll(1000))
        if self.front_state in sockets:
            peer_name, available = self.front_state.recv_multipart()
            print_msg("cluster %d recv: %s %s" % (self.index, peer_name, available))
        else:
            index = str(self.index)
            available = str(random.randint(1, 4))
            self.back_state.send_multipart([index, available])
            print_msg("cluster %s send: %s %s" % (index, index, available))

    def _response_loop(self):
        poll = ZMQUtils.create_poller()
        poll.register(self.back_local, zmq.POLLIN)
        poll.register(self.back_cloud, zmq.POLLIN)
        timeout = 1000 if len(self.worker) > 0 else None
        sockets = dict(poll.poll(timeout))
        response = None
        if self.back_local in sockets:
            parts = self.back_local.recv_multipart()
            self.worker.append(parts[0])
            if parts[2] == "READY":
                print_msg("cluster recv work ready")
            else:
                response = parts
                print_msg("cluster %d recv response from local: %s" % (self.index, response))
                response = response[2:]
        elif self.back_cloud in sockets:
            parts = self.back_cloud.recv_multipart()
            response = parts[2:]
            print_msg("cluster %d recv response from cloud: %s" % (self.index, response))

        if response is not None:
            address = response[0]
            if address in self.peer_identifies:
                self.front_cloud.send_multipart(response)
            else:
                self.front_local.send_multipart(response)

    def _request_loop(self):
        poll = ZMQUtils.create_poller()
        poll.register(self.front_local, zmq.POLLIN)
        poll.register(self.front_cloud, zmq.POLLIN)
        while len(self.worker) > 0:
            sockets = dict(poll.poll(timeout=5000))
            routable = False
            if self.front_local in sockets:
                msgs = self.front_local.recv_multipart()
                print_msg("cluster receive request from local: %s" % msgs)
                routable = True
            elif self.front_cloud in sockets:
                msgs = self.front_cloud.recv_multipart()
                print_msg("cluster receive request from cloud: %s" % msgs)
            else:
                print_msg("no request")
                return

            if routable and len(self.peer_addrs) != 0 and random.randint(1, 5) == 1:
                rand_peer = random.choice(self.peer_identifies)
                msgs = [rand_peer, ""] + msgs
                print_msg("cluster %d route to other cluster: %s" % (self.index, msgs))
                self.back_cloud.send_multipart(msgs)
            else:
                work_addr = self.worker[0]
                self.worker = self.worker[1:]
                work_msg = [work_addr, ""] + msgs
                self.back_local.send_multipart(work_msg)
                print_msg("cluster %d send msg to local: %s" % (self.index, work_msg))

    def run(self):
        self._response_loop()
        self._request_loop()


def _usage():
    print """
    python cluster.py index cluster_number
    0 <= index < cluster_number
    """
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        _usage()
    index = int(sys.argv[1])
    number = int(sys.argv[2])

    if not (0 <= index < number):
        _usage()

    s = Server(index, number)
    s.start()


if __name__ == '__main__':
    main()
