# This is an agent-independent framework for controlling a residential thermostat, 
# either in the real world (eg Ecobee) or in simulation (eg GridLAB-D)

import sys

import params

def main(argv):
  run_params = params.Params(argv)
  run_params.initialize_world()

  # Run first time step separately (TODO: is it necessary for this to be separate? probably...)
  run_first_time_step(run_params) # TODO

  # LOOP for each time step until end time is reached, if applicable
  while is_new_time_step:
    is_new_time_step = False


if __name__ == '__main__':
  main(sys.argv)