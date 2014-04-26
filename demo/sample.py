#!/usr/bin/env python
#-*- coding: utf8 -*-
"""
Simple map.
"""

from __init__ import *
from dbcarta import *
from demodata.continents import *

root = Tk()
dw = dbCarta(root)

dw.loadCarta(CONTINENTS)
dw.loadCarta(dw.createMeridians())
dw.centerCarta()

root.mainloop()
