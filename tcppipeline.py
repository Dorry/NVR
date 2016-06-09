'''
Created on 2016. 6. 3.

@author: zia
'''
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from pipeline import Pipeline


class TcpPipeline(Pipeline):
    '''
    classdocs
    '''
    def __init__(self, host, port):
        '''
        Constructor
        '''
        super(TcpPipeline, self).__init__()

        self._host = host
        self._port = port

    def _make_pipeline(self):
        '''
        pipeline => gst-launch tcpclientsrc host="127.0.0.1" port=5000 ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert !
                                xvimagesink sync=false
        '''
        self.src = Gst.ElementFactory.make('tcpclientsrc', None)
        self.src.set_property('host', self._host)
        self.src.set_property('port', self._port)

        gdpdepay = Gst.ElementFactory.make('gdpdepay', None)
        rtpdepay = Gst.ElementFactory.make('rtph264depay', None)
        avdec = Gst.ElementFactory.make('avdec_h264', None)
        convert = Gst.ElementFactory.make('videoconvert', None)
        self.videosink = Gst.ElementFactory.make('xvimagesink', None)
        self.videosink.set_property('sync', False)

        for ele in (self.src, gdpdepay, rtpdepay, avdec, convert, self.videosink):
            self.pipe.add(ele)

        self.src.link(gdpdepay)
        gdpdepay.link(rtpdepay)
        rtpdepay.link(avdec)
        avdec.link(convert)
        convert.link(self.videosink)
