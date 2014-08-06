import balance
from datetime import datetime

# For runtime tracking:
runs_start_time = datetime.now()
print 'starting runs at: ', runs_start_time

print "AUS_prefersCool_bMin: lowest_cost baseline agent"
balance.main([0,"AUS_prefersCool_bMin"])
print "AUS_prefersCool_bMax: highest_comfort baseline agent"
balance.main([0,"AUS_prefersCool_bMax"])
print "AUS_prefersWarm_bMin: lowest_cost baseline agent"
balance.main([0,"AUS_prefersWarm_bMin"])
print "AUS_prefersWarm_bMax: highest_comfort baseline agent"
balance.main([0,"AUS_prefersWarm_bMax"])

print 'Austin runs finished at ', datetime.now()

print "MPL_prefersCool_bMin: lowest_cost baseline agent"
balance.main([0,"MPL_prefersCool_bMin"])
print "MPL_prefersCool_bMax: highest_comfort baseline agent"
balance.main([0,"MPL_prefersCool_bMax"])
print "MPL_prefersWarm_bMin: lowest_cost baseline agent"
balance.main([0,"MPL_prefersWarm_bMin"])
print "MPL_prefersWarm_bMax: highest_comfort baseline agent"
balance.main([0,"MPL_prefersWarm_bMax"])

print 'Minneapolis runs finished at ', datetime.now()

print "STL_prefersCool_bMin: lowest_cost baseline agent"
balance.main([0,"STL_prefersCool_bMin"])
print "STL_prefersCool_bMax: highest_comfort baseline agent"
balance.main([0,"STL_prefersCool_bMax"])
print "STL_prefersWarm_bMin: lowest_cost baseline agent"
balance.main([0,"STL_prefersWarm_bMin"])
print "STL_prefersWarm_bMax: highest_comfort baseline agent"
balance.main([0,"STL_prefersWarm_bMax"])

print 'St. Louis runs finished at ', datetime.now()

print "SFO_prefersCool_bMin: lowest_cost baseline agent"
balance.main([0,"SFO_prefersCool_bMin"])
print "SFO_prefersCool_bMax: highest_comfort baseline agent"
balance.main([0,"SFO_prefersCool_bMax"])
print "SFO_prefersWarm_bMin: lowest_cost baseline agent"
balance.main([0,"SFO_prefersWarm_bMin"])
print "SFO_prefersWarm_bMax: highest_comfort baseline agent"
balance.main([0,"SFO_prefersWarm_bMax"])

runs_end_time = datetime.now()
print 'San Francisco runs finished at ', datetime.now()
print 'Time to complete: ', runs_end_time - runs_start_time

