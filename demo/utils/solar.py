#!/usr/bin/env python
#-*- coding: utf8 -*-
"""
Solar System bodies computes by "Low precision formulae" algorithms.
See http://stjarnhimlen.se/comp/ppcomp.html.
"""

__version__ = "0.1"

import time, math, sys

D = math.degrees
R = math.radians
P1 = lambda x: x - math.floor(x/360.0)*360.0

def timeScale(Y, M, D, h=0, m=0, s=0):
    """Return day's fractions from epoch J2000.
    Y, M, D, h, m, s UT values."""
    return 367*Y - 7 * ( Y + (M+9)//12 ) // 4 + 275*M//9 + D - 730530 + (h * 3600 + m * 60 + s) / 86400.0

def rect2spheric(xe, ye, ze):
    """Convert rectangular to spherical coordinates.
    Return list `[lonecl,latecl]`. Rev. to spheric2rect.
    XE, YE, ZE rectagular coordinates.
    """
    return [ math.atan2( ye, xe ),
             math.atan2( ze, math.sqrt(xe*xe+ye*ye) ),
             math.sqrt(xe*xe+ye*ye+ze*ze) ]
    
def spheric2rect(lonecl, latecl, r=1):
    """Convert spherical to rectangular coordinates.
    Return list `[x,y,z]`.
    LONECL, LATECL, R longtitude, latitude and radii.
    """
    return [ r * math.cos(lonecl) * math.cos(latecl),
             r * math.sin(lonecl) * math.cos(latecl),
             r * math.sin(latecl) ]

def ecl2eq(xe, ye, ze, d):
    """Convert ecliptic rectangular heliocentric to equatorial rectangular geocentric coordinates.
    Return list `[x,y,z]`.
    XE, YE, ZE rectagular coordinates.
    D day's fractions from epoch."""    
    # obliquity of the ecliptic
    ecl = 23.4393 - 3.563E-7 * d
    return [ xe,
             ye * math.cos(R(ecl)) - ze * math.sin(R(ecl)),
             ye * math.sin(R(ecl)) + ze * math.cos(R(ecl)) ]

def eq2radec(xq, yq, zq):
    """Convert equatorial rectangulat geocentric to equatorial spherical geocentric coordinates.
    Return list `[ra,dec,r]`.
    XQ, YQ, ZQ rectangular coordinates."""
    return rect2spheric(xq, yq, zq)

def ecl_helio2geo(xe, ye, ze, r, d, precession_epoch=False):
    """Convert ecliptic rectangular heliocentric to ecliptic rectangular geocentric coordinates.
    Return list `[x,y,z]`. Use Sun.
    XE, YE, ZE rectagular coordinates.
    D day's fractions from epoch.
    PRECESSION_EPOCH epoch with fraction"""
    # ecliptic spheric helio
    lonecl, latecl, r = rect2spheric(xe, ye, ze)    
    if precession_epoch:
        # precession
        lon_corr = 3.82394E-5 * ( 365.2422 * ( precval - 2000.0 ) - d )
        lonecl += lon_corr        
        # correct ecliptic spheric helio
        xe, ye, ze = spheric2rect(lonecl, latecl, r)        
    # sun pos
    xs, ys, zs = Sun(d) 
    # ecliptic rect geocentric
    xg = xe + xs
    yg = ye + ys
    zg = ze
    
    return [xg, yg, zg]

def eclrect(N, i, w, a, e, M):
    """Return list `[x,y,z]` of ecliptic rectangular heliocentric (geocentric for Moon) coordiantes.
    N long asc. node (in degrees).
    i inclination (in degrees).
    w arg. of perigee (in degrees).
    a mean distance from Sun.
    e eccentricity.
    M mean anomaly."""
    # eccentric anomaly
    E0 = P1(M + (180/math.pi) * e * math.sin(R(M)) * ( 1.0 + e * math.cos(R(M)) ))
    E1 = P1(E0 - (E0 - (180/math.pi) * e * math.sin(R(E0)) - M) / (1 - e * math.cos(R(E0))))
    
    x = a * (math.cos(R(E1)) - e)
    y = a * math.sqrt(1 - e*e) * math.sin(R(E1))
    
    # distance and true anomaly 
    r = math.sqrt( x*x + y*y )
    v = math.atan2( y, x )
    
    return [ r * ( math.cos(R(N)) * math.cos(v+R(w)) - math.sin(R(N)) * math.sin(v+R(w)) * math.cos(R(i)) ),
             r * ( math.sin(R(N)) * math.cos(v+R(w)) + math.cos(R(N)) * math.sin(v+R(w)) * math.cos(R(i)) ),
             r * math.sin(v+R(w)) * math.sin(R(i)) ]

def Sun(d, precession=0):
    # orbital
    N = 0.0                             # (Long asc. node)
    i = 0.0                             # (Inclination)
    w = P1(282.9404 + 4.70935E-5 * d)  # (Arg. of perigee)
    a = 1.000000                        # (Mean distance)
    e = 0.016709 - 1.151E-9 * d          # (Eccentricity)
    M = P1(356.0470 + 0.9856002585 * d) # (Mean anomaly)
    
    # mean longitude
    L = P1(w + M)
    # eccentric anomaly
    E = P1(M + (180/math.pi) * e * math.sin(R(M)) * ( 1.0 + e * math.cos(R(M)) ))
    
    # ecliptic rect heliocentric
    xv = math.cos(R(E)) - e
    yv = math.sqrt(1.0 - e*e) * math.sin(R(E))

    # distance and true anomaly
    r = math.sqrt( xv*xv + yv*yv )
    v = math.atan2( yv, xv )

    # true longitude
    lon = v + R(w) + precession
    
    # ecliptic rect geocentric
    xe = r * math.cos(lon)
    ye = r * math.sin(lon)
    ze = 0.0

    return [xe, ye, ze]

def Moon(d):
    N = 125.1228 - 0.0529538083 * d
    i = 5.1454
    w = 318.0634 + 0.1643573223 * d
    a = 60.2666
    e = 0.054900
    M = 115.3654 + 13.0649929509 * d
        
    return eclrect(N, i, P1(w), a, e, P1(M))

def Mercury(d):
    N = 48.3313 + 3.24587E-5 * d
    i = 7.0047 + 5.00E-8 * d
    w = 29.1241 + 1.01444E-5 * d
    a = 0.387098
    e = 0.205635 + 5.59E-10 * d
    M = 168.6562 + 4.0923344368 * d

    xg, yg, zg = eclrect(N, i, P1(w), a, e, P1(M))
    r = math.sqrt( xg*xg+yg*yg+zg*zg )
    
    return [xg, yg, zg, r]

def Venus(d):
    N = 76.6799 + 2.46590E-5 * d
    i = 3.3946 + 2.75E-8 * d
    w = 54.8910 + 1.38374E-5 * d
    a = 0.723330
    e = 0.006773 - 1.302E-9 * d
    M = 48.0052 + 1.6021302244 * d

    xg, yg, zg = eclrect(N, i, P1(w), a, e, P1(M))
    r = math.sqrt( xg*xg+yg*yg+zg*zg )
    
    return [xg, yg, zg, r]

def Mars(d):
    N = 49.5574 + 2.11081E-5 * d
    i = 1.8497 - 1.78E-8 * d
    w = 286.5016 + 2.92961E-5 * d
    a = 1.523688
    e = 0.093405 + 2.516E-9 * d
    M = 18.6021 + 0.5240207766 * d
    
    xg, yg, zg = eclrect(N, i, P1(w), a, e, P1(M))
    r = math.sqrt( xg*xg+yg*yg+zg*zg )
    
    return [xg, yg, zg, r]

def Jupiter(d):
    N = 100.4542 + 2.76854E-5 * d
    i = 1.3030 - 1.557E-7 * d
    w = 273.8777 + 1.64505E-5 * d
    a = 5.20256
    e = 0.048498 + 4.469E-9 * d
    M = 19.8950 + 0.0830853001 * d

    xg, yg, zg = eclrect(N, i, P1(w), a, e, P1(M))
    r = math.sqrt( xg*xg+yg*yg+zg*zg )
    
    return [xg, yg, zg, r]

def Saturn(d):
    N = 113.6634 + 2.38980E-5 * d
    i = 2.4886 - 1.081E-7 * d
    w = 339.3939 + 2.97661E-5 * d
    a = 9.55475
    e = 0.055546 - 9.499E-9 * d
    M = 316.9670 + 0.0334442282 * d

    xg, yg, zg = eclrect(N, i, P1(w), a, e, P1(M))
    r = math.sqrt( xg*xg+yg*yg+zg*zg )
    
    return [xg, yg, zg, r]

def Uranus(d):
    N = 74.0005 + 1.3978E-5 * d
    i = 0.7733 + 1.9E-8 * d
    w = 96.6612 + 3.0565E-5 * d
    a = 19.18171 - 1.55E-8 * d
    e = 0.047318 + 7.45E-9 * d
    M = 142.5905 + 0.011725806 * d

    xg, yg, zg = eclrect(N, i, P1(w), a, e, P1(M))
    r = math.sqrt( xg*xg+yg*yg+zg*zg )
    
    return [xg, yg, zg, r]

def Neptune(d):
    N = 131.7806 + 3.0173E-5 * d
    i = 1.7700 - 2.55E-7 * d
    w = 272.8461 - 6.027E-6 * d
    a = 30.05826 + 3.313E-8 * d
    e = 0.008606 + 2.15E-9 * d
    M = 260.2471 + 0.005995147 * d

    xg, yg, zg = eclrect(N, i, P1(w), a, e, P1(M))
    r = math.sqrt( xg*xg+yg*yg+zg*zg )
    
    return [xg, yg, zg, r]

def Pluto(d):
    pass

if __name__ == '__main__':
    d = timeScale(1990, 4, 19)
    print('d', d)
    
    ra, dec, r = eq2radec(*ecl2eq(*Sun(d) + [d]))
    print('Sun', R(P1(D(ra))),dec)
    
    ra, dec, r = eq2radec(*ecl2eq(*Moon(d) + [d]))
    print('Moon', R(P1(D(ra))),dec)

    for p in ('Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'):       
        ra, dec, r = eq2radec(*ecl2eq(*ecl_helio2geo(*eval(p + "(d)") + [d]) + [d]))
        print(p, D(R(P1(D(ra)))),(dec))
