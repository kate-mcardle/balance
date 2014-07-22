'''
This is an agent-independent framework for controlling a residential thermostat, 
either in the real world (eg Ecobee) or in simulation (eg GridLAB-D)

To run: python balance.py <run name>

Required in the directory from which the script is run:
- TMY2 file, if using GridLAB-D
- A directory labeled with the run name
- Inside the run directory must be a settings input file, titled <run_name>_settings.txt.
- Inside the run directory must be a simulation input file, if using GridLAB-D, titled <run_name>_sim.txt

For example, for the run titled "run_1", there must be a directory called "run_1", and inside that directory must be 
a settings file called "run_1_settings.txt".

Info needed from settings input file:
  world (gld or ecobee)
  agent (lookup or qlearn)
  electricity_price ($ per kWh)
  timestep (minutes; must be a factor of 1440, number of minutes in a day)
  preferred_low_temp
  preferred_high_temp
  min_temp
  max_temp
  budget (comma separated list for each month)

Info needed from sim input file:
  start_year (YYYY)
  start_month (mm)
  n_months
  timezone (eg CST+6CDT)
  tmyfilename
  house_size (sq ft)
  heater_type (RESISTANCE for electric, or GAS)

'''

import sys
from datetime import datetime
from pprint import pprint # for debugging

import params
import worlds
import agents
import util

def main(argv):
  run_params = params.Params(argv[1])
  world = run_params.initialize_world()
  pprint (vars(world))
  agent = run_params.initialize_agent()

  # For runtime tracking:
  starttime = datetime.now()
  print 'starting world at: ', starttime

  # Bring world to start of control
  world.launch(run_params)

  # LOOP for each time step until end time is reached, if applicable
  while True:
    if world.is_new_timestep():
      world.update_state(run_params)
      heating_setpoint, cooling_setpoint = agent.get_next_setpoints(world)
      world.set_next_setpoints(heating_setpoint, cooling_setpoint)
    if world.sim_complete:
      break

  world.final_cleanup(run_params)
  # For runtime tracking:
  endtime = datetime.now()
  print 'world stopped at ', endtime
  print 'time to run: ', endtime-starttime
  
  util.assess_performance(run_params, world, world.start_control, world.end_control)

if __name__ == '__main__':
  main(sys.argv)