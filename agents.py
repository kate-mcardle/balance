'''
agents.py contains the various agents we have developed for balance. The Agent class is a base 
class with only one function inherited by its derived classes. Derived classes must implement
a constructor and update_state and get_next_setpoints methods.
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
from random import randint

import worlds
import createGLM
import util

class Agent:
  def __init__(self, run_params):
    '''
    Class constructor for the agent. Takes care of any setup for the specifications of the run.
    '''
    print "Didn't define --constructor-- for this derived class!"

  def update_state(self, world):
    '''
    Update's the agent's knowledge of the world state, based on the current world parameters, and 
    its own tracking such as the budget used.
    '''
    print "Didn't define --update_state-- for this derived class!"

  def get_next_setpoints(self, world):
    '''
    Determines and returns the next heating and cooling setpoints the agent should use 
    for the thermostat.
    '''
    print "Didn't define --get_next_setpoints-- for this derived class!"

  def read_settings(self, run_name):
    '''
    Reads and stores the specifications related to this agent for this run.
    '''
    settings_file = run_name + '/' + run_name + '_agent_settings.txt'
    with open(settings_file, 'rb') as f:
      r = csv.reader(f, delimiter=' ')
      self.elec_price = float(r.next()[1])
      self.timestep = int(r.next()[1])
      self.preferred_low_temp = int(r.next()[1])
      self.preferred_high_temp = int(r.next()[1])
      self.min_temp = int(r.next()[1])
      self.max_temp = int(r.next()[1])
      self.budgets = r.next()[1:]
    self.budgets = [float(b) for b in self.budgets]
    
    self.n_timesteps_in_day = 1440.0 / self.timestep # assumes a fixed timestep
    self.n_timesteps_passed = -1
    self.current_month_index = -1
    self.budget_month_used = 0.0
    self.budget_day_used = 0.0

class LowestCostAgent(Agent):
  def __init__(self, run_params):
    print "initializing lowest cost agent"
    self.read_settings(run_params.run_name)

  def update_state(self, world):
    pass

  def get_next_setpoints(self, world):
    return (self.min_temp, self.max_temp)

class HighestComfortAgent(Agent):
  def __init__(self, run_params):
    print "initializing highest comfort agent"
    self.read_settings(run_params.run_name)

  def update_state(self, world):
    pass

  def get_next_setpoints(self, world):
    return (self.preferred_low_temp, self.preferred_high_temp)

class LookupAgent(Agent):
  def __init__(self, run_params):
    print "initializing lookup agent"
    self.energy_estimate = {} # Key = (outdoor_temp, indoor_temp, energy), value = (heating_setpoint, cooling_setpoint)
    self.prediction_sim_file = run_params.run_name + '/for_lookup_predictions.csv'
    self.read_settings(run_params.run_name)

  def update_state(self, world):
    self.n_timesteps_passed += 1
    # If start of new day...
    if world.current_timestep_start.hour == 0 and world.current_timestep_start.minute == 0:
      # If also start of new month, reset the month's used budget to 0 and increment the current month index
      if world.current_timestep_start.day == 1:
        print "new month! ", world.sim_time 
        self.budget_month_used = 0.0
        self.current_month_index += 1
      else:
        self.budget_month_used += world.last_timestep_energy_used * self.elec_price
      # Reset the day's used budget to 0 and recalculate the coming day's budget
      print "new day ", world.sim_time
      self.budget_day_used = 0.0
      self.budget_day = (self.budgets[self.current_month_index] - self.budget_month_used) / (world.n_days_in_months[self.current_month_index] - world.current_timestep_start.day + 1.0)
      self.n_timesteps_passed = 0
    # If not the start of a new day, update the used portions of the budgets
    else:
      self.budget_month_used += world.last_timestep_energy_used * self.elec_price
      self.budget_day_used += world.last_timestep_energy_used * self.elec_price
    
    # Whether it's the start of a new day or not...
    if hasattr(self, "last_outdoor_temp"): # as long as it's not the very first timestep, add the last timestep to the energy estimate lookup table
      self.energy_estimate[(round(self.last_outdoor_temp, 0), round(self.last_indoor_temp, 0), round(world.last_timestep_energy_used, 2))] = (world.heating_setpoint, world.cooling_setpoint)
    self.budget_timestep = (self.budget_day - self.budget_day_used) / (self.n_timesteps_in_day - self.n_timesteps_passed)
    self.last_outdoor_temp = world.outdoor_temp
    self.last_indoor_temp = world.indoor_temp

  def get_energy_estimate(self, world):
    '''
    Estimates how much energy will be used in the next timestep, given the current world state, by 
    running a GridLAB-D simulation for the timestep. The world's .glm file includes the thermostat 
    heating and cooling setpoint, which remain constant over the course of the simulated timestep.
    '''
    createGLM.write_GLM_file(world, self, "pred")
    util.run_gld_reg(world.glmfile)
    energy_used = util.get_energy_used(world.energy_use_file, world.sim_start_time, world.sim_end_time)
    if (round(world.outdoor_temp, 0), round(world.indoor_temp, 0), round(energy_used, 2)) not in self.energy_estimate.keys():
      self.energy_estimate[(round(world.outdoor_temp, 0), round(world.indoor_temp, 0), round(energy_used, 2))] = (world.heating_setpoint, world.cooling_setpoint)
    return energy_used

  def get_next_setpoints(self, world):
    # debug
    # times = [parser.parse("2013-04-01 02:00:00 CST"), parser.parse("2013-04-01 05:00:00 CST"), parser.parse("2013-04-03 09:00:00 CST"), parser.parse("2013-05-01 08:00:00 CST"), parser.parse("2013-05-05 13:00:00 CST"), parser.parse("2013-06-03 11:00:00 CST"), parser.parse("2013-06-13 23:00:00 CST")]
    # if (world.sim_time in times):
    #   n = randint(0,1)*2-1
    #   return (world.heating_setpoint+n, world.cooling_setpoint+n)
    
    energy_budget = self.budget_timestep / (self.elec_price + 0.0)
    if energy_budget <= 0.0:
      heating_setpoint = self.min_temp
      cooling_setpoint = self.max_temp
    elif (round(world.outdoor_temp, 0), round(world.indoor_temp, 0), round(energy_budget, 2)) in self.energy_estimate.keys():
      print "table lookup successful"
      heating_setpoint, cooling_setpoint = self.energy_estimate[(round(world.outdoor_temp, 0), round(world.indoor_temp, 0), round(energy_budget, 2))]
    else:
      pred_world = worlds.GldPredictiveWorld(world, self.timestep)
      pred_world.heating_setpoint = self.preferred_low_temp
      pred_world.cooling_setpoint = self.preferred_high_temp
      if world.last_mode == "COOL": # need to cool
        for i in range(self.max_temp - self.preferred_high_temp):
          energy_used = self.get_energy_estimate(pred_world)
          if energy_used <= energy_budget:
            break
          pred_world.cooling_setpoint += 1
      else: # need to heat
        for i in range(self.preferred_low_temp - self.min_temp):
          energy_used = self.get_energy_estimate(pred_world)
          if energy_used <= energy_budget:
            break
          pred_world.heating_setpoint -= 1
      cooling_setpoint = pred_world.cooling_setpoint
      heating_setpoint = pred_world.heating_setpoint
    return (heating_setpoint, cooling_setpoint)

class QLearnAgent(Agent):
  def __init__(self, run_params):
    print "initializing qlearn agent"
    self.read_settings(run_params.run_name)
    # TODO

  def update_state(self, world):
    # TODO
    pas

  def get_next_setpoints(self, world):
    # TODO
    pass