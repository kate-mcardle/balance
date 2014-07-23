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

def datetimeTOstring(dt, tz): # TODO This function only works for the year 2013...how to make it general?
  dtstring = str(dt)[:19] + ' ' + tz
  # Daylight Savings Time (need to use CDT): 3/10/13 - 11/3/13
  cdt_start = parser.parse("2013-03-10 02:00:00 CST")
  cdt_end = parser.parse("2013-11-03 02:00:00 CST")
  if dt >= cdt_start and dt <= cdt_end:
    dtstring = dtstring[:-2] + 'DT'
  return dtstring

def get_last_second_of_month(dt, tz):
  year = dt.year
  month = dt.month
  dt_string = str(year) + "-" + str(month) + "-" + str(calendar.monthrange(year, month)[1]) + " 23:59:59 " + tz
  return parser.parse(dt_string)

def get_energy_used(use_file, start_calc, end_calc, timestamp_col = 0, hvac_load_col = 1):  
  kWh = 0
  with open(use_file) as f:
    r = csv.reader(f)
    for row_header in r:
      match = re.search(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', row_header[timestamp_col])
      if match:
        break
    if (parser.parse(row_header[timestamp_col]) < start_calc):
      for row in r:
        if (parser.parse(row[timestamp_col]) >= start_calc):
          break
      row1 = row
    else:
      row1 = row_header
    for row2 in r:
      if (parser.parse(row2[timestamp_col]) > end_calc):
        break
      if (float(row1[hvac_load_col]) > 0):
        start_time = parser.parse(row1[timestamp_col])
        end_time = parser.parse(row2[timestamp_col])
        td = end_time - start_time
        secs = td.total_seconds()
        kWh += float(row1[hvac_load_col].strip('+')) * secs * (1.0/3600)
      row1 = row2
  return kWh

def assess_budget(world, agent, results_file, start_assessment, end_assessment):
  n_months_elapsed = (end_assessment.year - start_assessment.year)*12 + end_assessment.month - start_assessment.month + 1
  start_of_month = start_assessment
  end_of_month = get_last_second_of_month(start_of_month, world.timezone_short)
  with open(results_file, 'a') as f:
    fwriter = csv.writer(f)
    fwriter.writerow(["BUDGET RESULTS"])
  for i in range(n_months_elapsed):
    energy_used = get_energy_used(world.energy_use_file, start_of_month, end_of_month)
    total_cost = energy_used*agent.elec_price
    dollar_deviation = total_cost - agent.budgets[i]
    percent_deviation = 100 * dollar_deviation / (agent.budgets[i] + 0.0)
    print "For " + str(start_of_month.month) + "/" + str(start_of_month.year) + "---------"
    print "energy used = ", energy_used
    print "budget was: ", agent.budgets[i]
    print "total cost = ", total_cost
    print "deviation, $ = ", dollar_deviation
    print "deviation, % = ", percent_deviation
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
  n_months_elapsed = (end_assessment.year - start_assessment.year)*12 + end_assessment.month - start_assessment.month + 1
  start_of_month = start_assessment
  end_of_month = get_last_second_of_month(start_of_month, world.timezone_short)
  with open(results_file, 'a') as f:
    fwriter = csv.writer(f)
    fwriter.writerow(["COMFORT RESULTS"])
  for i in range(n_months_elapsed):
    mins = 0
    degree_mins = 0
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
      for row2 in r:
        if (parser.parse(row2[timestamp_col]) > end_of_month):
          break
        if (float(row2[temp_col]) > (agent.preferred_high_temp + 1)):
          mins += 1
          degree_mins += float(row2[temp_col]) - agent.preferred_high_temp + 1
        elif (float(row2[temp_col]) < (agent.preferred_low_temp - 1)):
          mins += 1
          degree_mins += agent.preferred_low_temp - 1 - float(row2[temp_col])
    print "For " + str(start_of_month.month) + "/" + str(start_of_month.year) + "---------"
    print "minutes outside preferred range = ", mins
    n_days_in_month = end_of_month.day
    percent_mins = 100 * mins / (n_days_in_month * 24 * 60.0)
    print "percent of minutes outside preferred range = ", percent_mins
    print "degree-minutes outside preferred range = ", degree_mins
    with open(results_file, 'a') as f:
      fwriter = csv.writer(f)
      fwriter.writerow([str(start_of_month.month) + "/" + str(start_of_month.year) + ":"])
      fwriter.writerow(["minutes outside preferred range = ", mins])
      fwriter.writerow(["percent of minutes outside preferred range = ", percent_mins])
      fwriter.writerow(["degree-minutes outside preferred range = ", degree_mins])
    start_of_month = end_of_month + timedelta(seconds = 1)
    end_of_month = get_last_second_of_month(start_of_month, world.timezone_short)

def assess_performance(run_params, world, agent, start_assessment, end_assessment):
  results_file = run_params.run_name + "/" + run_params.run_name + "_results_" + run_params.agent + ".csv"
  with open(results_file, 'wb') as f:
    fwriter = csv.writer(f)
  assess_budget(world, agent, results_file, start_assessment, end_assessment)
  assess_comfort(world, agent, results_file, start_assessment, end_assessment)