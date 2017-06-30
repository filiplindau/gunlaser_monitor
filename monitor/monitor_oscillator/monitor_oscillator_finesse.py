"""
Created on 29 Jun 2017

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


class MonitorOscillatorFinesse(MonitorCondition):
    """
    Monitors the operation of the oscillator pump laser Finesse.
    Checks for power,
    """
    def __init__(self, monitor_name, monitor_power, monitor_temperature, monitor_current, monitor_shutter):
        super(MonitorOscillatorFinesse, self).__init__(monitor_name)

        self.name_input = dict()
        self.data_input = dict()
        # Priority of each attribute. Expressed as a tuple with first element
        # relative priority (lower number => higher prio) and second element
        # if the attribute is required for operation
        self.data_priority = dict()

        self.name_input[monitor_power] = 'power'
        self.data_input['power'] = None
        self.data_priority['power'] = (1, True)
        self.name_input[monitor_temperature] = 'temperature'
        self.data_input['temperature'] = None
        self.data_priority['temperature'] = (2, True)
        self.name_input[monitor_current] = 'current'
        self.data_input['current'] = None
        self.data_priority['current'] = (4, False)
        self.name_input[monitor_shutter] = 'shutter'
        self.data_input['shutter'] = None
        self.data_priority['shutter'] = (5, True)

        # self.data_info['device'] = None
        self.last_read = None
        self.sorted_status_list = list()

    def check_condition(self):
        # Check all input if they are updated:
        super(MonitorOscillatorFinesse, self).check_condition()

        # Start with ON state and then modify if more severe states are encountered:
        # state = pt.DevState.ON
        #
        # s0 = "Finesse \n"
        # s = ""
        # status_string_list = list()
        #
        # # Build composite status
        # for attr_key in self.data_input:
        #     attr = self.data_input[attr_key]
        #     if attr is not None:
        #         # Only update status for relevant states:
        #         if self.state_priority[attr.state] < self.state_priority_safe_level:
        #             try:
        #                 # s = s + attr_key + " " + str(attr.state) + " " + attr.status + "\n"
        #                 # Add string with the priority of the message
        #                 status_string_list.append((self.data_priority[attr_key][1],
        #                                            self.state_priority[attr.state],
        #                                            self.data_priority[attr_key],
        #                                            self.attr.state,
        #                                            attr_key + " " + str(attr.state) + " " + attr.status))
        #             except AttributeError:
        #                 # s = s + attr_key + " attribute error"
        #                 status_string_list.append((self.data_priority[attr_key], attr_key + " attribute error"))
        #
        #         # Check for critical faults
        #         if self.data_priority[attr_key][1] is True:
        #             try:
        #                 if self.state_priority[attr.state] < self.state_priority[self.state]:
        #                     self.state = attr.state
        #             except KeyError:
        #                 pass
        #             except AttributeError:
        #                 pass
        #
        #         else:
        #             pass
        #
        # self.sorted_status_list = sorted(status_string_list,
        #                                  key=lambda stat_str: (stat_str[0], stat_str[1], stat_str[2]))
        s = str.join("\n", [sort_stat[4] for sort_stat in self.sorted_status_list])

        if s == "":
            s = "OK\n"

        new_status = "Finesse\n" + s
        if new_status != self.status:
            self.status = new_status
            self.emit_condition_signal(self.value)
        else:
            self.status = new_status
        # self.state = state

