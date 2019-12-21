"""
Init path to module dbCarta and demos.
"""

import sys, os

d = os.path.dirname(sys.argv[0])
if d: d = d + '/'
sys.path.insert(0, os.path.abspath(d))
sys.path.insert(0, os.path.abspath(d + '../'))
