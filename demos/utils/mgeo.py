#!/usr/bin/env python
#-*- coding: utf8 -*-
"""
geofunc.
"""
import math

def lineNcircle(ma, r):
    """Intersect. line MA and circle R."""
    EPS = 1e-8
    # y=kx+e
    k = (ma[1][1] - ma[0][1])/(ma[1][0] - ma[0][0] + EPS)
    e = ma[1][1] - k * ma[1][0]
    # ax+bx+c=0
    a = -k; b = 1; c = -e
    x0 = -a*c/(a*a+b*b)
    y0 = -b*c/(a*a+b*b)
    if (c*c > r*r*(a*a+b*b)): # no points
        return
    elif (abs(c*c - r*r*(a*a+b*b)) < 0): # 1 point
        return ma[1]
    else: # 2 points
        d = r*r - c*c/(a*a+b*b)
        mult = math.sqrt(d / (a*a+b*b))
        ax = x0 + b * mult
        bx = x0 - b * mult
        ay = y0 - a * mult
        by = y0 + a * mult
        # closest
        r1 = math.sqrt((ma[0][0] - ax)*(ma[0][0] - ax) + (ma[0][1] - ay)*(ma[0][1] - ay))
        r2 = math.sqrt((ma[0][0] - bx)*(ma[0][0] - bx) + (ma[0][1] - by)*(ma[0][1] - by))
        if (r1 < r2):
            return [ ax, ay ]
        else:
            return [ bx, by ]
