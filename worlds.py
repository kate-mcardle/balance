'''
worlds.py manages the passage of time in the agent's lifespan. The World class is a 
(virtual) base class; the derived classes that are used in balance.py are GldWorld and 
EcobeeWorld. These classes interact with the simulator or Ecobee to get the most recent
temperature and energy use values and set new thermostat setpoints.

Additionally, the derived class GldTempMeasWorld is provided to re-run the simulation 
in order to record temperatures every minute, and the derived class GldPredictiveWorld
is provided solely for the LookupAgent to use in its predictions. The derived class 
GldBaselineWorld is provided to run the baseline agents (LowestCostAgent and HighestComfortAgent) 
in "regular" mode (as opposed to server mode), because it is much faster.
'''

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
  '''
  Base class for the world used by balance; 
  '''
  def __init__(self, run_params, agent):
    '''
    Class constructor for the world. Takes care of any setup but does not initiate the
    "start" of the world.
    '''
    print "Didn't define --constructor-- for this derived class!"

  def launch(self, agent):
    '''
    Starts communication between the world and balance, bringing them 
    to the same point in time.
    '''
    print "Didn't define --launch-- method for this derived class!"

  def is_new_timestep(self):
    '''
    Controls balance's main control flow, to check if the current time 
    corresponds with a "balance" timestep. Also does housekeeping as needed, to track any 
    changes to the world that must be tracked as often as possible (eg HVAC usage).
    '''
    print "Didn't define --is_new_timestep-- method for this derived class!"

  def update(self, agent):
    '''
    Updates the values for the features of the world that may have changed since the
    last timestep, such as indoor and outdoor temperature.
    '''
    print "Didn't define --update-- method for this derived class!"

  def set_next_setpoints(self, new_heating_setpoint, new_cooling_setpoint):
    '''
    Adjusts the thermostat's heating and cooling setpoints to the values provided as arguments.
    '''
    print "Didn't define --set_next_setpoints-- method for this derived class!"

  def final_cleanup(self, run_params, agent):
    '''
    Completes any remaining housekeeping.
    '''
    print "Didn't define --final_cleanup-- method for this derived class!"

class GldWorld(World):
  def __init__(self, run_params, agent):
    # print "initializing GldWorld"
    self.ts_count = 0
    self.house_name = 'house_' + run_params.run_name
    sim_file = run_params.run_name + '/' + run_params.run_name + '_sim_settings.txt'
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
    # debug (comment/uncomment line above):
    # self.end_control = self.start_control + timedelta(hours=15)
    self.sim_end = self.end_control + timedelta(hours = 3)
    self.sim_end_string = util.datetimeTOstring(self.sim_end, self.timezone_short)
    self.first_pause_at = util.datetimeTOstring(self.start_control, self.timezone_short)
    self.sim_complete = False
    self.sim_time = ""

    # Format files needed
    for file_description in ['energy_use_file', 'cooling_temps_file', 'heating_temps_file', 'indoor_temps_file', 'floor_player_file']:
      file_name = run_params.run_name + '/' + run_params.run_name + '_' + file_description[:-5] + '_' + run_params.agent + '.csv'
      setattr(self, file_description, file_name)
    # UNCOMMENT HERE!
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
        timestamp += timedelta(minutes = agent.timestep)

    # Write GLM file
    self.glmfile = run_params.run_name + '/' + run_params.run_name + '_GLM_' + run_params.agent + '.glm'
    createGLM.write_GLM_file(self, agent, "main")
    
    if run_params.agent == "qlearn":
      for i in range(5):
        print "explore ", i
        agent.explore(self, run_params)

  def launch(self, agent):
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
    self.last_timestep_energy_used = 0.0
    self.hvac_load = 0.0
    self.heating_setpoint = agent.preferred_low_temp
    self.cooling_setpoint = agent.preferred_high_temp
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
        # debug
        # print "paused at ", sim_time
        # Need to do housekeeping due to GridLAB-D's syncing
        clock_delta = sim_time - self.last_pause_time
        secs = clock_delta.total_seconds()
        self.last_timestep_energy_used += self.hvac_load * secs * (1.0/3600)
        self.hvac_load = float(self.get_value("hvac_load"))
        # for new release: self.hvac_load = float(re.sub(r'[^\d.]+', '', self.get_value("hvac_load")))
        mode = self.get_value("system_mode")
        if (mode == "COOL") or (mode == "HEAT"):
          self.last_mode = mode
          # print "updated last_mode: ", last_mode
        self.last_pause_time = sim_time
        self.pause_time = sim_time + timedelta(seconds=1)
        # if (self.pause_time > self.new_timestep_start): # no longer think this makes sense...
        #   self.pause_time = self.new_timestep_start
        self.pause_string = util.datetimeTOstring(self.pause_time, self.timezone_short)
        self.pause_time = parser.parse(self.pause_string) # to take care of daylight savings issues
        if (sim_time >= self.new_timestep_start): # Simulation has been paused on a timestep transition
          self.sim_time = sim_time
          if (sim_time == self.start_control): # Simulation has been paused at the start of control, aka start of first timestep
            self.last_timestep_energy_used = 0.0
          # debug
          # print "new timestep! ", self.sim_time
          # print "energy used in last timestep = ", self.last_timestep_energy_used
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
        self.pause_time = parser.parse(self.pause_string)
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

  def update(self, agent):
    if (self.sim_time >= self.end_control):
      self.sim_complete = True
      return
    self.outdoor_temp = float(self.get_value("outdoor_temperature")[:-5])
    # for new release: self.outdoor_temp = float(re.sub(r'[^\d\+\-.]+', '', self.get_value("outdoor_temperature")[:-5]))
    self.indoor_temp = float(self.get_value("air_temperature")[:-5])
    # for new release: self.indoor_temp = float(re.sub(r'[^\d\+\-.]+', '', self.get_value("air_temperature")[:-5]))    
    self.current_timestep_start = self.new_timestep_start    
    self.new_timestep_start += timedelta(minutes=agent.timestep)

  def set_next_setpoints(self, new_heating_setpoint, new_cooling_setpoint):
    if new_heating_setpoint != self.heating_setpoint:
      self.heating_setpoint = new_heating_setpoint
      args_set_heat = ["wget", "http://localhost:6267/"+self.house_name+"/heating_setpoint="+str(self.heating_setpoint), "-q", "-O", "-"]
      cmd_set_heat = subprocess.Popen(args_set_heat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      cmd_set_heat.communicate()
      with open(self.heating_temps_file,'a') as f:
        fwriter = csv.writer(f)
        fwriter.writerow([util.datetimeTOstring(self.sim_time + timedelta(seconds=5), self.timezone_short), self.heating_setpoint])
    if new_cooling_setpoint != self.cooling_setpoint:
      self.cooling_setpoint = new_cooling_setpoint
      args_set_cool = ["wget", "http://localhost:6267/"+self.house_name+"/cooling_setpoint="+str(self.cooling_setpoint), "-q", "-O", "-"]
      cmd_set_cool = subprocess.Popen(args_set_cool, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      cmd_set_cool.communicate()
      with open(self.cooling_temps_file,'a') as f:
        fwriter = csv.writer(f)
        fwriter.writerow([util.datetimeTOstring(self.sim_time + timedelta(seconds=5), self.timezone_short), self.cooling_setpoint])

    # This should be the last thing to happen
    self.last_timestep_energy_used = 0.0
    args_set_pause = ["wget","http://localhost:6267/control/pauseat="+self.pause_string, "-q", "-O", "-"]
    cmd_set_pause = subprocess.Popen(args_set_pause, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_set_pause.communicate()

  def final_cleanup(self, run_params, agent):
    args_resume = ["wget", "http://localhost:6267/control/resume", "-O", "-"] 
    # "-O -" makes system not save output to a file
    # eventually will also want "-q" to not display output on console (helpful for now for debugging)
    cmd_resume = subprocess.call(args_resume) # subprocess.call will wait for call to finish before returning

    # Re-run, to measure comfort
    second_world = GldTempMeasWorld(run_params, agent)
    util.run_gld_reg(second_world.glmfile)

    # Test to compare HVAC usage in "real" run to that of the "comfort" run 
    # (comment when confident no large difference)
    results_file = run_params.run_name + "/" + run_params.run_name + "_results_second_run_" + run_params.agent + ".csv"
    with open(results_file, 'wb') as f:
      fwriter = csv.writer(f)
    util.assess_budget(second_world, agent, results_file, self.start_control, self.end_control)

class GldTempMeasWorld(World):
  def __init__(self, run_params, agent):
    # print "simple gld world!"
    self.house_name = 'house_' + run_params.run_name
    sim_file = run_params.run_name + '/' + run_params.run_name + '_sim_settings.txt'
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
    # debug (comment/uncomment line above):
    # self.end_control = self.start_control + timedelta(hours=15)
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
    createGLM.write_GLM_file(self, agent, "temps")

class GldPredictiveWorld(World):
  # Used only by the LookupAgent, for predictive runs
  def __init__(self, orig_world, timestep):
    self.run_name = orig_world.energy_use_file.split("/")[0]
    self.house_name = 'house_predictive_runs'
    self.timezone = orig_world.timezone
    self.tmyfile = orig_world.tmyfile
    self.house_size = orig_world.house_size
    self.heater_type = orig_world.heater_type
    self.sim_start_time = orig_world.sim_time
    self.sim_start_string = util.datetimeTOstring(self.sim_start_time, orig_world.timezone_short)
    self.sim_end_time = self.sim_start_time + timedelta(minutes = timestep)
    self.sim_end_string = util.datetimeTOstring(self.sim_end_time, orig_world.timezone_short)
    self.glmfile = self.run_name + "/predictive_runs_lookup.glm"
    self.energy_use_file = self.run_name + "/energy_use_for_predictions.csv"
    self.indoor_temp = orig_world.indoor_temp
    self.outdoor_temp = orig_world.outdoor_temp

class GldBaselineWorld:
  def __init__(self, run_params, agent):
    # print "initializing GldBaselineWorld"
    # self.ts_count = 0
    self.house_name = 'house_' + run_params.run_name
    sim_file = run_params.run_name + '/' + run_params.run_name + '_sim_settings.txt'
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
    self.end_control = self.start_control + timedelta(days = sum(self.n_days_in_months)) + timedelta(seconds = -1)
    # debug (comment/uncomment line above):
    # self.end_control = self.start_control + timedelta(hours=15)
    self.sim_end = self.end_control + timedelta(hours = 3)
    self.sim_end_string = util.datetimeTOstring(self.sim_end, self.timezone_short)

    # Format files needed
    for file_description in ['energy_use_file', 'indoor_temps_file']:
      file_name = run_params.run_name + '/' + run_params.run_name + '_' + file_description[:-5] + '_' + run_params.agent + '.csv'
      setattr(self, file_description, file_name)

    # Write GLM file
    self.glmfile = run_params.run_name + '/' + run_params.run_name + '_GLM_' + run_params.agent + '.glm'
    createGLM.write_GLM_file(self, agent, "baseline")

    # Set sim_complete to True to immediately escape main while loop in balance.py:
    self.sim_complete = True

  def launch(self, agent):
    util.run_gld_reg(self.glmfile)

  def is_new_timestep(self):
    return True

  def update(self, agent):
    pass

  def set_next_setpoints(self, new_heating_setpoint, new_cooling_setpoint):
    pass

  def final_cleanup(self, run_params, agent):
    pass

class EcobeeWorld(World):
  def __init__(self, run_params, agent):
    print "initializing Ecobee"
    # TODO
    # MUST DEFINE energy_use_file, indoor_temps_file, start_control, AND end_control! For final assessment

  def launch(self, agent):
    # TODO
    pass

  def is_new_timestep(self):
    # TODO
    pass

  def update(self, agent):
    # TODO
    pass

  def set_next_setpoints(self, new_heating_setpoint, new_cooling_setpoint):
    # TODO
    pass

  def final_cleanup(self, run_params, agent):
    # TODO
    pass
