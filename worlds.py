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

import util
import createGLM

class World:
  def final_cleanup(self):
    print "final cleanup"

class GldWorld(World):
  def __init__(self, run_params):
    print "gld world!"
    self.house_name = 'house_' + run_params.run_name
    sim_file = run_params.run_name + '/' + run_params.run_name + '_sim.txt'
    with open(sim_file, 'rb') as f:
      r = csv.reader(f, delimiter=' ')
      self.start_year = r.next()[1]
      self.start_month = r.next()[1]
      self.n_months = int(r.next()[1])
      self.timezone = r.next()[1]
      self.tmyfile = r.next()[1]
      self.house_size = r.next()[1]
      self.heater_type = r.next()[1]

    # Format times for GLD
    self.timezone_short = self.timezone[:3]
    self.start_control = parser.parse(self.start_year + "-" + self.start_month + "-01 00:00:00" + self.timezone_short)
    self.sim_start = self.start_control - timedelta(days = 2)
    self.sim_start_string = util.datetimeTOstring(self.sim_start, self.timezone_short)
    self.n_days_in_months = [calendar.monthrange(int(self.start_year)+i/12, int(self.start_month)+i)[1] for i in range(self.n_months)]
    self.end_control = self.start_control + timedelta(days = sum(self.n_days_in_months))
    self.sim_end = self.end_control + timedelta(hours = 1)
    self.sim_end_string = util.datetimeTOstring(self.sim_end, self.timezone_short)
    self.first_pause_at = util.datetimeTOstring(self.start_control, self.timezone_short)

    # Format files needed
    for file_description in ['energy_use_file', 'cooling_temps_file', 'heating_temps_file', 'indoor_temps_file', 'floor_player_file']:
      file_name = run_params.run_name + '/' + run_params.run_name + '_' + file_description[:-5] + '_' + run_params.agent + '.csv'
      setattr(self, file_description, file_name)
      with open(file_name,'wb') as f: # need to reset (some of) the files at the start of every run
        fwriter = csv.writer(f)
    with open(self.floor_player_file, 'wb') as f: # this file is needed to force GLD to work correctly (bug in GLD)
      fwriter = csv.writer(f)
      timestamp = self.start_control
      while (timestamp <= self.end_control):
        timestamp_string = util.datetimeTOstring(timestamp, self.timezone_short)
        fwriter.writerow([timestamp_string, "1000"])
        timestamp_sec = timestamp + timedelta(seconds = 1)
        timestamp_string = util.datetimeTOstring(timestamp_sec, self.timezone_short)
        fwriter.writerow([timestamp_string, "1000"])
        timestamp += timedelta(minutes = run_params.timestep)

    # Write GLM file
    self.glmfile = run_params.run_name + '/' + run_params.run_name + '_GLM_' + run_params.agent + '.glm'
    createGLM.write_GLM_file(self, run_params, "main")

  def run_first_time_step(self, run_params):
    # TODO
    pass

  def is_new_timestep(self):
    # TODO
    pass

  def update_state(self):
    # TODO
    pass

class EcobeeWorld(World):
  def __init__(self, run_params):
    print "ecobee world!"
    # TODO

  def run_first_time_step(self, run_params):
    # TODO
    pass

  def is_new_timestep(self):
    # TODO
    pass

  def update_state(self):
    # TODO
    pass
