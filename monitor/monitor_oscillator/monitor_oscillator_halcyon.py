"""
Created on 30 Jun 2017

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


class MonitorOscillatorHalcyon(MonitorCondition):
    """
    Monitors the operation of the oscillator pump laser Finesse.
    Checks for power,
    """
    def __init__(self, monitor_name, monitor_errorfrequency, monitor_jitter, monitor_piezovoltage):
        super(MonitorOscillatorHalcyon, self).__init__(monitor_name)

        self.name_input = dict()
        self.data_input = dict()
        # Priority of each attribute. Expressed as a tuple with first element
        # relative priority (lower number => higher prio) and second element
        # if the attribute is required for operation
        self.data_priority = dict()

        self.name_input[monitor_errorfrequency] = 'errorfrequency'
        self.data_input['errorfrequency'] = None
        self.data_priority['errorfrequency'] = (2, True)
        self.name_input[monitor_jitter] = 'jitter'
        self.data_input['jitter'] = None
        self.data_priority['jitter'] = (10, False)
        self.name_input[monitor_piezovoltage] = 'piezovoltage'
        self.data_input['piezovoltage'] = None
        self.data_priority['piezovoltage'] = (4, True)

        # self.data_info['device'] = None
        self.last_read = None
        self.sorted_status_list = list()

    def check_condition(self):
        # Check all input if they are updated:
        super(MonitorOscillatorHalcyon, self).check_condition()

        s = str.join("\n", [sort_stat[4] for sort_stat in self.sorted_status_list])

        if s == "":
            s = "OK\n"

        new_status = "Halcyon\n" + s
        if new_status != self.status:
            self.status = new_status
            self.emit_condition_signal(self.value)
        else:
            self.status = new_status
