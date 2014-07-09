class Params:
  def __init__(self, argv):
    # TODO
    self.world = argv[1]

  def initialize_world(self):
    if self.world == 'ECOBEE':
      self.initialize_ecobee()
    else:
      self.initialize_sim()

  def initialize_ecobee(self):
    print "initializing Ecobee"
    # TODO

  def initialize_sim(self):
    print "initializing GridLAB-D"
    # TODO
