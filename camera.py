'''
Created on 2016. 6. 10.

@author: Administrator
'''
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gst, GdkX11


class DisplayWidget(Gtk.DrawingArea):
    def __init__(self):
        super(DisplayWidget, self).__init__()
        self._xid = None
        self._sink = None
        self.modify_bg(Gtk.StateType.NORMAL, self.get_style().black)
        self.show()

    def do_expose_event(self, event):
        if self._sink is not None:
            self._sink.expose()
            return False
        else:
            return True

    def set_sink(self, sink):
        self._xid = self.get_property('window').get_xid()
        self._sink = sink
        self._sink.set_property('force-aspect-ratio', True)
        self._sink.set_window_handle(self._xid)


class Camera(Gtk.Overlay):
    def __init__(self, params):
        super(Camera, self).__init__()
