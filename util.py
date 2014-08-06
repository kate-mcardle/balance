'''
This file contains several helper methods.
'''

import sys
import csv
import re
import copy
from datetime import datetime
from datetime import timedelta
from dateutil import parser
import calendar
import subprocess
import time

energy_row_tracker = 0

def datetimeTOstring(dt, tz): # TODO This function only works for the year 2013...how to make it general?
  '''
  Converts a python datetime object and timezone to a string that can be used by GridLAB-D.
  '''
  dtstring = str(dt)[:19] + ' ' + tz
  # Daylight Savings Time (need to use CDT): 3/10/13 - 11/3/13
  cdt_start = parser.parse("2013-03-10 02:00:00 CST")
  cdt_end = parser.parse("2013-11-03 02:00:00 CST")
  if dt >= cdt_start and dt <= cdt_end:
    dtstring = dtstring[:-2] + 'DT'
  return dtstring

def get_last_second_of_month(dt, tz):
  '''
  Returns a datetime object corresponding to the last second in the month of the datetime object 
  provided, in the timezone given.
  '''
  year = dt.year
  month = dt.month
  dt_string = str(year) + "-" + str(month) + "-" + str(calendar.monthrange(year, month)[1]) + " 23:59:59 " + tz
  return parser.parse(dt_string)

def get_energy_used(use_file, start_calc, end_calc, forBudget = False, timestamp_col = 0, hvac_load_col = 1):
  '''
  Returns the energy, in kWh, used from one datetime (start_calc) to a later datetime (end_calc), as 
  recorded in the csv file use_file. The two datetimes must be contained within the timespan of
  the use_file.
  '''
  global energy_row_tracker
  if not forBudget:
    energy_row_tracker = 0
  kWh = 0
  with open(use_file) as f:
    r = csv.reader(f)
    if energy_row_tracker == 0:
      for row_header in r:
        energy_row_tracker += 1
        match = re.search(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', row_header[timestamp_col])
        if match:
          break
    else:
      for i in range(energy_row_tracker):
        row_header = r.next()
    if (parser.parse(row_header[timestamp_col]) < start_calc):
      for row in r:
        energy_row_tracker += 1
        if (parser.parse(row[timestamp_col]) >= start_calc):
          break
      row1 = row
    else:
      row1 = row_header
    for row2 in r:
      energy_row_tracker += 1
      if (float(row1[hvac_load_col]) > 0):
        start_time = parser.parse(row1[timestamp_col])
        end_time = parser.parse(row2[timestamp_col])
        td = end_time - start_time
        secs = td.total_seconds()
        kWh += float(row1[hvac_load_col].strip('+')) * secs * (1.0/3600)
      if (parser.parse(row2[timestamp_col]) >= end_calc):
        break
      row1 = row2
  return kWh

def assess_budget(world, agent, results_file, start_assessment, end_assessment):
  '''
  Compares the cost of the energy used (as recorded in the world's energy_use_file) to 
  the user's desired budget, from the datetime start_assessment to datetime end_assessment. 
  Records the results to a csv file results_file. The two datetimes must be contained within 
  the timespan of the world's energy use file.
  '''
  global energy_row_tracker
  energy_row_tracker = 0
  n_months_elapsed = (end_assessment.year - start_assessment.year)*12 + end_assessment.month - start_assessment.month + 1
  start_of_month = start_assessment
  end_of_month = get_last_second_of_month(start_of_month, world.timezone_short)
  with open(results_file, 'a') as f:
    fwriter = csv.writer(f)
    fwriter.writerow(["BUDGET RESULTS"])
  for i in range(n_months_elapsed):
    energy_used = get_energy_used(world.energy_use_file, start_of_month, end_of_month, True)
    total_cost = energy_used*agent.elec_prices[start_of_month.month-1]
    dollar_deviation = total_cost - agent.budgets[i]
    percent_deviation = 100 * dollar_deviation / (agent.budgets[i] + 0.0)
    # print "For " + str(start_of_month.month) + "/" + str(start_of_month.year) + "---------"
    # print "energy used = ", energy_used
    # print "budget was: ", agent.budgets[i]
    # print "total cost = ", total_cost
    # print "deviation, $ = ", dollar_deviation
    # print "deviation, % = ", percent_deviation
    with open(results_file, 'a') as f:
      fwriter = csv.writer(f)
      fwriter.writerow([str(start_of_month.month) + "/" + str(start_of_month.year) + ":"])
      fwriter.writerow(["energy used:", energy_used])
      fwriter.writerow(["budget:", agent.budgets[i]])
      fwriter.writerow(["actual cost:", total_cost])
      fwriter.writerow(["$ deviation:", dollar_deviation])
      fwriter.writerow(["% deviation:", percent_deviation])
    start_of_month = end_of_month + timedelta(seconds = 1)
    end_of_month = get_last_second_of_month(start_of_month, world.timezone_short)

def assess_comfort(world, agent, results_file, start_assessment, end_assessment, timestamp_col = 0, temp_col = 1):
  '''
  Compares the indoor temperatures (as recorded in the world's indoor_temps_file to the user's 
  preferred temperatures, from the datetime start_assessment to datetime end_assessment. 
  Records the results to a csv file results_file. The two datetimes must be contained within 
  the timespan of the world's energy use file.
  '''
  n_months_elapsed = (end_assessment.year - start_assessment.year)*12 + end_assessment.month - start_assessment.month + 1
  start_of_month = start_assessment
  end_of_month = get_last_second_of_month(start_of_month, world.timezone_short)
  with open(results_file, 'a') as f:
    fwriter = csv.writer(f)
    fwriter.writerow(["COMFORT RESULTS"])
  with open(world.indoor_temps_file) as f:
    r = csv.reader(f)
    for row_header in r:
      match = re.search(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', row_header[timestamp_col])
      if match:
        break
    if (parser.parse(row_header[timestamp_col]) < start_of_month):
      for row in r:
        if (parser.parse(row[timestamp_col]) >= start_of_month):
          break
      row1 = row
    else:
      row1 = row_header
    mins = {i:0 for i in range(n_months_elapsed)}
    degree_mins = {i:0 for i in range(n_months_elapsed)}
    percent_mins = {}
    months = {}
    for i in range(n_months_elapsed):
      months[i] = str(start_of_month.month) + "/" + str(start_of_month.year)
      for row2 in r:
        if (float(row1[temp_col]) > (agent.preferred_high_temp + 1)):
          mins[i] += 1
          degree_mins[i] += float(row1[temp_col]) - agent.preferred_high_temp + 1
        elif (float(row1[temp_col]) < (agent.preferred_low_temp - 1)):
          mins[i] += 1
          degree_mins[i] += agent.preferred_low_temp - 1 - float(row1[temp_col])
        row1 = row2
        if (parser.parse(row2[timestamp_col]) >= end_of_month):
          break
      n_days_in_month = end_of_month.day
      percent_mins[i] = 100 * mins[i] / (n_days_in_month * 24 * 60.0)
      start_of_month = end_of_month + timedelta(seconds = 1)
      end_of_month = get_last_second_of_month(start_of_month, world.timezone_short)
  with open(results_file, 'a') as f:
    fwriter = csv.writer(f)
    for i in range(n_months_elapsed):
      # print "For " + months[i] + "---------"
      # print "minutes outside preferred range = ", mins[i]
      # print "percent of minutes outside preferred range = ", percent_mins[i]
      # print "degree-minutes outside preferred range = ", degree_mins[i]
      fwriter.writerow([months[i] + ":"])
      fwriter.writerow(["minutes outside preferred range = ", mins[i]])
      fwriter.writerow(["percent of minutes outside preferred range = ", percent_mins[i]])
      fwriter.writerow(["degree-minutes outside preferred range = ", degree_mins[i]])

def assess_performance(run_params, world, agent, start_assessment, end_assessment):
  results_file = run_params.run_name + "/" + run_params.run_name + "_results_" + run_params.agent + ".csv"
  with open(results_file, 'wb') as f:
    fwriter = csv.writer(f)
  b_start = datetime.now()
  print 'starting budget assessment at ', b_start
  assess_budget(world, agent, results_file, start_assessment, end_assessment)
  b_end = datetime.now()
  print 'ending budget assessment at ', b_end
  print 'time to do budget assessment = ', b_end - b_start
  assess_comfort(world, agent, results_file, start_assessment, end_assessment)
  print 'ending comfort assessment at ', datetime.now()
  print 'time to do comfort assessment = ', datetime.now() - b_end

def run_gld_reg(glmfile):
  '''
  Runs a GridLAB-D simulation (not in server mode) using the provided .glm file.
  '''
  args_reg = ["gridlabd", glmfile]
  cmd_reg = subprocess.Popen(args_reg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  cmd_out, cmd_err = cmd_reg.communicate()
  if ("ERROR" in cmd_err) or ("FATAL" in cmd_err):
    print "GridLAB-D error in regular (non-server) simulation!"
    print cmd_err
    exit()