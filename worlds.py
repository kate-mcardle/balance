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

class GldWorld_TempMeas(World):
  def __init__(self, run_params):
    print "simple gld world!"
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
    self.sim_end = self.end_control + timedelta(hours = 3)
    self.sim_end_string = util.datetimeTOstring(self.sim_end, self.timezone_short)
    self.first_pause_at = util.datetimeTOstring(self.start_control, self.timezone_short)
    self.sim_complete = False
    self.sim_time = ""

    # Format files needed
    for file_description in ['cooling_temps_file', 'heating_temps_file', 'indoor_temps_file', 'energy_use_file']:
      file_name = run_params.run_name + '/' + run_params.run_name + '_' + file_description[:-5] + '_' + run_params.agent + '.csv'
      setattr(self, file_description, file_name)
    self.floor_player_file = run_params.run_name + '/' + run_params.run_name + '_floor_player_second_run_' + run_params.agent + '.csv'
    with open(self.energy_use_file, 'rb') as f:
      r = csv.reader(f)
      for row_header in r:
        match = re.search(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', row_header[0])
        if match:
          break
      with open(self.floor_player_file, 'wb') as f2:
        fwriter = csv.writer(f2)
        for row in r:
          fwriter.writerow([row[0], self.house_size])
    self.energy_use_file = run_params.run_name + '/' + run_params.run_name + '_energy_use_second_run_' + run_params.agent + '.csv'

    # Write GLM file
    self.glmfile = run_params.run_name + '/' + run_params.run_name + '_GLM_second_run_' + run_params.agent + '.glm'
    createGLM.write_GLM_file(self, run_params, "temps")

class GldWorld(World):
  def __init__(self, run_params):
    print "gld world!"
    self.ts_count = 0
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
    self.sim_end = self.end_control + timedelta(hours = 3)
    self.sim_end_string = util.datetimeTOstring(self.sim_end, self.timezone_short)
    self.first_pause_at = util.datetimeTOstring(self.start_control, self.timezone_short)
    self.sim_complete = False
    self.sim_time = ""

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
        fwriter.writerow([timestamp_string, self.house_size])
        timestamp_sec = timestamp + timedelta(seconds = 5)
        timestamp_string = util.datetimeTOstring(timestamp_sec, self.timezone_short)
        fwriter.writerow([timestamp_string, self.house_size])
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
    self.last_timestep_energy_used = 0.0
    self.hvac_load = 0.0
    self.heating_setpoint = run_params.preferred_low_temp
    self.cooling_setpoint = run_params.preferred_high_temp
    self.last_mode = "COOL"

  def get_value(self, prop):
    args_get_value = ["wget", "http://localhost:6267/"+self.house_name+"/"+prop, "-q", "-O", "-"]
    cmd_get_value = subprocess.Popen(args_get_value, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_out, cmd_err = cmd_get_value.communicate()
    match = re.search(r'<value>.+</value>', cmd_out)
    if match:
      return match.group()[7:-8]
    else:
      print "Didn't find property ", prop, " in server request result!!"
      exit()    

  def is_new_timestep(self):
    # Poll for clock time to be >= pauseat time (get value of global variable 'clock'):
    args_check_clock = ["wget", "http://localhost:6267/clock", "-q", "-O", "-"]
    cmd_check_clock = subprocess.Popen(args_check_clock, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_out, cmd_err = cmd_check_clock.communicate() # waits for cmd_check_clock to finish before returning
    match = re.search(r'<value>.+</value>', cmd_out)
    if match: 
      sim_time = parser.parse(match.group()[7:-8])
      if (sim_time >= self.pause_time): # Simulation has been paused
        # Need to do housekeeping due to GridLAB-D's syncing
        clock_delta = sim_time - self.last_pause_time
        secs = clock_delta.total_seconds()
        self.last_timestep_energy_used += self.hvac_load * secs * (1.0/3600)
        self.hvac_load = float(self.get_value("hvac_load"))
        mode = self.get_value("system_mode")
        if (mode == "COOL") or (mode == "HEAT"):
          self.last_mode = mode
          # print "updated last_mode: ", last_mode
        self.last_pause_time = sim_time
        self.pause_time = sim_time + timedelta(seconds=1)
        if (self.pause_time > self.new_timestep_start):
          self.pause_time = self.new_timestep_start
        self.pause_string = util.datetimeTOstring(self.pause_time, self.timezone_short)
        if (sim_time >= self.new_timestep_start): # Simulation has been paused on a timestep transition
          self.sim_time = sim_time
          # if self.ts_count < 10:
          #   print "new timestep! sim time = ", self.sim_time
          #   self.ts_count += 1
          return True
        else: # resume simulation
          args_set_pause = ["wget","http://localhost:6267/control/pauseat="+self.pause_string, "-q", "-O", "-"]
          cmd_set_pause = subprocess.Popen(args_set_pause) #, stdout=subprocess.PIPE, stderr=subprocess.PIPE
          cmd_set_pause.communicate()
          return False
      elif self.pause_time > self.start_control: # This shouldn't happen
        print "clock at ", sim_time, "; pause_string = ", self.pause_string
        self.pause_time = sim_time + timedelta(seconds=10)
        self.pause_string = util.datetimeTOstring(self.pause_time, self.timezone_short)
        print "updating pause_time: ", self.pause_string
        args_set_pause = ["wget","http://localhost:6267/control/pauseat="+self.pause_string, "-O", "-"]
        cmd_set_pause = subprocess.Popen(args_set_pause, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd_out_pause, cmd_err_pause = cmd_set_pause.communicate()
        print "cmd_out_pause = ", cmd_out_pause
        print "cmd_err_pause = ", cmd_err_pause
    else: # This shouldn't happen
      print "cmd_out = ", cmd_out
      print "cmd_err = ", cmd_err
    return False

  def update_state(self, run_params):
    if (self.sim_time >= self.end_control):
      self.sim_complete = True
      return
    self.new_timestep_start += timedelta(minutes=run_params.timestep)
    # TODO
    # Will need to check if new month; if so, increment self.current_month_index (among other things)

  def set_next_setpoints(self, new_heating_setpoint, new_cooling_setpoint):
    # debug
    if (new_heating_setpoint != None and new_cooling_setpoint != None):
      self.heating_setpoint = new_heating_setpoint
      self.cooling_setpoint = new_cooling_setpoint
      args_set_heat = ["wget", "http://localhost:6267/"+self.house_name+"/heating_setpoint="+str(self.heating_setpoint), "-q", "-O", "-"]
      cmd_set_heat = subprocess.Popen(args_set_heat) #, stdout=subprocess.PIPE, stderr=subprocess.PIPE
      cmd_set_heat.communicate()
      with open(self.heating_temps_file,'a') as f:
        fwriter = csv.writer(f)
        fwriter.writerow([util.datetimeTOstring(self.sim_time, self.timezone_short), self.heating_setpoint])
      args_set_cool = ["wget", "http://localhost:6267/"+self.house_name+"/cooling_setpoint="+str(self.cooling_setpoint), "-q", "-O", "-"]
      cmd_set_cool = subprocess.Popen(args_set_cool) #, stdout=subprocess.PIPE, stderr=subprocess.PIPE
      cmd_set_cool.communicate()
      with open(self.cooling_temps_file,'a') as f:
        fwriter = csv.writer(f)
        fwriter.writerow([util.datetimeTOstring(self.sim_time, self.timezone_short), self.cooling_setpoint])

    # This should be the last thing to happen
    args_set_pause = ["wget","http://localhost:6267/control/pauseat="+self.pause_string, "-q", "-O", "-"]
    cmd_set_pause = subprocess.Popen(args_set_pause) #, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    cmd_set_pause.communicate()

  def final_cleanup(self, run_params):
    args_resume = ["wget", "http://localhost:6267/control/resume", "-O", "-"] 
    # "-O -" makes system not save output to a file
    # eventually will also want "-q" to not display output on console (helpful for now for debugging)
    cmd_resume = subprocess.call(args_resume) # subprocess.call will wait for call to finish before returning

    # Re-run, to measure comfort
    second_world = GldWorld_TempMeas(run_params)
    args_meas = ["gridlabd", second_world.glmfile]
    cmd_meas = subprocess.Popen(args_meas, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_out, cmd_err = cmd_meas.communicate()
    if ("ERROR" in cmd_err) or ("FATAL" in cmd_err):
      print "GridLAB-D error in prediction simulation!"
      print cmd_err
      exit()

    # Test
    results_file = run_params.run_name + "/" + run_params.run_name + "_results_second_run" + run_params.agent + ".csv"
    with open(results_file, 'wb') as f:
      fwriter = csv.writer(f)
    util.assess_budget(second_world, run_params, results_file, self.start_control, self.end_control)

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
