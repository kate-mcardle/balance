import sys

def write_GLM_file(world, run_params, simType):
  with open(world.glmfile, 'wb') as glmfile:
    if simType == 'main':
      glmfile.write('#set pauseat=\'' + world.first_pause_at + '\'\n')

    glmfile.write('clock {')
    glmfile.write('\n\ttimezone ' + world.timezone + ';')
    glmfile.write('\n\tstarttime \'' + world.sim_start_string + '\';')
    glmfile.write('\n\tstoptime \'' + world.sim_end_string + '\';')
    glmfile.write('\n}')

    glmfile.write('\nmodule residential;\nmodule tape;\nmodule climate;')

    glmfile.write('\nobject climate {')
    glmfile.write('\n\ttmyfile ' + world.tmyfile + ';')
    glmfile.write('\n};')

    glmfile.write('\nobject house: {')
    glmfile.write('\n\tname "' + world.house_name + '";')
    glmfile.write('\n\tfloor_area ' + world.house_size + ';')
    glmfile.write('\n\tcooling_system_type ELECTRIC;')
    glmfile.write('\n\theating_system_type ' + world.heater_type + ';')

    if simType == "main":
      glmfile.write('\n\tcooling_setpoint ' + str(run_params.preferred_high_temp) + ';')
      glmfile.write('\n\theating_setpoint ' + str(run_params.preferred_low_temp) + ';')
      glmfile.write('\n\tobject player: {')
      glmfile.write('\n\t\tproperty floor_area;')
      glmfile.write('\n\t\tfile ' + world.floor_player_file + ';')
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
    # TODO
    # elif simType == "pred":
    #   glmfile.write('\n\tcooling_setpoint ' + str(runParams.pred_cooling_setpoint) + ';')
    #   glmfile.write('\n\theating_setpoint ' + str(runParams.pred_heating_setpoint) + ';')
    #   glmfile.write('\n\tair_temperature ' + str(runParams.pred_indoor_temp) + ';')
    #   glmfile.write('\n\tobject recorder: {')
    #   glmfile.write('\n\t\tproperty hvac_load;')
    #   glmfile.write('\n\t\tfile ' + runParams.pred_file + ';')
    #   glmfile.write('\n\t};')
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