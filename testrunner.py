import sys
import importlib
from xsplicetest import Patch

tc = importlib.import_module(sys.argv[1])

patches = []
with open(sys.argv[1] + '.txt', "r") as f:
    for line in f:
        line = line.strip()
        if line:
            line = line.split(' ')
            patches.append(Patch(line[0], line[1]))

testcase = tc.Testcase(sys.argv[2], patches)
testcase.build()
try:
    testcase.run()
finally:
    testcase.cleanup()
