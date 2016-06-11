'''
Created on 2016. 6. 3.

@author: zia
'''
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


class Pipeline(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.pipe = Gst.Pipeline.new()
        self.bus = None

        self._make_pipeline()

    def set_message_handler(self, func):
        if self.bus is None:
            self._set_bus()

        self.bus.connect('message', func)

    def set_sync_message_handler(self, func):
        if self.bus is None:
            self._set_bus()

        self.bus.connect('sync-message::element', func)

    def start(self):
        self.pipe.set_state(Gst.State.PLAYING)

    def stop(self):
        self.pipe.set_state(Gst.State.NULL)

    def _set_bus(self):
        self.bus = self.pipe.get_bus()
        self.bus.add_signal_watch()
        self.bus.enable_sync_message_emission()

    def _make_pipeline(self):
        raise NotImplementedError()
