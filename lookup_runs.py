import balance
from datetime import datetime

# For runtime tracking:
runs_start_time = datetime.now()
print 'starting runs at: ', runs_start_time

# print "AUS_prefersCool_bMin: lookup agent"
# balance.main([0,"AUS_prefersCool_bMin"])
# print "AUS_prefersCool_b1: lookup agent"
# balance.main([0,"AUS_prefersCool_b1"])
# print "AUS_prefersCool_b2: lookup agent"
# balance.main([0,"AUS_prefersCool_b2"])
# print "AUS_prefersCool_bMax: lookup agent"
# balance.main([0,"AUS_prefersCool_bMax"])

# print "AUS_prefersWarm_bMin: lookup agent"
# balance.main([0,"AUS_prefersWarm_bMin"])
# print "AUS_prefersWarm_b1: lookup agent"
# balance.main([0,"AUS_prefersWarm_b1"])
# print "AUS_prefersWarm_b2: lookup agent"
# balance.main([0,"AUS_prefersWarm_b2"])
# print "AUS_prefersWarm_bMax: lookup agent"
# balance.main([0,"AUS_prefersWarm_bMax"])

# print 'Austin runs finished at ', datetime.now()

# print "MPL_prefersCool_bMin: lookup agent"
# balance.main([0,"MPL_prefersCool_bMin"])
# print "MPL_prefersCool_b1: lookup agent"
# balance.main([0,"MPL_prefersCool_b1"])
# print "MPL_prefersCool_b2: lookup agent"
# balance.main([0,"MPL_prefersCool_b2"])
# print "MPL_prefersCool_bMax: lookup agent"
# balance.main([0,"MPL_prefersCool_bMax"])

# print "MPL_prefersWarm_bMin: lookup agent"
# balance.main([0,"MPL_prefersWarm_bMin"])
# print "MPL_prefersWarm_b1: lookup agent"
# balance.main([0,"MPL_prefersWarm_b1"])
# print "MPL_prefersWarm_b2: lookup agent"
# balance.main([0,"MPL_prefersWarm_b2"])
# print "MPL_prefersWarm_bMax: lookup agent"
# balance.main([0,"MPL_prefersWarm_bMax"])

# print 'Minneapolis runs finished at ', datetime.now()

# print "STL_prefersCool_bMin: lookup agent"
# balance.main([0,"STL_prefersCool_bMin"])
print "STL_prefersCool_b1: lookup agent"
balance.main([0,"STL_prefersCool_b1"])
print "STL_prefersCool_b2: lookup agent"
balance.main([0,"STL_prefersCool_b2"])
print "STL_prefersCool_bMax: lookup agent"
balance.main([0,"STL_prefersCool_bMax"])

print "STL_prefersWarm_bMin: lookup agent"
balance.main([0,"STL_prefersWarm_bMin"])
print "STL_prefersWarm_b1: lookup agent"
balance.main([0,"STL_prefersWarm_b1"])
print "STL_prefersWarm_b2: lookup agent"
balance.main([0,"STL_prefersWarm_b2"])
print "STL_prefersWarm_bMax: lookup agent"
balance.main([0,"STL_prefersWarm_bMax"])

print 'St. Louis runs finished at ', datetime.now()

print "SFO_prefersCool_bMin: lookup agent"
balance.main([0,"SFO_prefersCool_bMin"])
print "SFO_prefersCool_b1: lookup agent"
balance.main([0,"SFO_prefersCool_b1"])
print "SFO_prefersCool_b2: lookup agent"
balance.main([0,"SFO_prefersCool_b2"])
print "SFO_prefersCool_bMax: lookup agent"
balance.main([0,"SFO_prefersCool_bMax"])

print "SFO_prefersWarm_bMin: lookup agent"
balance.main([0,"SFO_prefersWarm_bMin"])
print "SFO_prefersWarm_b1: lookup agent"
balance.main([0,"SFO_prefersWarm_b1"])
print "SFO_prefersWarm_b2: lookup agent"
balance.main([0,"SFO_prefersWarm_b2"])
print "SFO_prefersWarm_bMax: lookup agent"
balance.main([0,"SFO_prefersWarm_bMax"])

print 'San Francisco runs finished at ', datetime.now()

runs_end_time = datetime.now()
print 'Time to complete: ', runs_end_time - runs_start_time

