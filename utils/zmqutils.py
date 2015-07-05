#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zmq
import time
from threading import Thread


class ZMQUtils(object):
    context = zmq.Context()

    @classmethod
    def create_context(cls):
        return zmq.Context()

    @classmethod
    def _create_bind(cls, addr, socket_type=zmq.PUSH, hwm=None):
        recver = cls.context.socket(socket_type)
        if hwm:
            recver.setsockopt(zmq.RCVHWM, hwm)
        recver.bind(addr)
        return recver

    @classmethod
    def _create_conn(cls, addr,  socket_type=zmq.PULL, hwm=None):
        sender = cls.context.socket(socket_type)
        if hwm:
            sender.setsockopt(zmq.SNDHWM, hwm)
        sender.connect(addr)
        return sender

    @classmethod
    def _create_durable_conn(cls, addr, identify, socket_type, hwm=None):
        sender = cls.context.socket(socket_type)
        sender.setsockopt(zmq.IDENTITY, identify)
        sender.setsockopt(zmq.SNDHWM, hwm)
        sender.connect(addr)
        return sender

    @classmethod
    def create_bind_rep(cls, addr, hwm=None):
        return cls._create_bind(addr, zmq.REP, hwm)

    @classmethod
    def create_conn_rep(cls, addr, hwm=None):
        return cls._create_conn(addr, zmq.REP, hwm)

    @classmethod
    def create_conn_req(cls, addr, hwm=None):
        return cls._create_conn(addr, zmq.REQ, hwm)

    @classmethod
    def create_bind_req(cls, addr, hwm=None):
        return cls._create_bind(addr, zmq.REQ, hwm)

    @classmethod
    def create_bind_pub(cls, addr, hwm=None):
        return cls._create_bind(addr, zmq.PUB, hwm)

    @classmethod
    def create_conn_pub(cls, addr, hwm=None):
        return cls._create_conn(addr, zmq.PUB, hwm)

    @classmethod
    def create_conn_sub(cls, addr, hwm=None):
        return cls._create_conn(addr, zmq.SUB, hwm)

    @classmethod
    def create_durable_sub(cls, addr, identify, hwm=None):
        return cls._create_durable_conn(addr, identify, zmq.SUB, hwm)

    @classmethod
    def create_bind_sub(cls, addr, hwm=None):
        return cls._create_bind(addr, zmq.SUB, hwm)

    @classmethod
    def create_bind_push(cls, addr, hwm=None):
        return cls._create_bind(addr, zmq.PUSH, hwm)

    @classmethod
    def create_bind_pull(cls, addr, hwm=None):
        return cls._create_bind(addr, zmq.PULL, hwm)

    @classmethod
    def create_conn_push(cls, addr, hwm=None):
        return cls._create_conn(addr, zmq.PUSH, hwm)

    @classmethod
    def create_conn_pull(cls, addr, hwm=None):
        return cls._create_conn(addr, zmq.PULL, hwm)

    @classmethod
    def create_durable_pull(cls, addr, identify, hwm=None):
        return cls._create_durable_conn(addr, identify, zmq.PULL, hwm)

    @classmethod
    def create_bind_router(cls, addr, hwm=None):
        return cls._create_bind(addr, zmq.ROUTER, hwm)

    @classmethod
    def create_bind_dealer(cls, addr, hwm=None):
        return cls._create_bind(addr, zmq.DEALER, hwm)

    @classmethod
    def create_poller(cls):
        return zmq.Poller()

    @classmethod
    def create_queue_device(cls, frontend, backend):
        return zmq.device(zmq.QUEUE, frontend, backend)

    @classmethod
    def create_bind_pair(cls, addr):
        return cls._create_bind(addr, zmq.PAIR)

    @classmethod
    def create_conn_pair(cls, addr):
        return cls._create_conn(addr, zmq.PAIR)


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
