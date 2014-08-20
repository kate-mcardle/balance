'''
A simple class to read in the run settings and dynamically create the 
appropriate world (GridLAB-D simulation or Ecobee) and agent, based
on the run settings.
'''

import sys
import csv
import re

import worlds
import agents

class Params:
  def __init__(self, run_name):
    self.run_name = run_name
    settings_file = self.run_name + '/' + self.run_name + '_settings.txt'
    with open(settings_file, 'rb') as f:
      r = csv.reader(f, delimiter=' ')
      self.world = r.next()[1]
      self.agent = r.next()[1]

  def initialize_agent(self):
    return getattr(self, 'initialize_%s_agent' % self.agent)()

  def initialize_lowest_cost_agent(self):
    return agents.LowestCostAgent(self)

  def initialize_highest_comfort_agent(self):
    return agents.HighestComfortAgent(self)

  def initialize_lookup_agent(self):
    return agents.LookupAgent(self)

  def initialize_qlearn_agent(self):
    return agents.QLearnAgent(self)

  def initialize_random_agent(self):
    return agents.RandomAgent(self)

  def initialize_world(self, agent):
    return getattr(self, 'initialize_%s' % self.world)(agent)

  def initialize_gld(self, agent):
    return worlds.GldWorld(self, agent)

  def initialize_gld_baseline(self, agent):
    return worlds.GldBaselineWorld(self, agent)

  def initialize_ecobee(self, agent):
    return worlds.EcobeeWorld(self, agent)