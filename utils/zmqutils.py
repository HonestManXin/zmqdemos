#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zmq
import time
from threading import Thread


class ZMQUtils(object):
    context = zmq.Context()

    @classmethod
    def _create_bind(cls, addr, socket_type=zmq.PUSH):
        recver = cls.context.socket(socket_type)
        recver.bind(addr)
        return recver

    @classmethod
    def _create_conn(cls, addr,  socket_type=zmq.PULL):
        sender = cls.context.socket(socket_type)
        sender.connect(addr)
        return sender

    @classmethod
    def create_bind_rep(cls, addr):
        return cls._create_bind(addr, zmq.REP)

    @classmethod
    def create_conn_rep(cls, addr):
        return cls._create_conn(addr, zmq.REP)

    @classmethod
    def create_conn_req(cls, addr):
        return cls._create_conn(addr, zmq.REQ)

    @classmethod
    def create_bind_req(cls, addr):
        return cls._create_bind(addr, zmq.REQ)

    @classmethod
    def create_bind_pub(cls, addr):
        return cls._create_bind(addr, zmq.PUB)

    @classmethod
    def create_conn_pub(cls, addr):
        return cls._create_conn(addr, zmq.PUB)

    @classmethod
    def create_conn_sub(cls, addr):
        return cls._create_conn(addr, zmq.SUB)

    @classmethod
    def create_bind_sub(cls, addr):
        return cls._create_bind(addr, zmq.SUB)

    @classmethod
    def create_bind_push(cls, addr):
        return cls._create_bind(addr, zmq.PUSH)

    @classmethod
    def create_bind_pull(cls, addr):
        return cls._create_bind(addr, zmq.PULL)

    @classmethod
    def create_conn_push(cls, addr):
        return cls._create_conn(addr, zmq.PUSH)

    @classmethod
    def create_conn_pull(cls, addr):
        return cls._create_conn(addr, zmq.PULL)

    @classmethod
    def create_bind_router(cls, addr):
        return cls._create_bind(addr, zmq.ROUTER)

    @classmethod
    def create_bind_dealer(cls, addr):
        return cls._create_bind(addr, zmq.DEALER)

    @classmethod
    def create_poller(cls):
        return zmq.Poller()

    @classmethod
    def create_queue_device(cls, frontend, backend):
        return zmq.device(zmq.QUEUE, frontend, backend)


_THREAD_ID = 1


class ZmqThread(Thread):

    def __init__(self):
        super(ZmqThread, self).__init__()
        global _THREAD_ID
        self.name = "zmq_" + str(_THREAD_ID)
        self.daemon = True
        self.stop_flag = False
        _THREAD_ID += 1

    def stop(self):
        self.stop_flag = False
