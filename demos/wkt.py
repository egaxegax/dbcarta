#!/usr/bin/env python
"""
Well-Known Text (WKT) coordinates format usage.
"""

from __init__ import *
from dbcarta import *

root = Tk()
dbcarta = dbCarta(root)
dbcarta.changeProject(203, [[-76,80]])
holebg = dbcarta.mopt['.Water']['bg']

dbcarta.loadCartaWKT([('D1',"POLYGON( (-178 80,-178 70,-158 73,-158 77,-178 80) )",'D',None,None,None,'yellow')])
dbcarta.loadCartaWKT([('D2',"POLYGON( (-175 78,-175 72,-161 74,-161 76,-175 78) )",None,None,None,None,holebg)])
dbcarta.loadCartaWKT([('B1',"POLYGON( (-148 80,-148 70,-128 73,-142 75,-128 77,-148 80) )",'B',None,None,None,'red')])
dbcarta.loadCartaWKT([('B2',"POLYGON( (-145 78,-145 75.5,-138 77,-145 78) )",None,None,None,None,holebg)])
dbcarta.loadCartaWKT([('B3',"POLYGON( (-145 74,-145 71.5,-138 73,-145 74) )",None,None,None,None,holebg)])
dbcarta.loadCartaWKT([('C',"POLYGON( (-98 80,-118 83,-118 70,-98 73,-101 75,-115 73,-115 80,-101 78,-98 80) )",'C',None,None,None,'yellow')])
dbcarta.loadCartaWKT([('A1',"POLYGON( (-76 80,-86 70,-78 70,-77 74,-75 74,-74 70,-66 70,-76 80) )",None,None,None,None,'red')])
dbcarta.loadCartaWKT([('A2',"POLYGON( (-76 77,-77 75,-75 75,-76 77) )",None,None,None,None,holebg)])
dbcarta.loadCartaWKT([('R1',"POLYGON( (-58 80,-58 70,-53 70,-53 73,-44 70,-38 70,-52 75,-38 77,-58 80) )",'R',None,None,None,'yellow')])
dbcarta.loadCartaWKT([('R2',"POLYGON( (-55 78,-55 75.5,-48 77,-55 78) )",'',None,None,None,holebg)])
dbcarta.loadCartaWKT([('T',"POLYGON( (-28 80,-28 77,-20 77,-20 70,-12 70,-12 77,-4 77,-4 80,-28 80) )",'T',None,None,None,'red')])
dbcarta.loadCartaWKT([('A3',"POLYGON( (14 80,4 70,12 70,13 74,15 74,16 70,24 70,14 80) )",'A',None,None,None,'yellow')])
dbcarta.loadCartaWKT([('A4',"POLYGON( (14 77,13 75,15 75,14 77) )",'A',None,None,None,holebg)])
dbcarta.loadCarta(dbcarta.createMeridians())

dbcarta.slider.var.set(dbcarta.slider.get() + dbcarta.slider['resolution'] * 3)
dbcarta.scaleCarta()

root.mainloop()