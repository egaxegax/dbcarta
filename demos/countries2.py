#!/usr/bin/env python
"""
World countries in dialog.
"""

from __init__ import *
from countries import *

root = Tk()
create_tlist(root)
fill_tlist()

master = Toplevel()
dbcarta = create_dbcarta(master)
dbcarta.changeProject(203, centerof=[[0,0]])
dbcarta.loadCarta(CONTINENTS)
dbcarta.loadCarta(dbcarta.createMeridians())

master.mainloop()