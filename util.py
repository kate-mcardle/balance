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