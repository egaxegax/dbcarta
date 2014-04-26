#!/usr/bin/env python
"""
Draw stars, planets on dbCarta.
Algorithms and stars data are taken from Marble Project at http://edu.kde.org/marble.
Solar System bodies are calculated by "Low precision formulae" issue at http://stjarnhimlen.se/comp/ppcomp.html. 
Sattelite's orbit computes by sgp4 module.
"""

__version__ = "0.5"

import math, sys
import calendar, datetime, time
from __init__ import *
from dbcarta import *
from demodata.continents import *
from demodata.constellations import *
from demodata.stars import *
from demodata.tledata import *
from utils.solar import *
from utils.mgeo import *
from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv

class Qn:
    """Spherical transformations."""
    @staticmethod
    def fromEuler(pitch, yaw, roll):
        cPhi = math.cos(0.5 * pitch)
        cThe = math.cos(0.5 * yaw)
        cPsi = math.cos(0.5 * roll)

        sPhi = math.sin(0.5 * pitch)
        sThe = math.sin(0.5 * yaw)
        sPsi = math.sin(0.5 * roll)

        w = cPhi * cThe * cPsi + sPhi * sThe * sPsi
        x = sPhi * cThe * cPsi - cPhi * sThe * sPsi
        y = cPhi * sThe * cPsi + sPhi * cThe * sPsi
        z = cPhi * cThe * sPsi - sPhi * sThe * cPsi

        return [w, x, y, z]
    @staticmethod
    def toMatrix(qpos):
        vw, vx, vy, vz = qpos
        m = []

        xy = vx * vy
        yy = vy * vy
        zw = vz * vw

        xz = vx * vz
        yw = vy * vw
        zz = vz * vz

        m.append([1.0 - 2.0 * (yy + zz), 2.0 * (xy + zw), 2.0 * (xz - yw), 0.0])

        xx = vx * vx
        xw = vx * vw
        yz = vy * vz

        m.append([2.0 * (xy - zw), 1.0 - 2.0 * (xx + zz), 2.0 * (yz + xw), 0.0])
        m.append([2.0 * (xz + yw), 2.0 * (yz - xw), 1.0 - 2.0 * (xx + yy), 0.0])

        return m
    @staticmethod
    def rotateAroundAxis(centerof, m):
        vw, vx, vy, vz = centerof

        x =  m[0][0] * vx + m[1][0] * vy + m[2][0] * vz
        y =  m[0][1] * vx + m[1][1] * vy + m[2][1] * vz
        z =  m[0][2] * vx + m[1][2] * vy + m[2][2] * vz

        return [1.0, x, y, z]
    @staticmethod
    def inverse(qpos):
        vw, vx, vy, vz = qpos
        inverse = [vw, -vx, -vy, -vz]
        return Qn.normalize(inverse)
    @staticmethod
    def length(qpos):
        vw, vx, vy, vz = qpos
        return math.sqrt(vw * vw + vx * vx + vy * vy + vz * vz)
    @staticmethod
    def normalize(qpos):
        vw, vx, vy, vz = qpos
        v = 1.0 / Qn.length(qpos)
        return [vw * v, vx * v, vy * v, vz * v]
    @staticmethod
    def fromSpherical(lon, lat):
        w = 0.0
        x = math.cos(lat) * math.sin(lon)
        y = math.sin(lat)
        z = math.cos(lat) * math.cos(lon)
        return [w, x, y, z]
    @staticmethod
    def gregorianToJulian(y, m, d):
        if (y <= 99):
            y += 1900
        if (m > 2):
            m -= 3
        else:
            m += 9
            y -= 1
        c = y
        c //= 100
        ya = y - 100*c
        return 1721119 + d + (146097*c)//4 + (1461*ya)//4 + (153*m+2)//5
    @staticmethod
    def siderealTime(gmtm):
        """Greenwich mean sidereal time in hours (0..24)."""
        y, m, d = gmtm[:3]
        mjdUtc = Qn.gregorianToJulian(y, m, d)

        h, m, s = gmtm[3:6]
        offsetUtcSecs = h * 3600 + m * 60 + s
        d_days = mjdUtc - 2451545.5
        d = d_days + ( offsetUtcSecs / ( 24.0 * 3600 ) )

        gmst = 18.697374558 + 24.06570982441908 * d
        return gmst - int( gmst / 24.0 ) * 24.0

class Starry:
    """Render stars, planets, sattelites."""
    gmtm = time.gmtime(time.time()) # UTC date/time set

    def initSky(self):
        viewport_x, viewport_y = dbcarta.sizeOf()
        self.vx, self.vy = viewport_x * dbcarta.slider.var.get(), viewport_y * dbcarta.slider.var.get()
        self.vx1, self.vy1 = viewport_x * dbcarta.slider['resolution'], viewport_y * dbcarta.slider['resolution']

        self.left, self.right = [self.vx * x for x in dbcarta.dw.xview()]
        self.top, self.bottom = [self.vy * y for y in dbcarta.dw.yview()]

        center_x, center_y = dbcarta.centerOf()[0]
        cx, cy = math.radians(center_x), math.radians(center_y)

        gmst = Qn.siderealTime( self.gmtm )
        skyRotationAngle = gmst / 12.0 * math.pi

        skyAxis = Qn.fromEuler(-cy, cx + skyRotationAngle, 0.0)
        self.skyAxisMatrix = Qn.toMatrix(Qn.inverse(skyAxis))

        self.earthRadiusKm = 6378.136
        self.earthRadius = 180 / math.pi * dbcarta.delta * dbcarta.slider.var.get()
        self.skyRadius = 0.6 * sqrt(self.vx * self.vx + self.vy * self.vy)

        dbcarta.dw.config(bg=rgb(17,17,96))
        # viewport border
        dbcarta.dw.create_rectangle(0, 0, self.vx, self.vy, 
                                    outline=rgb(17,17,196), dash=(10,1),
                                    tags=('.vpBorder', 'Line'))

    def calcSkyPos(self, ra, de, darkhide=True, outhide=True):
        """RA, DEC convert to points."""
        qpos = Qn.fromSpherical(ra, de)
        w, qx, qy, qz = Qn.rotateAroundAxis(qpos, self.skyAxisMatrix)

        if qz > 0:
            return

        earthCenteredX = qx * self.skyRadius
        earthCenteredY = qy * self.skyRadius

        # dark side
        if ( darkhide and (qz < 0 and ((earthCenteredX * earthCenteredX + earthCenteredY * earthCenteredY) < (self.earthRadius * self.earthRadius))) ):
            return

        x = (self.vx / 2.0 + self.skyRadius * qx)
        y = (self.vy / 2.0 - self.skyRadius * qy)

        # outside visible
        if ( outhide and ((x < self.left or x >= self.right) or (y < self.top or y >= self.bottom)) ):
            return

        return [x, y]

    def clns(self, mtag, data=[]):
        """Render constellations on map."""
        if dbcarta.isSpherical():
            for i in range(0, len(data), 2):
                pos1 = self.calcSkyPos(data[i][0], data[i][1], False, False)
                pos2 = self.calcSkyPos(data[i+1][0], data[i+1][1], False, False)

                if pos1 and pos2:
                    pts = pos1 + pos2
                else:
                    continue

                color = rgb(84,84,120)

                dbcarta.dw.create_line(pts,
                                       fill=color,
                                       tags=(mtag + str(i), 'Line', mtag))

    def stars(self, mtag, data=[]):
        """Render body on map.
        DATA list of list `[ra, de, mag, nbody, label]`.
        DARKHIDE, OUTHIDE."""
        if dbcarta.isSpherical():
            for i, body in enumerate(data):
                dd = dict([[k,v] for k, v in enumerate(body)])
                ra, de = [dd[0], dd[1]]
                pos = self.calcSkyPos(ra, de)

                if not pos:
                    continue

                x, y, = pos
                mag = dd.get(2, 10)
                nbody = dd.get(3, i)
                label = dd.get(4, '')
                color = dd.get(5, 'white')
                labelcolor = dd.get(6, rgb(155,155,200))

                # star point size by magitude
                if ( mag < -1 ): size = 7
                elif ( mag < 0 ): size = 6
                elif ( mag < 1 ): size = 5
                elif ( mag < 2 ): size = 4
                elif ( mag < 3 ): size = 3
                elif ( mag < 4 ): size = 2
                elif ( mag < 5 ): size = 1
                else: size = 0

                if label:
                    dbcarta.dw.create_text([x, y],
                                           fill=labelcolor, 
                                           text=_(label), anchor='sw',
                                           tags=('.' + mtag + str(nbody), mtag))
                if (len(body) > 5): # solar
                    dbcarta.dw.create_oval(x-size/2.0, y-size/2.0, x+size/2.0, y+size/2.0,
                                           outline=color, fill=color,
                                           tags=(mtag + str(nbody), 'DotPort', mtag))
                else:               # stars
                    dbcarta.dw.create_arc(x-size/2.0, y-size/2.0, x+size/2.0, y+size/2.0,
                                           outline=color, fill=color,
                                           tags=(mtag + str(nbody), 'DotPort', mtag))
                dbcarta.usercl(mtag + str(nbody), {'coords': [['HD',nbody],['label',_(label)],['ra',ra],['dec',de],['mag',mag]]})

    def sat(self, mtag, tledata=[]):
        """Render satellite's orbit (by whorl) on map.
        TLEDATA list of `[sat, line1, line2]`."""
        if dbcarta.isSpherical():
            for label, line1, line2 in tledata:
                satellite = twoline2rv(line1, line2, wgs84)
                ps = 2.0 * math.pi * 180/satellite.no
                utc1 = utc2 = datetime.datetime(*self.gmtm[:6])
                # by 2 mean motion ago
                delta = datetime.timedelta(0, ps)
                step = delta.total_seconds() / 200.0
                i = 0
                while (utc1 - utc2 < delta):
                    pos, vel = satellite.propagate(*utc2.timetuple()[:6])
                    utc2 = utc2 - datetime.timedelta(0, step)
                    xe, ye, ze = pos
                    ra, dec, r = rect2spheric(*pos) 
                    re = math.sqrt(xe*xe + ye*ye + ze*ze)

                    qpos = [0, ye/re, ze/re, xe/re] # rotate axis
                    w, qx, qy, qz = Qn.rotateAroundAxis(qpos, self.skyAxisMatrix)                    
                    skyRadius = self.earthRadius * re / self.earthRadiusKm

                    earthCenteredX = qx * skyRadius
                    earthCenteredY = qy * skyRadius

                    if ( qz < 0 and ( (earthCenteredX * earthCenteredX + earthCenteredY * earthCenteredY) < (self.earthRadius * self.earthRadius) ) ):
                        continue

                    x = (self.vx / 2.0 + skyRadius * qx)
                    y = (self.vy / 2.0 - skyRadius * qy)

                    #if ( (x < self.left or x >= self.right) or (y < self.top or y >= self.bottom) ):
                    #    continue

                    if not i: size = 7
                    else: size = 1

                    color = rgb(100,100,220)
                    labelcolor = rgb(200,200,170)

                    if not i: color = labelcolor

                    dbcarta.dw.create_oval(x-size/2.0, y-size/2.0, x+size/2.0, y+size/2.0,
                                           outline=color, fill=color,
                                           tags=(mtag + label, 'DotPort', mtag))
                    if not i:
                        dbcarta.dw.create_text([x, y], 
                                               fill=labelcolor,
                                               text=label, anchor='sw',
                                               tags=('.' + mtag + label, mtag))
                        dbcarta.usercl(mtag + label, {'coords': [['n',label],['ra',ra],['dec',dec]]})
                    i += 1

def renderSat():
    """Render sat tracs."""
    if dbcarta.isSpherical():
        dbcarta.dw.delete('iss')
        starry.sat( 'iss', TLEDATA[:3] )
    else:
        dbcarta.dw.delete('solar', 'stars', 'clns', 'cnts', 'iss')
        dbcarta.dw.config(bg=rgb(186,196,205))

def renderSky():
    """Render sky bodies."""
    # calc solar bodies pos.
    solar = []
    d = timeScale(*starry.gmtm[:6])
    ra, dec, r = eq2radec(*ecl2eq(*Sun(d) + [d]))
    solar += [[ra, dec, -26, 'Sun', 'Sun', 'yellow', 'yellow']]
    ra, dec, r = eq2radec(*ecl2eq(*Moon(d) + [d]))
    solar += [[ra, dec, -16, 'Moon', 'Moon', 'lightgray', 'lightgray']]
    for p in ('Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'):
        ra, dec, r = eq2radec(*ecl2eq(*ecl_helio2geo(*eval(p + "(d)") + [d]) + [d]))
        solar += [[ra, dec, 2, p, p, 'gray', rgb(255,155,128)]]

    dbcarta.dw.delete('solar', 'stars', 'clns', 'cnts')
    starry.initSky()
    starry.stars( 'solar', solar )
    starry.stars( 'stars', STARS )
    starry.clns( 'clns', CLNS )
    starry.stars( 'cnts', [cnt + ['', rgb(0,200,0)] for cnt in CNTS] )

    cx, cy = dbcarta.centerOf()[0]
    centerof = ( math.degrees(P(math.radians(cx), math.pi)),
                 math.degrees(P(math.radians(cy), math.pi/2.0)) * [-1, 1][math.cos(math.radians(cy)) > 0] )
    tmsg_var.set( 'X %s Y %s ' % centerof +
                  'T %s-%s-%s %s:%s:%s' % starry.gmtm[:6] )

def setTime():
    """Set UTC."""
    try:
        msg = [ _('Type date/time in format') + ' "Y-M-D h:m:s":',
              "(" + _('set blank to use current UTC time') + ")" ]
        _gmtm = askstring( _('Set time'), "\n".join(msg), initialvalue=time.strftime("%Y-%m-%d %H:%M:%S", starry.gmtm) )
        if _gmtm:
            _gmtm = time.strptime( _gmtm, "%Y-%m-%d %H:%M:%S" )
        elif _gmtm == None:
            return
        else:
            _gmtm = time.gmtime(time.time())
        starry.gmtm = _gmtm
    except:
        print('setTime: ', sys.exc_info()[0], sys.exc_info()[1])

root = Tk()
root.geometry('1000x650+%s+%s' % (150, 20))
dbcarta = dbCarta(root, viewportx=600, viewporty=400)
_ = setLanguage(dbcarta.langOf(), 'starry')
__ = setLanguage(dbcarta.langOf(), 'dbcarta')
root.title(_('Starry Sky on Canvas'))
f = Frame(root)
f.pack(fill='both')
Button(f, bitmap='hourglass', foreground=rgb(150,50,55), command=lambda : setTime() or renderSky()).pack(side='right')
help_var = StringVar()
help_var.set( '\n'.join( [
              _('Turn, Move Starry Sky') + ':',
              '    ' + __('<Shift> + <Arrows> turn sphere (for Globe projection)'),
              '    ' + __('<Shift> + <Left Click> move view with cursor'),
              _('View body info') + ':',
              '    ' + __('<Right Click> context menu')] ) )
Button(f, bitmap='questhead', foreground='blue', command=lambda: showinfo(title='Starry Sky v' + __version__,
                                                                          message=help_var.get())).pack(side='right')
tmsg_var = StringVar()
Label(f, textvariable=tmsg_var, anchor='w', justify='left').pack(fill='both')
starry = Starry()
dbcarta.changeProject(203, [[37.61,55.75]])
renderSky()
dbcarta.paintBound()
dbcarta.loadCarta(CONTINENTS)
dbcarta.loadCarta([('DotPort', 'Moscow', [[37.61,55.75]], _('Moscow'))])
dbcarta.loadCarta(dbcarta.createMeridians())
renderSat()
dbcarta.usercl('changeProject', ['renderSky', locals()], 'Before')
dbcarta.usercl('changeProject', ['renderSat', locals()], 'After')
root.mainloop()
root.destroy()
