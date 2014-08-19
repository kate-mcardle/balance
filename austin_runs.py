import balance
from datetime import datetime

# For runtime tracking:
runs_start_time = datetime.now()
print 'starting runs at: ', runs_start_time

print "AUS_prefersCool_b1: lookup agent"
balance.main([0,"AUS_prefersCool_b1"])
print "AUS_prefersCool_b2: lookup agent"
balance.main([0,"AUS_prefersCool_b2"])
print "AUS_prefersCool_bMax: lookup agent"
balance.main([0,"AUS_prefersCool_bMax"])

print "AUS_prefersWarm_bMin: lookup agent"
balance.main([0,"AUS_prefersWarm_bMin"])
print "AUS_prefersWarm_b1: lookup agent"
balance.main([0,"AUS_prefersWarm_b1"])
print "AUS_prefersWarm_b2: lookup agent"
balance.main([0,"AUS_prefersWarm_b2"])
print "AUS_prefersWarm_bMax: lookup agent"
balance.main([0,"AUS_prefersWarm_bMax"])

runs_end_time = datetime.now()
print 'Austin runs finished at ', runs_end_time
print 'Time to complete: ', runs_end_time - runs_start_time

