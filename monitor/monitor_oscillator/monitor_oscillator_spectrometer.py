"""
Created on 26 Jun 2017

@author: Filip Lindau
"""

from ..monitor_condition import MonitorCondition
import PyTango as pt
import numpy as np


class MonitorOscillatorFinesse(MonitorCondition):
    def __init__(self, monitor_name, device_name):
        super(MonitorOscillatorFinesse, self).__init__(monitor_name)

        self.name_input = dict()
        self.name_input[device_name] = 'device'
        self.data_input = dict()
        self.data_input['device'] = None
        self.last_read

    def check_condition(self):
        # Check all input if they are updated:
        super(MonitorOscillatorFinesse, self).check_condition()
        # Check if we are already unknown state, then there is not enough information to
        # determine the state of the oscillator
        if self.state != pt.DevState.UNKNOWN:
            # Start with ON state and then modify if more severe states are encountered:
            state = pt.DevState.ON

            s = ""
            attr = self.data_input['device'].value
            attr_info = attr.get_attr_info()
            # We set the value to the power level to display as the main characteristic of the oscillator
            self.value = attr.value
            if attr_info is not False:
                if attr.quality == pt.AttrQuality.ATTR_VALID:
                    if attr.value < np.double(attr_info.min_alarm()):
                        state = pt.DevState.ALARM
                        s += "Oscillator power LOW\n"
                elif attr.quality == pt.AttrQuality.ATTR_INVALID:
                    state = pt.DevState.FAULT
                    s += "Oscillator power attribute INVALID\n"
                elif attr.quality == pt.AttrQuality.ATTR_ALARM:
                    state = pt.DevState.ALARM
                    s += "Oscillator power attribute ALARM\n"
                elif attr.quality == pt.AttrQuality.ATTR_WARNING:
                    state = pt.DevState.ALARM
                    s += "Oscillator power attribute WARNING\n"

            else:
                s += "Oscillator power attribute INFO NOT LOADED.\n"
                state = pt.DevState.FAULT

            self.status = s
            self.state = state
