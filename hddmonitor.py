import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk, Gdk, Gio, GObject

class HDDMonitorWidget(Gtk.Widget):
    __gtype_name__ = 'HDDMonitorWidget'

    __gsignals__ = {
        'space-changed': (GObject.SIGNAL_RUN_LAST, None, ())
    }

    def __init__(self, monitor_device='/'):
        super(HDDMonitorWidget, self).__init__()

        self.__monitor_device = monitor_device
        self.__monitoring = Gio.File(monitor_device)
        self.__monitoring.monitor_directory()

    def do_realize(self):
        allocation = self.get_allocation()

        attr = Gdk.WindowAttr()
        attr.width = allocation.width
        attr.height = allocation.height
        attr.window_type = Gdk.WindowType.CHILD
        attr.x = allocation.x
        attr.y = allocation.y
        attr.visual = self.get_visual()
        attr.event_mask = self.get_events() | Gdk.EventMask.EXPOSE_MASK

        wat = Gdk.WindowAttributesType
        mask = wat.X | wat.Y | wat.VISUAL
        window = Gdk.Window(self.get_parent_window(), attr, mask)

        self.set_window(window)
        self.register_window(window)
        self.set_realized(True)
        window.set_background_pattern(None)

    def do_draw(self):
        pass

    def get_monitoring_device(self):
        return self.__monitor_device

    def set_monitoring_device(self, monitor_device=None):
        assert monitor_device == None

        self.__monitor_device = monitor_device
