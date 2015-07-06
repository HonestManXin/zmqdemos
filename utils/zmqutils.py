#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zmq
from threading import Thread


class ZMQUtils(object):
    context = zmq.Context()
    _hwm = "hwm"
    _identify = "identify"

    @classmethod
    def create_context(cls):
        return zmq.Context()

    @classmethod
    def _create_bind(cls, addr, socket_type=zmq.PUSH, **kwargs):
        recver = cls.context.socket(socket_type)
        if cls._hwm in kwargs:
            hwm = kwargs[cls._hwm]
            recver.setsockopt(zmq.RCVHWM, hwm)
        if cls._identify in kwargs:
            identify = kwargs[cls._identify]
            recver.setsockopt(zmq.IDENTITY, identify)
        recver.bind(addr)
        return recver

    @classmethod
    def _create_conn(cls, addr,  socket_type=zmq.PULL, **kwargs):
        sender = cls.context.socket(socket_type)
        if cls._hwm in kwargs:
            hwm = kwargs[cls._hwm]
            sender.setsockopt(zmq.SNDHWM, hwm)
        if cls._identify in kwargs:
            identify = kwargs[cls._identify]
            sender.setsockopt(zmq.IDENTITY, identify)
        sender.connect(addr)
        return sender

    @classmethod
    def create_bind_rep(cls, addr, **kwargs):
        return cls._create_bind(addr, zmq.REP, **kwargs)

    @classmethod
    def create_conn_rep(cls, addr, **kwargs):
        return cls._create_conn(addr, zmq.REP, **kwargs)

    @classmethod
    def create_durable_rep(cls, addr, identify, **kwargs):
        kwargs = kwargs or {}
        kwargs[cls._identify] = identify
        return cls._create_conn(addr, zmq.REP, **kwargs)

    @classmethod
    def create_conn_req(cls, addr, **kwargs):
        return cls._create_conn(addr, zmq.REQ, **kwargs)

    @classmethod
    def create_durable_req(cls, addr, identify, **kwargs):
        kwargs = kwargs or {}
        kwargs[cls._identify] = identify
        return cls._create_conn(addr, zmq.REQ, **kwargs)

    @classmethod
    def create_bind_req(cls, addr, **kwargs):
        return cls._create_bind(addr, zmq.REQ, **kwargs)

    @classmethod
    def create_bind_pub(cls, addr, **kwargs):
        return cls._create_bind(addr, zmq.PUB, **kwargs)

    @classmethod
    def create_conn_pub(cls, addr, **kwargs):
        return cls._create_conn(addr, zmq.PUB, **kwargs)

    @classmethod
    def create_conn_sub(cls, addr, **kwargs):
        return cls._create_conn(addr, zmq.SUB, **kwargs)

    @classmethod
    def create_durable_sub(cls, addr, identify, **kwargs):
        kwargs = kwargs or {}
        kwargs[cls._identify] = identify
        return cls._create_conn(addr, zmq.SUB, **kwargs)

    @classmethod
    def create_bind_sub(cls, addr, **kwargs):
        return cls._create_bind(addr, zmq.SUB, **kwargs)

    @classmethod
    def create_bind_push(cls, addr, **kwargs):
        return cls._create_bind(addr, zmq.PUSH, **kwargs)

    @classmethod
    def create_bind_pull(cls, addr, **kwargs):
        return cls._create_bind(addr, zmq.PULL, **kwargs)

    @classmethod
    def create_conn_push(cls, addr, **kwargs):
        return cls._create_conn(addr, zmq.PUSH, **kwargs)

    @classmethod
    def create_conn_pull(cls, addr, **kwargs):
        return cls._create_conn(addr, zmq.PULL, **kwargs)

    @classmethod
    def create_durable_pull(cls, addr, identify, **kwargs):
        kwargs = kwargs or {}
        kwargs[cls._identify] = identify
        return cls._create_conn(addr, zmq.PULL, **kwargs)

    @classmethod
    def create_bind_router(cls, addr, **kwargs):
        return cls._create_bind(addr, zmq.ROUTER, **kwargs)

    @classmethod
    def create_conn_router(cls, addr, **kwargs):
        return cls._create_conn(addr, zmq.ROUTER, **kwargs)

    @classmethod
    def create_bind_dealer(cls, addr, **kwargs):
        return cls._create_bind(addr, zmq.DEALER, **kwargs)

    @classmethod
    def create_conn_dealer(cls, addr, **kwargs):
        return cls._create_conn(addr, zmq.DEALER, **kwargs)

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
