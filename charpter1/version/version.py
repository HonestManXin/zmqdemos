# -*- coding: utf-8 -*-

import zmq


def main():
    print zmq.zmq_version()
    print zmq.pyzmq_version()

main()