"""
Created on 1 Jun 2017

@author: Filip Lindau
"""

from monitor.monitor_oscillator import monitor_oscillator_finesse_power
from monitor.monitor_oscillator import monitor_oscillator_finesse_temperature
from monitor.monitor_oscillator import monitor_oscillator_finesse_shutter
from monitor.monitor_oscillator import monitor_oscillator_finesse_current
from monitor.monitor_oscillator import monitor_oscillator_finesse
import PyTango as pt
import sys
import logging
from PyQt4 import QtGui, QtCore
import time
sys.path.insert(0, '../guitests/src/QTangoWidgets')

# For reading attributes in a thread:
from AttributeReadThreadClass import AttributeClass
import QTangoWidgets as qw

# Setup logger:
root = logging.getLogger()
while len(root.handlers):
    root.removeHandler(root.handlers[0])

f = logging.Formatter("%(asctime)s - %(module)s.   %(funcName)s - %(levelname)s - %(message)s")
fh = logging.StreamHandler()
fh.setFormatter(f)
root.addHandler(fh)
root.setLevel(logging.DEBUG)


class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.monitors = dict()
        self.monitors['finesse_power'] = monitor_oscillator_finesse_power.MonitorOscillatorFinessePower(
            'monitor/gunlaser/finesse/power', 'gunlaser/oscillator/finesse/power')
        self.monitors['finesse_temperature'] = monitor_oscillator_finesse_temperature.MonitorOscillatorFinesseTemperature(
            'monitor/gunlaser/finesse/temperature', 'gunlaser/oscillator/finesse/lasertemperature')
        self.monitors['finesse_shutter'] = monitor_oscillator_finesse_shutter.MonitorOscillatorFinesseShutter(
            'monitor/gunlaser/finesse/shutter', 'gunlaser/oscillator/finesse/shutterstate')
        self.monitors['finesse_current'] = monitor_oscillator_finesse_current.MonitorOscillatorFinesseCurrent(
            'monitor/gunlaser/finesse/current', 'gunlaser/oscillator/finesse/current')
        self.monitors['finesse'] = monitor_oscillator_finesse.MonitorOscillatorFinesse(
            'monitor/gunlaser/finesse', 'monitor/gunlaser/finesse/power', 'monitor/gunlaser/finesse/temperature',
            'monitor/gunlaser/finesse/current', 'monitor/gunlaser/finesse/shutter')

        self.devices = dict()
        self.devices['finesse'] = pt.DeviceProxy('gunlaser/oscillator/finesse')
        self.attributes = dict()
        self.attributes['finesse_power'] = AttributeClass('power', self.devices['finesse'], 1.0,
                                                          self.monitors['finesse_power'].update_data, getInfo=True)
        self.attributes['finesse_temperature'] = AttributeClass('lasertemperature', self.devices['finesse'], 1.0,
                                                                self.monitors['finesse_temperature'].update_data,
                                                                getInfo=True)
        self.attributes['finesse_shutter'] = AttributeClass('shutterstate', self.devices['finesse'], 1.0,
                                                                self.monitors['finesse_shutter'].update_data,
                                                                getInfo=True)
        self.attributes['finesse_current'] = AttributeClass('current', self.devices['finesse'], 1.0,
                                                                self.monitors['finesse_current'].update_data,
                                                                getInfo=True)
        self.monitors['finesse_power'].monitor_condition_signal.connect(self.monitors['finesse'].update_data)
        self.monitors['finesse_temperature'].monitor_condition_signal.connect(self.monitors['finesse'].update_data)
        self.monitors['finesse_shutter'].monitor_condition_signal.connect(self.monitors['finesse'].update_data)
        self.monitors['finesse_current'].monitor_condition_signal.connect(self.monitors['finesse'].update_data)
        self.monitors['finesse'].monitor_condition_signal.connect(self.update)
        # self.attributes['finessePower'].attrSignal.connect(self.update)

        self.setup_layout()

    def update(self, data):
        if type(data) == pt.DeviceAttribute:
            root.debug("attr")
            self.finesse_name.setState(data)
        else:
            root.debug("moni")
            self.finesse_name.setState(data.state)

        self.finesse_status.setStatus(data.state, data.status)

    def closeEvent(self, event):
        root.debug("Closing down")
        for a in self.attributes.itervalues():
            a.stop_read()
            a.read_thread.join()
        root.debug("Threads joined... done")

    def setup_layout(self):
        s = 'QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.title_sizes = qw.QTangoSizes()
        self.title_sizes.barHeight = 30
        self.title_sizes.barWidth = 18
        self.title_sizes.readAttributeWidth = 300
        self.title_sizes.writeAttributeWidth = 150
        self.title_sizes.fontStretch = 80
        self.title_sizes.fontType = 'Arial'

        self.frame_sizes = qw.QTangoSizes()
        self.frame_sizes.barHeight = 30
        self.frame_sizes.barWidth = 35
        self.frame_sizes.readAttributeWidth = 300
        self.frame_sizes.writeAttributeWidth = 150
        self.frame_sizes.fontStretch = 80
        self.frame_sizes.fontType = 'Arial'
        #        self.frame_sizes.fontType = 'Trebuchet MS'

        self.attr_sizes = qw.QTangoSizes()
        self.attr_sizes.barHeight = 30
        self.attr_sizes.barWidth = 35
        self.attr_sizes.readAttributeWidth = 300
        self.attr_sizes.readAttributeHeight = 250
        self.attr_sizes.writeAttributeWidth = 299
        self.attr_sizes.fontStretch = 80
        self.attr_sizes.fontType = 'Arial'
        #        self.attr_sizes.fontType = 'Trebuchet MS'

        self.colors = qw.QTangoColors()

        layout_top = QtGui.QVBoxLayout(self)
        layout_top.setMargin(0)
        layout_top.setSpacing(0)
        layout_top.setContentsMargins(9, 9, 9, 9)

        layout_side = QtGui.QHBoxLayout()
        layout_side.setMargin(0)
        layout_side.setSpacing(0)
        layout_side.setContentsMargins(-1, 0, 0, 0)

        layout_inside = QtGui.QVBoxLayout()
        layout_inside.setMargin(0)
        layout_inside.setSpacing(0)
        layout_inside.setContentsMargins(-1, 0, 0, 0)
        spacer_item_v = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        spacer_item_bar = QtGui.QSpacerItem(self.frame_sizes.barWidth, self.frame_sizes.barHeight + 8,
                                            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        spacer_item_h = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        self.title = qw.QTangoTitleBar('Gunlaser overview', self.title_sizes)
        self.setWindowTitle('Gunlaser overview')
        self.sidebar = qw.QTangoSideBar(colors=self.colors, sizes=self.frame_sizes)
        self.bottombar = qw.QTangoHorizontalBar()

        layout_data = QtGui.QHBoxLayout()
        layout_data.setMargin(self.attr_sizes.barHeight / 2)
        layout_data.setSpacing(self.attr_sizes.barHeight * 2)
        self.layout_attributes_osc = QtGui.QVBoxLayout()
        self.layout_attributes_osc.setMargin(0)
        self.layout_attributes_osc.setSpacing(self.attr_sizes.barHeight / 2)
        self.layout_attributes_osc.setContentsMargins(0, 0, 0, 0)

        self.finesse_name = qw.QTangoDeviceNameStatus(colors=self.colors, sizes=self.frame_sizes)
        self.finesse_name.setAttributeName('Finesse')
        self.layout_attributes_osc.addWidget(self.finesse_name)

        self.finesse_status = qw.QTangoDeviceStatus(colors=self.colors, sizes=self.frame_sizes)
        self.finesse_status.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        self.layout_attributes_osc.addWidget(self.finesse_status)

        layout_top.addLayout(layout_side)
        layout_side.addLayout(layout_inside)

        layout_inside.addWidget(self.title)
        layout_inside.addSpacerItem(QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        layout_inside.addLayout(layout_data)
        layout_data.addLayout(self.layout_attributes_osc)

        self.setGeometry(200, 100, 600, 300)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = TangoDeviceClient()
    myapp.show()
    sys.exit(app.exec_())
