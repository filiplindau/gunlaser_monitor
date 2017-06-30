"""
Created on 26 Jun 2017

@author: Filip Lindau
"""
from ..monitor_condition import MonitorCondition
import PyTango as pt
import numpy as np
import logging

# Setup logger:
root = logging.getLogger()
while len(root.handlers):
    root.removeHandler(root.handlers[0])

f = logging.Formatter("%(asctime)s - %(module)s.   %(funcName)s - %(levelname)s - %(message)s")
fh = logging.StreamHandler()
fh.setFormatter(f)
root.addHandler(fh)
root.setLevel(logging.DEBUG)


class MonitorOscillatorFinessePower(MonitorCondition):
    """
    Monitors the operation of the oscillator pump laser Finesse.
    Checks for power,
    """
    def __init__(self, monitor_name, device_name):
        super(MonitorOscillatorFinessePower, self).__init__(monitor_name)

        self.name_input = dict()
        self.name_input[device_name] = 'device'
        self.data_input = dict()
        self.data_input['device'] = None
        self.data_info['device'] = None
        self.data_priority['device'] = (1, True)
        self.last_read = None

    def check_condition(self):
        # Check all input if they are updated:
        super(MonitorOscillatorFinessePower, self).check_condition()
        # Check if we are already unknown state, then there is not enough information to
        # determine the state of the oscillator

        # Start with ON state and then modify if more severe states are encountered:
        state = pt.DevState.ON

        # s0 = "Finesse power "
        s0 = ""
        s = ""
        attr = self.data_input['device']
        attr_info = self.data_info['device']
        # We set the value to the power level to display as the main characteristic of the oscillator
        self.value = attr.value
        if attr_info is not None:
            if attr.quality == pt.AttrQuality.ATTR_VALID:
                pass
            elif attr.quality == pt.AttrQuality.ATTR_INVALID:
                state = pt.AttrQuality.ATTR_INVALID
                s += "attribute INVALID\n"
            elif attr.quality == pt.AttrQuality.ATTR_ALARM:
                state = pt.DevState.ALARM
                try:
                    if attr.value < np.double(attr_info.min_alarm):
                        s += "attribute LOW\n"
                    elif attr.value > np.double(attr_info.max_alarm):
                        s += "attribute HIGH\n"
                except ValueError:
                    pass
            elif attr.quality == pt.AttrQuality.ATTR_WARNING:
                state = pt.AttrQuality.ATTR_WARNING
                try:
                    if attr.value < np.double(attr_info.alarms.min_warning):
                        s += "attribute LOW\n"
                    elif attr.value > np.double(attr_info.alarms.max_warning):
                        s += "attribute HIGH\n"
                except ValueError:
                    pass

        else:
            s += "attribute INFO NOT LOADED.\n"
            state = pt.DevState.FAULT

        if s == "":
            s = "OK\n"
        new_status = s0 + s
        self.state = state
        if new_status != self.status:
            self.status = new_status
            self.emit_condition_signal(self.value)
        else:
            self.status = new_status

