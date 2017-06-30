"""
Created on 30 Jun 2017

@author: Filip Lindau
"""
from ..monitor_condition import MonitorCondition
import PyTango as pt
import numpy as np


class MonitorOscillatorHalcyonModelocked(MonitorCondition):
    """
    Monitors the operation of the oscillator pump laser Finesse.
    Checks for power,
    """
    def __init__(self, monitor_name, device_name):
        super(MonitorOscillatorHalcyonModelocked, self).__init__(monitor_name)

        self.name_input = dict()
        self.name_input[device_name] = 'device'
        self.data_input = dict()
        self.data_input['device'] = None
        self.data_info['device'] = None
        self.data_priority['device'] = (1, True)
        self.last_read = None

    def check_condition(self):
        # Check all input if they are updated:
        super(MonitorOscillatorHalcyonModelocked, self).check_condition()
        # Check if we are already unknown state, then there is not enough information to
        # determine the state of the oscillator

        # Start with ON state and then modify if more severe states are encountered:
        state = pt.DevState.ON

        s0 = ""
        s = ""
        attr = self.data_input['device']
        attr_info = self.data_info['device']
        # We set the value to the power level to display as the main characteristic of the oscillator
        self.value = attr.value
        if attr.quality == pt.AttrQuality.ATTR_VALID:
            if attr.value is False:
                state = pt.DevState.ALARM
                s += "NOT MODELOCKED\n"
        elif attr.quality == pt.AttrQuality.ATTR_INVALID:
            state = pt.AttrQuality.ATTR_INVALID
            s += "attribute INVALID\n"

        if s == "":
            s = "OK\n"
        new_status = s0 + s
        if new_status != self.status:
            self.emit_condition_signal(self.value)
        self.status = new_status
        self.state = state

