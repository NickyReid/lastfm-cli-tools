import os
import shutil
from lasthop import lasthop

for i in range(5):
    print "single process:"
    lasthop.go()
    shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + '/users/')