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

  def initialize_lookup_agent(self):
    print "initializing lookup agent"
    return agents.LookupAgent(self)

  def initialize_qlearn_agent(self):
    print "initializing qlearning agent"
    return agents.QLearnAgent(self)


  def initialize_world(self, agent):
    return getattr(self, 'initialize_%s' % self.world)(agent)

  def initialize_gld(self, agent):
    print "initializing GridLAB-D"
    return worlds.GldWorld(self, agent)

  def initialize_ecobee(self, agent):
    print "initializing Ecobee"
    return worlds.EcobeeWorld(self, agent)