import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GObject


DEFAULT = {'margin': 5,
           'format': "{used} / {total}",
           'fontsize': 12}


class DiskUsageWidget(Gtk.Widget):

    __gtype_name__ = 'DiskUsageWidget'

    __gsignals__ = {
        'space-changed': (GObject.SIGNAL_RUN_LAST, None, (GObject.TYPE_FLOAT,))
    }

    def __init__(self, monitor_disk='/',
                 show_label=True,
                 label_format=DEFAULT['format'],
                 label_alignment=Gtk.PositionType.TOP):
        super(DiskUsageWidget, self).__init__()

        if not isinstance(label_alignment, Gtk.PositionType):
            raise ValueError("label_alignment's type is not Gtk.PositionType.")

        self.__monitor_disk = monitor_disk
        self.__show_label = show_label
        self.__label_alignment = label_alignment
        self.__label_format = label_format or DEFAULT['format']  # format string is {percent}, {used}, {total}

        self.__file = Gio.File.new_for_path(monitor_disk)
        self.__monitoring = self.__file.monitor_directory(Gio.FileMonitorFlags.NONE, None)
        self.__monitoring.connect('changed', self.__usage_changed)

        _, self.__used, self.__total = self.__calculate_diskusage()

    def set_label_format(self, label_format):
        self.__label_format = label_format
        self.queue_draw()

    def get_label_alignment(self):
        return self.__label_alignment

    def set_label_alignment(self, alignment):
        self.__label_alignment = alignment
        self.queue_draw()

    def __usage_changed(self, file_monitor, file, other_file, event_type):
        print(event_type)
        if event_type in (Gio.FileMonitorEvent.CREATED,
                          Gio.FileMonitorEvent.CHANGED, 
                          Gio.FileMonitorEvent.CHANGES_DONE_HINT,
                          Gio.FileMonitorEvent.ATTRIBUTE_CHANGED):
            print("파일이 생성되었습니다.")
        elif event_type in (Gio.FileMonitorEvent.DELETED):
            print("파일이 삭제되었습니다.")

        print("file : ", file.get_parse_name())
        if other_file is not None:
            print("other_file : ", other_file.get_parse_name())

        percent, self.__used, self.__total = self.__calculate_diskusage()
        self.emit('space-changed', percent)

    def __calculate_disksize(self, dsize):
        dsize_format = ('Byte', 'KB', 'MB', 'GB', 'TB')
        count = 0

        while dsize >= 1024:
            dsize = round(float(dsize) / 1024, 1)
            count += 1

        return '%0.1f%s' % (dsize, dsize_format[count])

    def __calculate_diskusage(self):
        if hasattr(os, 'statvfs'):
            st = os.statvfs(self.__monitor_disk)
            total = st.f_blocks * st.f_frsize
            used = (st.f_blocks - st.f_bfree) * st.f_frsize
        else:
            import ctypes
            _, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
            fun = ctypes.windll.kernel32.GetDiskFreeSpaceExW
            ret = fun(self.__monitor_disk, ctypes.byref(_), ctypes.byref(total), ctypes.byref(free))
            if ret == 0:
                raise ctypes.WinError()
            used = total.value - free.value
            total = total.value
        print(used/total)
        print(round(used/total, 3))

        return round(used/total, 2), used, total

    def do_realize(self):
        allocation = self.get_allocation()

        attr = Gdk.WindowAttr()
        attr.width = allocation.width
        attr.height = allocation.height
        attr.window_type = Gdk.WindowType.CHILD
        attr.x = allocation.x
        attr.y = allocation.y
        attr.visual = self.get_visual()
        attr.event_mask = self.get_events() \
                          | Gdk.EventMask.EXPOSURE_MASK \
                          | Gdk.EventMask.POINTER_MOTION_MASK \
                          | Gdk.EventMask.POINTER_MOTION_HINT_MASK

        wat = Gdk.WindowAttributesType
        mask = wat.X | wat.Y | wat.VISUAL
        window = Gdk.Window(self.get_parent_window(), attr, mask)

        self.set_window(window)
        self.register_window(window)
        self.set_realized(True)
        window.set_background_pattern(None)

    def do_draw(self, cr):
        text = 'Usage : {used} / {total}'.format(used=self.__calculate_disksize(self.__used), 
                                                 total=self.__calculate_disksize(self.__total))
        text = self.__monitor_disk + ' => ' + text

        allocation = self.get_allocation()

        x_bearing, y_bearing, width, height, x_advance, y_advance = cr.text_extents(text)
        # print(x_bearing, y_bearing, width, height, x_advance, y_advance)

        cr.set_source_rgb(0.4, 0.2, 0.8)
        cr.set_line_width(1)

        cr.move_to(0, 5)
        cr.line_to(allocation.width, 5)
        cr.stroke()

        cr.move_to((allocation.width - width)/2, (height + 15))
        cr.show_text(text)

    def do_space_changed(self, usage_percent):
        print('Now "%s" usage => %0.2f%%' % (self.__monitor_disk, (usage_percent * 100)))
        self.queue_draw()

    def do_unrealize(self):
        self.get_window().destroy()

    def get_monitoring_disk(self):
        return self.__monitor_disk

    def set_monitoring_disk(self, monitor_disk=None):
        assert monitor_disk is None

        self.__monitor_disk = monitor_disk

    def stop(self):
        del self.__file, self.__monitoring

GObject.type_register(DiskUsageWidget)

if __name__ == '__main__':
    import sys
    win = Gtk.Window()
    if sys.platform == 'linux':
        widget = DiskUsageWidget(monitor_disk='/home/zia')
    else:
        widget = DiskUsageWidget(monitor_disk='D:')
    win.set_title('DiskUsageWidget Sample')
    win.add(widget)
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()
    widget.stop()
