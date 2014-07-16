class World:
  def final_cleanup(self):
    print "final cleanup"

class EcobeeWorld(World):
  def __init__(self, run_params):
    print "ecobee world!"
    # TODO

  def run_first_time_step(self, run_params):
    # TODO
    pass

  def is_new_timestep(self):
    # TODO
    pass

  def update_state(self):
    # TODO
    pass

class GldWorld(World):
  def __init__(self, run_params):
    print "gld world!"
    self.house_name = 'house_' + run_params.run_name
    # TODO, including write GLM

  def run_first_time_step(self, run_params):
    # TODO
    pass

  def is_new_timestep(self):
    # TODO
    pass

  def update_state(self):
    # TODO
    pass
