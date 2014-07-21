class Agent:
  pass

class LookupAgent(Agent):
  def __init__(self, run_params):
    print "lookup agent"
    self.energy_estimate = {} # Key = (outdoor_temp, indoor_temp, energy), value = (heating_setpoint, cooling_setpoint)
    self.prediction_sim_file = run_params.run_name + '/for_lookup_predictions.csv'

  def get_next_setpoints(self):
    # TODO
    return None, None

class QLearnAgent(Agent):
  def __init__(self):
    print "qlearn agent"
    # TODO

  def get_next_setpoints(self):
    # TODO
    pass