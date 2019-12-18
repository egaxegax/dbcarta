"""
Init path to module dbCarta and demos.
"""

import sys, os

DEMOPATH = os.path.dirname(sys.argv[0])
if DEMOPATH: DEMOPATH = DEMOPATH + '/'
sys.path.insert(0, os.path.abspath(DEMOPATH))
sys.path.insert(0, os.path.abspath(DEMOPATH + '../'))
