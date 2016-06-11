'''
Created on 2016. 6. 10.

@author: Administrator
'''
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gst, GdkX11, GstVideo
from tcppipeline import TcpPipeline


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
    def __init__(self, host, port):
        super(Camera, self).__init__()

        self.display_widget = DisplayWidget()
        self.add(self.display_widget)

        self.src = TcpPipeline(host, port)
        self.src.set_message_handler(self.message)
        self.src.set_sync_message_handler(self.sync_message_handler)
        self.src.start()

    def message(self, bus, msg):
        pass
    
    def sync_message_handler(self, bus, msg):
        if msg.get_structure().get_name() == "prepare-window-handle":
            print("Prepare-window-handle")
            self.display_widget.set_sink(msg.src)


if __name__ == '__main__':
    from gi.repository import GObject
    GObject.threads_init()
    Gst.init(None)

    def quit(widget):
        cam.src.stop()
        Gtk.main_quit()

    win = Gtk.Window()
    win.connect('destroy', quit)
    hbox = Gtk.HBox()
    win.add(hbox)
    cam = Camera('127.0.0.1', 5000)
    hbox.pack_start(cam, True, True, 0)
    win.show_all()
    Gtk.main()
