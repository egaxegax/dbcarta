#!/usr/bin/env python
"""
Simple map.
"""

from __init__ import *
from dbcarta import *
from data.continents import *

root = Tk()
dw = dbCarta(root)

dw.loadCarta(CONTINENTS)
dw.loadCarta(dw.createMeridians())
dw.centerCarta()

root.mainloop()
