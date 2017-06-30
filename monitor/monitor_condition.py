"""
Created on 1 Jun 2017

@author: Filip Lindau
"""

import time
import sys
import os
import logging
import numpy as np
import PyTango as pt
from PyQt4 import QtGui, QtCore

# Path to gui widgets and AttributeReadThread class:
sys.path.insert(0, '../guitests/src/QTangoWidgets')

# Setup logger:
root = logging.getLogger()
while len(root.handlers):
    root.removeHandler(root.handlers[0])

f = logging.Formatter("%(asctime)s - %(module)s.   %(funcName)s - %(levelname)s - %(message)s")
fh = logging.StreamHandler()
fh.setFormatter(f)
root.addHandler(fh)
root.setLevel(logging.DEBUG)

# For reading attributes in a thread:
from AttributeReadThreadClass import AttributeClass


class MonitorOutputData(object):
    """
    This class is used for sending data with condition signals
    """
    def __init__(self, name=None, value=None, state=pt.DevState.UNKNOWN, status="", device_name=None):
        self.name = name
        self.value = value
        self.state = state
        self.status = status
        self.device_name = device_name


class MonitorCondition(QtCore.QObject):
    """
    Class to monitor attribute or other monitor objects. Subclass and reimplement the
    check_condition() method. The updata_data slot should be connected to signals that feed
    data to the monitor. The monitor emits a signal when the condition is fulfilled.
    The get_state() and get_status() methods can be used to check on the current status of
    the monitor.
    """
    monitor_condition_signal = QtCore.pyqtSignal(MonitorOutputData)

    def __init__(self, name):
        super(MonitorCondition, self).__init__()
        self.name = name
        self.data_input = dict()        # Directory where the input data is stored
        self.data_priority = dict()     # Directory where the input data priority is stored
        self.data_info = dict()
        self.name_name = dict()     # Directory where the input names are stored.
        # The keys are the names of the objects that send the signals to the check_conditions method.
        # The values are same names as in the data_input dict.
        self.state = pt.DevState.UNKNOWN
        self.status = ""
        self.value = 0.0

        self.state_priority = dict()
        self.state_priority[pt.DevState.FAULT] = 1
        self.state_priority[pt.DevState.UNKNOWN] = 2
        self.state_priority[pt.DevState.ALARM] = 3
        self.state_priority[pt.DevState.OFF] = 7
        self.state_priority[pt.DevState.DISABLE] = 5
        self.state_priority[pt.DevState.INIT] = 4
        self.state_priority[pt.DevState.ON] = 99
        self.state_priority[pt.DevState.EXTRACT] = 10
        self.state_priority[pt.DevState.MOVING] = 11
        self.state_priority[pt.DevState.INSERT] = 9
        self.state_priority[pt.DevState.RUNNING] = 90
        self.state_priority[pt.AttrQuality.ATTR_WARNING] = 6
        self.state_priority[pt.AttrQuality.ATTR_INVALID] = 4
        self.state_priority[pt.AttrQuality.ATTR_ALARM] = 3
        self.state_priority[pt.AttrQuality.ATTR_CHANGING] = 11
        self.state_priority[pt.AttrQuality.ATTR_VALID] = 99

        self.state_priority_safe_level = 10
        self.sorted_status_list = list()

    def add_input(self, name, data=None):
        name = name.lower()
        if name not in self.data_input:
            self.data_input[name] = data
            self.data_info[name] = None

    @QtCore.pyqtSlot(pt.DeviceAttribute, MonitorOutputData)
    def update_data(self, data):
        """
        This is a slot that is called to update the internal representation of data. The supplied data could be
        a pytango attribute or something else that has a name and value attribute.
        :param data:
        :return:
        """
        # We want to include the device name in the name to be able to have several attributes
        # with the same name in the dictionary.
        # Check the input type to see how to retrieve the device name.
        # If the type is DeviceAttribute, see if the sender has a device class attribute
        # that can be used (this is the case if the AttributeReadThread class is used)
        if type(data) == pt.DeviceAttribute:
            try:
                device_name = self.sender().device.name()
                attr_info = self.sender().get_attr_info()
                if attr_info is False:
                    attr_info = None
            except AttributeError:
                device_name = None
                attr_info = None
        elif type(data) == MonitorOutputData:
            device_name = data.device_name
            attr_info = None
        else:
            device_name = None
            attr_info = None

        if device_name is not None:
            name = "".join((device_name, "/", data.name))
        else:
            name = data.name

        name = name.lower()
        # root.debug("Found name " + name)
        if name in self.name_input:
            self.data_input[self.name_input[name]] = data
            self.data_info[self.name_input[name]] = attr_info
            self.check_condition()

    def check_condition(self):
        """
        Reimplement to reflect the actual condition. Emit signal if condition fulfilled. Update state and status.
        Example:
        if self.data_input['power'] < 0.1:
            value = 'power_low'
            self.emit_condition_signal(value)
        :return:
        """
        s = ""
        for key, value in self.data_input.viewitems():
            if value is None:
                self.state = pt.DevState.UNKNOWN
                s_tmp = str(key) + " is unknown\n"
                s += s_tmp

        self.status = s

        # Start with ON state and then modify if more severe states are encountered:
        self.state = pt.DevState.ON

        status_string_list = list()

        # Build composite status
        for attr_key in self.data_input:
            attr = self.data_input[attr_key]
            if type(attr) == MonitorOutputData:
                attr_state = attr.state
                attr_status = attr.status
                # Use here the self.sorted_status_list
            elif type(attr) == pt.DeviceAttribute:
                attr_state = attr.quality
                attr_status = ""
            if attr is not None:
                # Only update status for relevant states:
                if self.state_priority[attr_state] < self.state_priority_safe_level:
                    try:
                        # Add string with the priority of the message
                        status_string_list.append((self.data_priority[attr_key][1],
                                                   self.state_priority[attr_state],
                                                   self.data_priority[attr_key][0],
                                                   attr_state,
                                                   attr_key + " " + str(attr_state) + " " + attr_status))
                    except AttributeError:
                        status_string_list.append((self.data_priority[attr_key], attr_key + " attribute error"))

                # Check for critical faults
                if self.data_priority[attr_key][1] is True:
                    try:
                        if self.state_priority[attr_state] < self.state_priority[self.state]:
                            self.state = attr_state
                    except KeyError:
                        pass
                    except AttributeError:
                        pass

                else:
                    pass
            # root.debug(self.name + " status string: " + str(status_string_list))
            # Sort status list according to:
            # Required attribute, state priority, attribute priority
            self.sorted_status_list = sorted(status_string_list,
                                             key=lambda stat_str: (stat_str[0], stat_str[1], stat_str[2]), reverse=True)

    def emit_condition_signal(self, value, state=None, status=None):
        if state is None:
            state = self.state
        if status is None:
            status = self.status
        data = MonitorOutputData(self.name, value, state, status)
        self.monitor_condition_signal.emit(data)

    def get_state(self):
        return self.state

    def get_status(self):
        return self.sorted_status_list


class MonitorDevice(object):
    def __init__(self):
        self.devices = {}
        self.conditions = {}
        self.responses = {}
        self.state = pt.DevState.UNKNOWN

    def add_condition(self, condition_name, condition_obj, condition_response_name):
        self.conditions[condition_name] = (condition_obj, condition_response_name)

    def check_conditions(self):
        for condition in self.conditions:
            self.conditions[condition]


if __name__ == "__main__":
    mon = MonitorDevice()
    cond = MonitorCondition("power_level")
    mon.add_condition("power_level", cond)

