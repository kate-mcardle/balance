class Agent:
  pass

class LookupAgent(Agent):
  def __init__(self, run_params):
    print "lookup agent"

    self.prediction_sim_file = run_params.run_name + '/for_lookup_predictions.csv'
    # TODO

  def set_next_setpoints(self):
    # TODO
    pass

class QLearnAgent(Agent):
  def __init__(self):
    print "qlearn agent"
    # TODO

  def set_next_setpoints(self):
    # TODO
    pass