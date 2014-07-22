import sys
import csv
import re
import copy
from datetime import datetime
from datetime import timedelta
from dateutil import parser
import calendar
import subprocess
import time

class Agent:
  pass

class LookupAgent(Agent):
  def __init__(self, run_params):
    print "lookup agent"
    self.energy_estimate = {} # Key = (outdoor_temp, indoor_temp, energy), value = (heating_setpoint, cooling_setpoint)
    self.prediction_sim_file = run_params.run_name + '/for_lookup_predictions.csv'

  def get_next_setpoints(self, world):
    # debug
    times = [parser.parse("2013-04-01 02:00:00 CST"), parser.parse("2013-04-01 05:00:00 CST"), parser.parse("2013-04-03 09:00:00 CST"), parser.parse("2013-04-01 10:31:00 CST")]
    if (world.sim_time in times):
      return (world.heating_setpoint+1, world.cooling_setpoint+1)
    # TODO
    return None, None

class QLearnAgent(Agent):
  def __init__(self):
    print "qlearn agent"
    # TODO

  def get_next_setpoints(self, world):
    # TODO
    pass