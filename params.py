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
      self.elec_price = float(r.next()[1])
      self.timestep = int(r.next()[1])
      self.preferred_low_temp = int(r.next()[1])
      self.preferred_high_temp = int(r.next()[1])
      self.min_temp = int(r.next()[1])
      self.max_temp = int(r.next()[1])
      self.budget = float(r.next()[1])

  def initialize_world(self):
    return getattr(self, 'initialize_%s' % self.world)()

  def initialize_ecobee(self):
    print "initializing Ecobee"
    return worlds.EcobeeWorld(self)

  def initialize_gld(self):
    print "initializing GridLAB-D"
    return worlds.GldWorld(self)

  def initialize_agent(self):
    return getattr(self, 'initialize_%s_agent' % self.agent)()

  def initialize_lookup_agent(self):
    print "initializing lookup agent"
    return agents.LookupAgent()

  def initialize_qlearn_agent(self):
    print "initializing qlearning agent"
    return agents.QLearnAgent()