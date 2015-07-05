# -*- coding: utf-8 -*-

import signal
import zmq

def _not_used(variable):
    _ = variable


class BaseZmqServer(object):
    def __init__(self):
        self.stop = False
        self._init_signal()

    def _init_signal(self):

        def _signal_handler(dummy_no, dummy_frame):
            _not_used(dummy_no)
            _not_used(dummy_frame)
            self.stop = True

        signal.signal(signal.SIGINT, _signal_handler)

    def run(self):
        raise NotImplementedError("run method not implemented")

    def start(self):
        while not self.stop:
            self.run()
