import sys
import csv
import re

def main(argv):
  output_file = argv[1]
  with open(output_file) as f:
    r = csv.reader(f)
    prev_row_hvac = '+0'
    prev_row_ts = ''
    last_ts = ''
    for row_header in r:
      match = re.search(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', row_header[0])
      if match:
        break
    for row in r:
      hvac = row[1]
      if (prev_row_hvac != '+0' and hvac != '+0'):
        if (last_ts == prev_row_ts):
          print "from ", prev_row_ts, " to ", row[0]
        last_ts = row[0]
      prev_row_ts = row[0]
      prev_row_hvac = hvac
    # with open(argv[2], 'wb') as f2:
    #   fwriter = csv.writer(f2)
    #   for row in r:
    #     fwriter.writerow([row[0], "1000"])

if __name__ == '__main__':
  main(sys.argv)