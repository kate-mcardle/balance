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
  pass

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
    self.start_control_string = util.datetimeTOstring(self.start_control, self.timezone_short)
    self.sim_start = self.start_control - timedelta(days = 2)
    self.sim_start_string = util.datetimeTOstring(self.sim_start, self.timezone_short)
    self.n_days_in_months = [calendar.monthrange(int(self.start_year)+i/12, int(self.start_month)+i)[1] for i in range(self.n_months)]
    self.end_control = self.start_control + timedelta(days = sum(self.n_days_in_months)) + timedelta(seconds = -1)
    self.end_control_string = util.datetimeTOstring(self.end_control, self.timezone_short)
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


  def launch(self, run_params):
    # Start GridLAB-D in server mode.
    # Popen does NOT wait for command to finish.
    args = ["gridlabd", self.glmfile, "--server", "-q"]
    cmd = subprocess.Popen(args) # does not wait for subprocess to finish

    # Wait for server to come online
    while True:
      args_check_clock = ["wget", "http://localhost:6267/clock", "-q", "-O", "-"]
      cmd_check_clock = subprocess.Popen(args_check_clock, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      cmd_out, cmd_err = cmd_check_clock.communicate() # waits for cmd_check_clock to finish before returning
      if cmd_out != "":
        break

    # Set first simulation pause
    self.pause_time = self.start_control
    self.pause_string = util.datetimeTOstring(self.pause_time, self.timezone_short)
    args_set_pause = ["wget","http://localhost:6267/control/pauseat="+self.pause_string, "-q", "-O", "-"]
    subprocess.call(args_set_pause) # waits for subprocess to complete

    # Initialize variables
    self.new_timestep_start = self.start_control
    self.last_pause_time = self.start_control + timedelta(seconds=-1)
    self.n_timesteps_in_day = 1440.0 / run_params.timestep
    self.n_timesteps_passed = -1
    self.current_month_index = 0
    self.hvac_load = 0.0
    self.heating_setpoint = run_params.preferred_low_temp
    self.cooling_setpoint = run_params.preferred_high_temp
    self.last_mode = "COOL"

  def is_new_timestep(self):
    # TODO
    pass

  def update_state(self):
    # TODO
    # Will need to check if new month; if so, increment self.current_month_index (among other things)
    pass

  def final_cleanup(self, run_params):
    args_resume = ["wget", "http://localhost:6267/control/resume", "-O", "-"] 
    # "-O -" makes system not save output to a file
    # eventually will also want "-q" to not display output on console (helpful for now for debugging)
    cmd_resume = subprocess.call(args_resume) # subprocess.call will wait for call to finish before returning

class EcobeeWorld(World):
  def __init__(self, run_params):
    print "ecobee world!"
    # TODO
    # MUST DEFINE energy_use_file, indoor_temps_file, start_control, AND end_control! For final assessment

  def launch(self, run_params):
    # TODO
    pass

  def is_new_timestep(self):
    # TODO
    pass

  def update_state(self):
    # TODO
    pass

  def final_cleanup(self, run_params):
    # TODO
    pass
