'''
This file contains a function, write_GLM_file, to create a .glm file for GridLAB-D, based on 
the world's and agent's specifications, as well as the type (purpose) of simulation.
'''

import sys

def write_GLM_file(world, agent, simType):
  with open(world.glmfile, 'wb') as glmfile:
    if simType == 'main':
      glmfile.write('#set pauseat=\'' + world.first_pause_at + '\'\n')

    glmfile.write('clock {')
    glmfile.write('\n\ttimezone ' + world.timezone + ';')
    glmfile.write('\n\tstarttime \'' + world.sim_start_string + '\';')
    glmfile.write('\n\tstoptime \'' + world.sim_end_string + '\';')
    glmfile.write('\n}')

    glmfile.write('\nmodule residential;\nmodule tape;\nmodule climate;')
    glmfile.write('\nmodule assert;')

    glmfile.write('\nobject climate {')
    glmfile.write('\n\ttmyfile ' + world.tmyfile + ';')
    glmfile.write('\n};')

    glmfile.write('\nobject house: {')
    glmfile.write('\n\tname "' + world.house_name + '";')
    glmfile.write('\n\tfloor_area ' + world.house_size + ';')
    glmfile.write('\n\tcooling_system_type ELECTRIC;')
    glmfile.write('\n\theating_system_type ' + world.heater_type + ';')

    if simType == "main":
      glmfile.write('\n\tcooling_setpoint ' + str(agent.preferred_high_temp) + ';')
      glmfile.write('\n\theating_setpoint ' + str(agent.preferred_low_temp) + ';')
      glmfile.write('\n\tobject player: {')
      glmfile.write('\n\t\tproperty floor_area;')
      glmfile.write('\n\t\tfile ' + world.floor_player_file + ';')
      glmfile.write('\n\t};')
      glmfile.write('\n\tobject assert {')
      glmfile.write('\n\t\ttarget floor_area;')
      glmfile.write('\n\t\trelation "==";')
      glmfile.write('\n\t\tvalue 1000;')
      glmfile.write('\n\t};')      
      glmfile.write('\n\tobject recorder: {')
      glmfile.write('\n\t\tproperty hvac_load, air_temperature, cooling_setpoint, heating_setpoint, outdoor_temperature, system_mode;')
      glmfile.write('\n\t\tfile ' + world.energy_use_file + ';')
      glmfile.write('\n\t};')
    elif simType == "temps":
      glmfile.write('\n\tcooling_setpoint ' + str(agent.preferred_high_temp) + ';')
      glmfile.write('\n\theating_setpoint ' + str(agent.preferred_low_temp) + ';')
      glmfile.write('\n\tobject player: {')
      glmfile.write('\n\t\tproperty floor_area;')
      glmfile.write('\n\t\tfile ' + world.floor_player_file + ';')
      glmfile.write('\n\t};')
      glmfile.write('\n\tobject assert {')
      glmfile.write('\n\t\ttarget floor_area;')
      glmfile.write('\n\t\trelation "==";')
      glmfile.write('\n\t\tvalue 1000;')
      glmfile.write('\n\t};')
      glmfile.write('\n\tobject player {')
      glmfile.write('\n\t\tproperty cooling_setpoint;')
      glmfile.write('\n\t\tfile ' + world.cooling_temps_file + ';')
      glmfile.write('\n\t};')
      glmfile.write('\n\tobject player {')
      glmfile.write('\n\t\tproperty heating_setpoint;')
      glmfile.write('\n\t\tfile ' + world.heating_temps_file + ';')
      glmfile.write('\n\t};')
      glmfile.write('\n\tobject recorder: {')
      glmfile.write('\n\t\tproperty hvac_load, air_temperature, cooling_setpoint, heating_setpoint, outdoor_temperature, system_mode;')
      glmfile.write('\n\t\tfile ' + world.energy_use_file + ';')
      glmfile.write('\n\t};')
      glmfile.write('\n\tobject recorder: {')
      glmfile.write('\n\t\tproperty air_temperature;')
      glmfile.write('\n\t\tfile ' + world.indoor_temps_file + ';')
      glmfile.write('\n\t\tinterval 60;')
      glmfile.write('\n\t};')
    elif simType == "pred":
      glmfile.write('\n\tcooling_setpoint ' + str(world.cooling_setpoint) + ';')
      glmfile.write('\n\theating_setpoint ' + str(world.heating_setpoint) + ';')
      glmfile.write('\n\tair_temperature ' + str(world.indoor_temp) + ';')
      glmfile.write('\n\tobject recorder: {')
      glmfile.write('\n\t\tproperty hvac_load;')
      glmfile.write('\n\t\tfile ' + world.energy_use_file + ';')
      glmfile.write('\n\t};')
    # TODO
    # elif simType == "min_cost":
    #   glmfile.write('\n\tcooling_setpoint ' + str(runParams.max_temp) + ';')
    #   glmfile.write('\n\theating_setpoint ' + str(runParams.min_temp) + ';')
    #   glmfile.write('\n\tobject recorder: {')
    #   glmfile.write('\n\t\tproperty hvac_load, air_temperature, cooling_setpoint, heating_setpoint, outdoor_temperature, system_mode;')
    #   glmfile.write('\n\t\tfile ' + runParams.energy_use_file + ';')
    #   glmfile.write('\n\t};')
    #   glmfile.write('\n\tobject recorder: {')
    #   glmfile.write('\n\t\tproperty air_temperature;')
    #   glmfile.write('\n\t\tfile ' + runParams.indoor_temps_file + ';')
    #   glmfile.write('\n\t\tinterval 60;')
    #   glmfile.write('\n\t};')
    # elif simType == "max_comfort":
    #   glmfile.write('\n\tcooling_setpoint ' + str(runParams.preferred_high_temp) + ';')
    #   glmfile.write('\n\theating_setpoint ' + str(runParams.preferred_low_temp) + ';')
    #   glmfile.write('\n\tobject recorder: {')
    #   glmfile.write('\n\t\tproperty hvac_load, air_temperature, cooling_setpoint, heating_setpoint, outdoor_temperature, system_mode;')
    #   glmfile.write('\n\t\tfile ' + runParams.energy_use_file + ';')
    #   glmfile.write('\n\t};')
    #   glmfile.write('\n\tobject recorder: {')
    #   glmfile.write('\n\t\tproperty air_temperature;')
    #   glmfile.write('\n\t\tfile ' + runParams.indoor_temps_file + ';')
    #   glmfile.write('\n\t\tinterval 60;')
    #   glmfile.write('\n\t};')

    glmfile.write('\n}')