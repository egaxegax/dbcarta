#!/usr/bin/env python
#
# Python 2,3 Tkinter Canvas object map. Draw, color, move, zoom map and objects.
#
# https://github.com/egaxegax/dbcarta.
# egax@bk.ru, 2007-2022.

"""
General hotkeys:
<Control> + <Left Click> draw figure and calculate distance
<Left Click> + <Move> move view with cursor
<Right Click> context menu
<Arrows: Left-Right-Top-Bottom> scroll view
<Control> + <Left-Right Arrows> rotate map around Z-axis
<Shift> + <Arrows> turn sphere (for Globe projection)
<+>|<->|<Space>|<BackSpace>|<Mouse Wheel> zoom-in/out
"""

__version__ =  "220115"

import sys, re
from math import *
from inspect import stack

if sys.version_info[0] == 3:
    from tkinter.colorchooser import *
    from tkinter.simpledialog import *
    from tkinter.messagebox import *
else:
    from tkColorChooser import *
    from tkSimpleDialog import *
    from tkMessageBox import *

from tablelist.tablelist import *

"""Return value in interval -y..y.
X value (in radians).
Y interval value (in radians)."""
P = lambda x, y: x - 2 * y * int(x / (2 * y) + [-1, 1][x > 0] / 2.0)

"""Return Tk color by RGB."""
rgb = lambda r, g, b: '#%02x%02x%02x' % (r, g, b)

class dbCarta:
    """Main class."""
    # Public
    mopt = {
        '.Arctic':      {'cls': 'Polygon', 'fg': rgb(210,221,195), 'bg': rgb(210,221,195)},
        '.Mainland':    {'cls': 'Polygon', 'fg': rgb(135,159,103), 'bg': rgb(135,159,103)},
        '.Water':       {'cls': 'Polygon', 'fg': rgb(90,140,190), 'bg': rgb(90,140,190)},
        '.WaterLine':   {'cls': 'Line', 'fg': rgb(186,196,205), 'smooth': 1},
        '.Latitude':    {'cls': 'Line', 'fg': rgb(164,164,164), 'anchor': 'sw'},
        '.Longtitude':  {'cls': 'Line', 'fg': rgb(164,164,164), 'anchor': 'nw'},
        'DotPort':      {'cls': 'Dot', 'fg': rgb(240,220,0), 'labelcolor': rgb(255,155,128)},
        'Area':         {'cls': 'Polygon', 'fg': rgb(0,130,200), 'bg': ''},
        'Line':         {'cls': 'Line', 'fg': rgb(0,130,200)},
        'Figure':       {'cls': 'Line', 'fg': rgb(0,130,200), 'width': 2},
        'CurrFigure':   {'cls': 'Line', 'fg': rgb(0,130,200), 'anchor': 'ne', 'width': 2},
        'UserLine':     {'cls': 'Line', 'fg': rgb(0,0,0), 'anchor': 'nw'},
    }
    delta = 3600.0
    halfX = 648000.0
    ylimit = 84
    mflood = {}
    # Private
    __wkt_mopt = {
        'POINT': 'DotPort',
        'MULTIPOINT': 'DotPort',
        'LINESTRING': 'Line',
        'MULTILINESTRING': 'Line',
        'POLYGON': 'Area',
        'MULTIPOLYGON': 'Area',
    }
    __temp = {}
    __usercl = {}
    
    def __init__(self, master, **kw):
        """Constructor.
        MASTER container.
        **KW dict with config:
          PROJECT projection id.
          BG Canvas bg color.
          VIEWPORTX scroll width in degrees.
          VIEWPORTY scroll height in degrees."""
        self.lang()
        master.protocol('WM_DELETE_WINDOW', master.quit)
        master.title('Tk Widget dbCarta')
        parent = Frame(master)
        parent.pack(fill='both', expand=1)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        self.master = master
        self.parent = parent
        self.bg = kw.get('bg')
        self.viewportx = kw.get('viewportx', 360+180)
        self.viewporty = kw.get('viewporty', 180+90)
        self.__createCtls()
        self.project = 0
        self.changeProject(self.project)
        master.update()

    def __createMenu(self, dynmenu=()):
        """Create right-click menu.
        DYNMENU (opt.) list with dyn elements
           (`func for command`, `label`, `func arg1`, ...)."""
        self.menu = {}
        self.menu['menu'] = Menu(self.parent, tearoff=0)
        self.menu['menu.project'] = Menu(self.menu['menu'], tearoff=0)
        self.menu['menu.project'].add_radiobutton(label=_('Mercator'), command=lambda: self.changeProject(101))
        self.menu['menu.project'].add_radiobutton(label=_('Linear'), command=lambda: self.changeProject(0))
        self.menu['menu.project'].add_radiobutton(label=_('Globe/Sphere'), command=lambda: self.changeProject(203))
        self.menu['menu'].add_cascade(label=_('Projection'), menu=self.menu['menu.project'])
        self.menu['menu'].add_separator()
        self.menu['menu'].add_command(label=_('Forecolor: Outline...'), command=lambda: self.colorCarta('fg', 0, 'Area', 'Line'))
        self.menu['menu.fillmenu'] = Menu(self.menu['menu'], tearoff=0)
        self.menu['menu.fillmenu'].add_command(label=_('Set transparent'), command=lambda: self.colorCarta('bg', 1, 'Area'))
        self.menu['menu.fillmenu'].add_command(label=_('Backcolor...'), command=lambda: self.colorCarta('bg', 0, 'Area'))
        self.menu['menu'].add_cascade(label=_('Backcolor: Filling'), menu=self.menu['menu.fillmenu'])
        self.menu['menu'].add_separator()
        self.menu['menu.clrmenu'] = Menu(self.menu['menu'], tearoff=0)
        self.menu['menu.clrmenu'].add_command(label=_('All'), command=lambda: self.clearLayers(*self.mopt.keys()))
        self.menu['menu'].add_cascade(label=_('Clear'), menu=self.menu['menu.clrmenu'])
        self.menu['menu'].add_separator()
        self.menu['menu.langmenu'] = Menu(self.menu['menu'], tearoff=0)
        self.menu['menu.langmenu'].add_radiobutton(label=_('Russian'), command=lambda: self.lang('ru'))
        self.menu['menu.langmenu'].add_radiobutton(label=_('English'), command=lambda: self.lang('en'))
        self.menu['menu'].add_cascade(label=_('Language'), menu=self.menu['menu.langmenu'])
        self.menu['menu'].add_command(label=_('Help'), command=lambda: showinfo(title='dbCarta v' + __version__,
                                                                                message=_(__doc__ ) ))
        # add dynmenu
        k = {}
        for i, x in enumerate(dynmenu):
            if not i:
                addmenu = lambda x: self.menu[x[0]].add_command(label=x[1], command=lambda: x[2](*x[3:]))
            if x[0] in k:
                self.menu[x[0]].add_separator()
                k[x[0]] = ''
            addmenu(x)

    def __createCtls(self):
        """Create widgets."""
        #self.parent.bind('<Configure>', self.labelPoint)
        self.master.bind('<Key>', self.__master_keyPress)
        self.master.bind('<Control-Key>', self.__master_keyPressCtrl)
        self.master.bind('<Shift-Key>', self.__master_keyPressShift)
        # Slider widget for scale
        self.slider = Scale(self.parent, label=_('Lon Lat'), orient='horizontal', showvalue=0,
                            from_=0.0005, to=1.0, resolution=0.0005, command=self.scaleCarta)
        self.slider.var = DoubleVar()
        self.slider.config(variable=self.slider.var)
        self.slider.grid(column=0, row=0, columnspan=2, sticky='ew')
        # Canvas with scrollbars
        self.dw = Canvas(self.parent, bd=0, bg=self.bg or rgb(186,196,205))
        self.scrollX = Scrollbar(self.parent, orient='horizontal',
                                 command=lambda *ev: self.dw.xview(*ev))
        self.scrollY = Scrollbar(self.parent, orient='vertical',
                                 command=lambda *ev: self.dw.yview(*ev))
        self.scrollX.bind('<ButtonRelease-1>', self.__dw_mouseUp)
        self.scrollY.bind('<ButtonRelease-1>', self.__dw_mouseUp)
        self.scrollX.grid(column=0, row=2, sticky='ew')
        self.scrollY.grid(column=1, row=1, sticky='ns')
        self.dw.config(xscrollcommand=self.scrollX.set, yscrollcommand=self.scrollY.set)
        self.dw.grid(column=0, row=1, sticky='nsew')
        self.dw.bind('<Button>', self.__dw_mouseDown)
        self.dw.bind('<Control-Button-1>', self.__dw_mouseDownCtrl)
        self.dw.bind('<ButtonRelease-1>', self.__dw_mouseUp)
        self.dw.bind('<Control-ButtonRelease-1>', self.__dw_mouseUpCtrl)
        self.dw.bind('<Motion>', self.__dw_mouseMove)

    def __listCoords(self, title, ftag, x, y):
        """Show tablelist with object coords.
        TITLE label from mflood.
        FTAG uniq. tag from mflood.
        X left-top X (in pixels).
        Y left-top Y (in pixels)."""
        # create window for ftag
        if not 'coords.%s' % ftag in self.__temp:
            def exitcmd(ev):
                """Close window callback."""
                if (str(ev.widget) == _self.winfo_pathname(_self.winfo_id())):
                    self.__temp.pop('coords.%s' % _self.ftag, '')
                    self.clearLayers('UserLine')
            def sortbycolumn(table, col):
                """Tablelist sort column callback."""
                order = "-increasing"
                if _self.tlist.sortcolumn() == int(col) and _self.tlist.sortorder() == "increasing":
                    order = "-decreasing"
                _self.tlist.sortbycolumn(col, order)
            def editendcmd(table, row, col, text):
                """Tablelist cell end edit callback."""
                index = _self.tlist.get(row)[0]
                m = self.mflood.get(_self.ftag) or self.__usercl.get(_self.ftag)
                coord = _coord = m['coords'][index]
                old_text = coord[int(col) - 1]
                try:    text = float(text)
                except: return old_text
                # if text is number
                if col == '1':
                    _coord = [text, coord[1]]
                elif col == '2':
                    _coord = [coord[0], text]
                # save new coord
                self.__temp['coords.%s' % _self.ftag][index] = _coord
                return text
            def savecoord():
                """Save button click callback."""
                _coords = self.__temp['coords.%s' % _self.ftag]
                m = self.mflood.get(_self.ftag) or self.__usercl.get(_self.ftag)
                # update coords
                for index in _coords.keys():
                    m['coords'][index] = _coords[index]
                # update map if mflood
                if self.mflood.get(_self.ftag):
                    ftype = self.mflood.get(_self.ftag)['ftype']
                    self.paintCarta(m['coords'], ftype, _self.ftag)
                    self.labelPoint()
            def showcoord():
                """Show coords on map."""
                ftype = 'UserLine'
                self.clearLayers(ftype)
                try:    cursel = _self.tlist.getcurselection()
                except: cursel = ()
                for coords in cursel:
                    n, x, y = coords
                    left, top, right, bottom = self.viewsizeOf()
                    try:    px, py = self.toPoints([[x, y]], doscale=1)
                    except: continue
                    self.dw.create_line([left, py, right, py, px, py, px, top, px, bottom], tags=(ftype + '.1',ftype))
                    self.dw.create_text([px, py], anchor=self.mopt[ftype]['anchor'], text=str(n), tags=(ftype + '.1',ftype))
            _self = Toplevel(self.parent)
            _self.ftag = ftag
            _self.title(title)
            _self.geometry('220x200+%s+%s' % (x, y))
            _self.bind('<Destroy>', exitcmd)
            _self.fm = Frame(_self)
            _self.fm.columnconfigure(0, weight=1)
            _self.fm.rowconfigure(0, weight=1)
            _self.fm.pack(fill='both', expand=1)
            _self.tlist = TableList(_self.fm, activestyle = 'none', columns = (0, '#', 0, 'X', 0, 'Y'),
                                    setfocus=1, selectmode='extended', selecttype='row', stretch = 'all', stripebackground=self.mopt['.Water']['fg'])
            _self.tlist.configure(labelcommand=sortbycolumn, editendcommand=editendcmd)
            _self.tlist.columnconfigure(0, sortmode='integer')
            _self.tlist.columnconfigure(1, sortmode='dictionary', editable='yes')
            _self.tlist.columnconfigure(2, sortmode='dictionary', editable='yes')
            _self.scrollY = Scrollbar(_self.fm, orient='vertical', command=_self.tlist.yview)
            _self.scrollY.grid(column=1, row=0, sticky='ns')
            _self.tlist.config(yscrollcommand=_self.scrollY.set)
            _self.tlist.grid(column=0, row=0, sticky='nsew')
            _self.fbutt = Frame(_self.fm)
            _self.fbutt.grid(column=0, row=1)
            _self.btok = Button(_self.fbutt, text=_('Save'), command=savecoord)
            _self.btok.pack(side='left')
            _self.btshow = Button(_self.fbutt, text=_('Show'), command=showcoord)
            _self.btshow.pack(side='left')
            self.__temp['coords.%s' % ftag] = {}
            # coords from mflood or __usercl
            m = self.mflood.get(ftag) or self.__usercl.get(ftag)
            for i, _coords in enumerate(m.get('coords', [])):
                _self.tlist.insert('end', tuple([i] + _coords))

    #-------------------------------------

    def __master_keyPress(self, ev):
        """KeyPress callback."""
        # zoom/scale map
        if ev.keysym in ('KP_Add', 'plus', 'space', 'KP_Subtract', 'minus', 'BackSpace', 4, 5):
            self.slider.var.set(self.slider.get() + self.slider['resolution'] * (1, -1)[ev.keysym in ('KP_Subtract', 'minus', 'BackSpace', 5)])
            self.scaleCarta()
        # move map
        elif ev.keysym in ('Left', 'Right'):
            self.dw.xview('scroll', (1, -1)[ev.keysym == 'Left'], 'units')
            self.labelPoint()
        elif ev.keysym in ('Up', 'Down'):
            self.dw.yview('scroll', (1, -1)[ev.keysym == 'Up'], 'units')
            self.labelPoint()
        self.clfunc()

    def __master_keyPressCtrl(self, ev):
        """`Ctrl + Key` callback."""
        self.__temp['z_angle'] = self.__temp.get('z_angle', 0)
        if ev.keysym == 'Left':
            self.__temp['z_angle'] += 10
        elif ev.keysym == 'Right':
            self.__temp['z_angle'] -= 10
        else:
            return
        self.changeProject(self.project)
        self.labelPoint()
        self.clfunc()

    def __master_keyPressShift(self, ev):
        """`Shift + Key` callback."""
        if self.isSpherical():
            if ev.keysym == 'Left':
                self.__temp['centerof'][0][0] += 10
            elif ev.keysym == 'Right':
                self.__temp['centerof'][0][0] -= 10
            elif ev.keysym == 'Up':
                self.__temp['centerof'][0][1] -= 10
            elif ev.keysym == 'Down':
                self.__temp['centerof'][0][1] += 10
            else:
                return
            # range x(-180..180), y(-180..180)
            self.__temp['centerof'] = [[
                degrees(P(radians(self.__temp['centerof'][0][0]), pi)),
                degrees(P(radians(self.__temp['centerof'][0][1]), pi))]]
            self.changeProject(self.project)
            self.labelPoint()
        else:
            self.__master_keyPress(ev)
        self.clfunc()

    def __dw_mouseDown(self, ev):
        """MouseDown callback."""
        x, y = self.dw.canvasx(ev.x), self.dw.canvasy(ev.y)
        if 'Figure' in self.__temp:  # close figure and clear `waste`
            self.__dw_mouseDownCtrl(ev)
            self.__temp.pop('Figure', '')
            self.clearCarta('CurrFigure')
        elif ev.num == 1: 
            # remember visible center for move
            self.__temp['shift'] = [ ev, 
                [ self.dw.winfo_width() / 2.0,
                  self.dw.winfo_height() / 2.0 ],
                self.centerOf() ]
        elif ev.num == 3:  # add dynmenu
            pmsg = """
            POINT(0 0)
            LINESTRING(0 0,1 1,1 2)
            POLYGON((0 0,4 0,4 4,0 4,0 0),(1 1, 2 1, 2 2, 1 2,1 1))
            MULTIPOINT(0 0,1 2)
            MULTILINESTRING((0 0,1 1,1 2),(2 3,3 2,5 4))
            MULTIPOLYGON(((0 0,4 0,4 4,0 4,0 0),(1 1,2 1,2 2,1 2,1 1)), ((-1 -1,-1 -2,-2 -2,-2 -1,-1 -1)))
            GEOMETRYCOLLECTION(POINT(2 3),LINESTRING(2 3,3 4))"""
            mnu = [('menu', _('Add Figure(s)...'), lambda : self.loadCartaWKT( [(False, askstring(_('Add Figures'), _('Type coordinate\'s WKT-string: %s') % (pmsg,)))] ))]
            # clrmenu
            lclear = []
            for pid in self.dw.find_all():
                ftag, ftype = self.dw.gettags(pid)[:2]
                if ftype in self.mopt and not ftype in lclear:
                    lclear += [ftype]
                    mnu.append( ('menu.clrmenu', _('%s') % (ftype,), self.clearLayers, ftype) )
            # under cursor (not labels)
            for pid in self.dw.find_overlapping(x - 5, y - 5, x + 5, y + 5):
                ftag, ftype = self.dw.gettags(pid)[:2]
                if ftype in self.mopt and ftag[0] != '.':
                    label = ftag
                    mnu.append( ('menu', (_('Information %s') + '...') % (label,), self.__listCoords, _('Info %s') % (label,), ftag, ev.x_root, ev.y_root) )
                    mnu.append( ('menu.clrmenu', _('%s') % (label,), self.clearCarta, ftag) )
            self.__createMenu(mnu)
            self.menu['menu'].tk_popup(ev.x_root, ev.y_root)
        elif ev.num in (4,5): # wheel
            ev.keysym = ev.num
            self.__master_keyPress(ev)

    def __dw_mouseDownCtrl(self, ev):
        """Control + MouseDown callback."""
        x, y = self.dw.canvasx(ev.x), self.dw.canvasy(ev.y)
        # create or continue figure
        if 'Figure' in self.__temp:
            self.__temp['Figure'][1] += self.__temp['Figure'][0]
            self.__temp['Figure'][2] = self.fromPoints([x, y], dosphere=1)
            self.paintCarta(self.__temp['Figure'][2], 'Figure', '%04d_%s_%s' % (len(self.mflood)-1, 'Figure', self.__temp['Figure'][3]), addcoords=1)
        else:
            # remember init figure values of distance, coords, tag
            self.__temp['Figure'] = [0, 0, self.fromPoints([x, y], dosphere=1), self.freeTag('Figure')]
            self.loadCarta( [('Figure', self.__temp['Figure'][3], str(self.__temp['Figure'][2]))] )

    def __dw_mouseMove(self, ev):
        """MouseMove callback."""
        x, y = self.dw.canvasx(ev.x), self.dw.canvasy(ev.y)
        # move figure part
        if 'Figure' in self.__temp:
            coords = self.fromPoints([x, y], dosphere=1)
            if coords:
                coords = self.__temp['Figure'][2] + coords
                self.__temp['Figure'][0] = self.distance(coords)
                self.paintCarta(coords, 'CurrFigure', 'CurrFigure.1')
                self.paintCarta([coords[1]], 'CurrFigure', '.CurrFigure.1', _('%s\n%s km') % tuple(self.__temp['Figure'][:2]))
        elif 'shift' in self.__temp:
            pts = [ self.dw.canvasx(self.__temp['shift'][1][0] - (ev.x - self.__temp['shift'][0].x)),
                    self.dw.canvasy(self.__temp['shift'][1][1] - (ev.y - self.__temp['shift'][0].y)) ]
            if self.isSpherical():
                # turn sphere
                centerof = self.__temp['shift'][2]
                mcenterof = self.fromPoints(pts)
                self.__temp['centerof'] = [[ centerof[0][0] + mcenterof[0][0], centerof[0][1] + mcenterof[0][1]]]  
                self.changeProject(self.project)
                self.labelPoint()
            else:
                # center on move and remember new visible center
                self.centerPoint(*pts)
                self.__temp['shift'][0] = ev
            self.clfunc()
        # calc and show coords under cursor
        coords = self.fromPoints((x, y), dosphere=1) or [('', '')]
        self.slider.config(label=_('Lon %s Lat %s') % (str(coords[0][0]), str(coords[0][1])))

    def __dw_mouseUp(self, ev):
        """MouseUp callback."""
        self.__temp.pop('shift', '')
        self.labelPoint()
        self.clfunc()

    def __dw_mouseUpCtrl(self, ev):
        """Control + MouseUp callback."""
        self.clfunc()

    #-------------------------------------

    def createMeridians(self):
        """Return meridians coords."""
        lonlat = []
        # X
        x = -180
        while x <= 180:
            lon = []
            y = -90
            while y <= 90:
                lon += [[x, y]]
                y += 30
            lonlat += [('.Longtitude', str([x, y]), str(lon), str(x), str(lon[0]))]
            x += 30
        # Y
        y = -90
        while y <= 90:
            centerof = [-180, y]
            lat = [centerof]
            x = -180
            while x < 180:
                x += 30
                lat += [[x, y]]
                lonlat += [('.Latitude', str([x, y]), str(lat), str(y), str(centerof))]
                label = centerof = None
                lat.pop(0)
            y += 30
        return lonlat

    def centerPoint(self, x=None, y=None):
        """Center map by point.
        X (opt.) `points` by horizontal.
        Y (opt.) `points` by vertical."""
        # current view
        scrollX = self.dw.xview()
        scrollY = self.dw.yview()
        if x and y:
            # center by point
            moveX = x / (self.scaleX * self.slider.var.get()) - (scrollX[1] - scrollX[0]) / 2.0
            moveY = y / (self.scaleY * self.slider.var.get()) - (scrollY[1] - scrollY[0]) / 2.0
        else:
            # visible center
            moveX = self.__temp['center_x'] - (scrollX[1] - scrollX[0]) / 2.0
            moveY = self.__temp['center_y'] - (scrollY[1] - scrollY[0]) / 2.0
        self.dw.xview('moveto', moveX)
        self.dw.yview('moveto', moveY)

    def changeProject(self, new_project=0, centerof=None):
        """Change map projection. Recalc. coords of all objects.
        MenuClick `Project` callback.
        NEW_PROJECT (opt.) projection id {
            0 linear (default) |
            101 mercator |
            203 ortho globe/sphere }.
        CENTEROF center point to set (opt.)."""
        mcenterof = []
        if not self.project == new_project:
            mcenterof = self.__temp['centerof'] = (centerof or self.centerOf())
        if new_project == 101:    # mercator
            self.scaleX = self.viewportx * self.delta
            self.scaleY = self.toMercator(90.0) * self.delta * self.viewporty/90.0
        elif new_project == 0:   # linear
            self.scaleX = self.viewportx * self.delta
            self.scaleY = self.viewporty * self.delta
        elif new_project == 203: # globe
            self.scaleX = self.viewportx * self.delta
            self.scaleY = self.viewporty * self.delta
        self.halfX = self.scaleX / 2.0
        self.halfY = self.scaleY / 2.0
        self.project = new_project
        self.scaleCarta(docenter=0)
        self.clfunc('Before')
        self.paintBound()
        # redraw all in mflood by new projection
        mkeys = list(self.mflood.keys())
        mkeys.sort()
        for ftag in mkeys:
            value = self.mflood[ftag]
            self.paintCarta(value['coords'], value['ftype'], ftag)
        if mcenterof:
            self.centerCarta(mcenterof)
        self.clfunc('After')

    def freeTag(self, ftype, i=1):
        """Return label with increment index.
        FTYPE layer's name from mopt.
        I (opt.) init index value (1 default)."""
        ftag = str(len(self.dw.find_withtag(ftype)) + i)
        if self.dw.find_withtag('%s_%s' % (ftype, ftag)):
            return self.freeTag(ftype, i + 1)
        return ftag

    def labelPoint(self):
        """Draw labels of objects in visible area. Also mouse ButtonRelease callback."""
        rect = self.fromPoints(self.viewsizeOf(), 0)
        left, top, right, bottom = rect[0] + rect[1]
        mleft = [left, -180][left < -180]
        mtop = [top, [90, self.ylimit][self.project == 101]][top > 90]
        # clear all labels and draw again in visible area
        for ftag, value in self.mflood.items():
            ftype  = value['ftype']
            _ftag = '.' + ftag             # tag of label
            __ftag = '.' + _ftag           # tag of icon
            centerof = value.get('centerof')
            if self.mopt[ftype]['cls'] == 'Dot':
                centerof = value['coords']
            label = value.get('label')
            icon = value.get('icon')
            if (not centerof or not label):
                continue
            center_x, center_y = centerof[0]
            # limit merc
            if self.project == 101:
                if abs(center_y) > self.ylimit:
                    center_y = self.ylimit * [-1, 1][center_y > 0]
            self.dw.delete(_ftag)
            self.dw.delete(__ftag)
            if ftype in ('.Longtitude'):
                if self.isSpherical():
                    if -180 < center_x <= 180:
                        self.paintCarta([[center_x, 0]], ftype, _ftag, ftext=label)
                elif left <= center_x <= right:
                    self.paintCarta([[center_x, mtop]], ftype, _ftag, ftext=label)
            elif ftype in ('.Latitude'):
                if self.isSpherical():
                    self.paintCarta([[0, center_y]], ftype, _ftag, ftext=label)
                elif bottom <= center_y <= top:
                    # limit merc
                    if self.project == 101:
                        label = str(int(center_y))
                    self.paintCarta([[mleft, center_y]], ftype, _ftag, ftext=label)
            else:
                if (left <= center_x <= right and bottom <= center_y <= top) or self.isSpherical():
                    _d = self.slider['from'] / self.slider.var.get() ; d = 3 * _d # shift label (3 degrees)
                    if icon:  # icon & text
                        self.paintCarta([[center_x + d, center_y]], ftype, __ftag, fimage=icon) ; d = icon.width() * _d
                    self.paintCarta([[center_x + d, center_y]], ftype, _ftag, ftext=label)

    def lang(self, lang=''):
        global _
        self.__lang = lang
        _ = setLanguage(lang)

    def centerCarta(self, centerof=[[0,0]]):
        """Center map by point.
        CENTEROF list of point coords [[x,y]] (in degrees)."""
        pts = self.toPoints(centerof, doscale=1)
        if pts:
            self.centerPoint(*pts)
            self.labelPoint()

    def loadCartaWKT(self, data=(), docenter=0):
        """Display WKT-objects. Use loadCarta.
        DATA (opt.) list of list as (
            0 see loadCarta: data[1],
            1 WKT-string "LINESTRING(0 0,1 1,..)",
            2 see loadCarta: data[3],
            3 see loadCarta: data[4],
            4 see loadCarta: data[5],
            5 see loadCarta: data[6],
            6 see loadCarta: data[7] ).
        DOCENTER see loadCarta: docenter."""
        _data = []
        for row in data:
            try:
                _row = dict([[i, x] for i, x in enumerate(row)])
                if not _row.get(1):
                    continue
                obj_coords = self.fromWKT(_row[1])
                if not obj_coords:
                    raise ValueError("Invalid WKT")
                for i1, wl in enumerate(obj_coords):
                    tp, coords1 = wl
                    for i2, coords2 in enumerate(coords1):
                        for i, coords in enumerate(coords2):
                            # unique tag if not
                            if not _row[0]: _row[0] = self.freeTag(self.__wkt_mopt[tp])
                            _data += [(self.__wkt_mopt[tp], '%s_%s_%s_%s' % (_row[0], i1, i2, i), coords, _row.get(2), _row.get(3), _row.get(4), _row.get(5), _row.get(6))]
            except:
                print('loadCartaWKT: ', sys.exc_info()[0], sys.exc_info()[1])
                raise
        if _data:
            self.loadCarta(_data, docenter)

    def loadCarta(self, data=(), docenter=0):
        """Display objects. Use paintCarta.
        DATA (opt.) list of list as (
            0 layer name from mopt,
            1 tag of object (unique within layer),
            2 string of coords as "((x1,y1),...,(xn,yn))"  (in degrees),
            3 (opt.) label,
            4 (opt.) center for label as {'' (no label)|"(x,y)"},
            5 (opt.) icon (GIF),
            6 (opt.) fgcolor,
            7 (opt.) bgcolor).
        DOCENTER (opt.) center after display {1|0 (default)}."""
        for row in data:
            try:
                _row = dict([[i, x] for i, x in enumerate(row) if not x == None])
                if not ( _row[2] and _row[0] in self.mopt and _row[1] ):
                    continue
                ftype, tag = _row[0], _row[1]
                ftag = '%04d_%s_%s' % (len(self.mflood), ftype, tag)
                coords, centerof = _row[2], _row.get(4)
                if type(coords) is str:
                    coords = self.toCoords(coords)
                if type(centerof) is str:
                    centerof = self.toCoords(centerof)
                # save in mflood label, coords..
                self.mflood[ftag] = {
                    'ftype': ftype,
                    'coords': coords,
                    'label': _row.get(3),
                    'centerof': centerof,
                    'icon': _row.get(5),
                    'fg': _row.get(6, self.mopt[ftype]['fg']),
                    'bg': _row.get(7, self.mopt[ftype].get('bg', ''))}
                # draw object
                self.paintCarta(coords, ftype, ftag)
            except:
                print('loadCarta: ', sys.exc_info()[0], sys.exc_info()[1])
                raise
        if data:
            if docenter and centerof:
                # remember center for Globe projection
                if self.isSpherical():
                    self.__temp['centerof'] = centerof
                    self.changeProject(self.project)
                self.centerCarta(centerof)
            else:
                self.labelPoint()

    def paintBound(self):
        """Draw Sphere radii bounds."""
        self.dw.delete('sphereBounds')
        if self.isSpherical():
            radii = 180 / pi * self.delta * self.slider.var.get()
            vx, vy = self.scaleX * self.slider.var.get(), self.scaleY * self.slider.var.get()
            self.dw.create_oval(vx/2.0 - radii, vy/2.0 - radii, vx/2.0 + radii, vy/2.0 + radii,
                                outline=self.mopt['.Latitude']['fg'], 
                                fill=self.mopt['.Water']['bg'], tags=('.Water', 'sphereBounds'))            

    def paintCarta(self, coords, ftype, ftag, ftext='', fimage=None, addcoords=0):
        """Draw object, label, icon.
        COORDS list of coords [[x,y],[x1,y1]...] (in degrees).
        FTYPE layer name from mopt.
        FTAG uniq. tag.
        FTEXT (opt.) label.
        FIMAGE (opt.) icon (GIF).
        ADDCOORDS (opt.) create or continue outline {1|0 (default)}."""
        # interpolate coords for Globe projection
        _coords = []
        if self.isSpherical():
            for i in range(len(coords) - 1):
                _coords += self.interpolateCoords(coords[i:i + 2])
        if not _coords:
            _coords = coords

        points = self.toPoints(_coords, doscale=1)
        if not addcoords:
            self.dw.delete(ftag)
        if not points:
            return

        # colors of layer or self
        fg = self.mopt[ftype]['fg']
        bg = self.mopt[ftype].get('bg', '')
        mflood = self.mflood.get(ftag, 0)
        if mflood:
            fg = mflood.get('fg', fg)
            bg = mflood.get('bg', bg)
        # create/add points
        if addcoords:
            self.dw.coords(ftag, tuple(self.dw.coords(ftag) + points))
            self.mflood[ftag]['coords'] += coords
        elif ftext:
            self.dw.create_text(points, anchor=self.mopt[ftype].get('anchor', 'w'), text=' ' + ftext + '   ', fill=self.mopt[ftype].get('labelcolor', 'black'), tags=(ftag, ftype))
        elif fimage:
            self.dw.create_image(points, anchor=self.mopt[ftype].get('anchor', 'w'), image=fimage, tags=(ftag, ftype))
        elif self.mopt[ftype]['cls'] in ('Line'):
            if len(points) < 4:
                points = points * 2
            self.dw.create_line(points, fill=fg, 
                                dash=self.mopt[ftype].get('dash'), smooth=self.mopt[ftype].get('smooth'), 
                                width=self.mopt[ftype].get('width', 1), tags=(ftag, ftype))
        elif self.mopt[ftype]['cls'] in ('Polygon'):
            if len(points) < 4:
                points = points * 2
            self.dw.create_polygon(points, fill=bg, outline=fg, tags=(ftag, ftype))
        elif self.mopt[ftype]['cls'] in ('Dot'):
            if len(points) < 4:
                points = points * 2
            size = self.mopt[ftype].get('size', 0)
            self.dw.create_oval(points[0] - size/2.0, points[1] - size/2.0,
                                points[0] + size/2.0, points[1] + size/2.0,
                                width=self.mopt[ftype].get('width', 1), fill=bg, outline=fg, tags=(ftag, ftype))

    def clearLayers(self, *ftypes):
        """Delete all objects by layer.
        *FTYPES layers from mopt."""
        ftags = list(ftypes)
        for ftag, value in self.mflood.items():
            if value['ftype'] in ftypes:
                ftags.append(ftag)
        self.clearCarta(*ftags)

    def clearCarta(self, *ftags):
        """Delete objects, labels, icons from canvas and mflood.
        *FTAGS tags of objects."""
        for ftag in ftags:
            self.dw.delete(ftag)
            self.dw.delete('.' + ftag)
            self.dw.delete('..' + ftag)
            self.mflood.pop(ftag, '')

    def colorCarta(self, option='fg', dotransparent=0, *ftypes):
        """Select and save layer'color (transparent) of layers.
        OPTION (opt.) param's key from mopt (default 'fg').
        DOTRANSPARENT (opt.) use transparent {1|0 (default)}.
        *FTYPES (opt.) list of layers from mopt."""
        color = ''
        if not dotransparent:
            try:
                if self.mopt[ftypes[0]].get(option):
                    color = askcolor(parent=self.parent, initialcolor=self.mopt[ftypes[0]].get(option))
                else:
                    color = askcolor(parent=self.parent)
            except:
                return
            color = color[1]
        # save color to mopt
        for ftype in ftypes:
            self.mopt[ftype][option] = color

    def scaleCarta(self, docenter=1):
        """Change scale according previous value. Also Slider callback.
        DOCENTER (opt.) center when scaling {1 (default)|0}."""
        # remember visible center for centerPoint
        self.__temp['center_x'] = (self.dw.xview()[0] + self.dw.xview()[1]) / 2.0
        self.__temp['center_y'] = (self.dw.yview()[0] + self.dw.yview()[1]) / 2.0
        # calc ratio of current and previous scale
        ratio = self.slider.var.get() / self.__temp.get('scale', self.slider['resolution'])
        # scale and center with ratio, show labels by new scale
        self.dw['scrollregion'] = (0, 0, self.scaleX * self.slider.var.get(), self.scaleY * self.slider.var.get())
        self.dw.scale('all', 0, 0, ratio, ratio)
        if docenter:
            self.centerPoint()
            self.labelPoint()
        # remember scale after changing
        self.__temp['scale'] = self.slider.var.get()

    def isSpherical(self, project=False):
        if project == False:
           project = self.project
        return (project > 200 and project < 300)

    def usercl(self, cl, func, when=''):
        """Add user info/callback.
        CL key/event name.
        FUNC value/user function name.
        WHEN (opt.) Before/After key."""
        self.__usercl[cl + when] = func

    def clfunc(self, when=''):
        """Execute user callback.
        WHEN see usercl."""
        fn = stack()[1][3]
        if fn + when in self.__usercl:
            clfunc, symtable = self.__usercl[fn + when]
            exec(clfunc + '()', symtable)

    def centerOf(self):
        """Return centerof [[x,y]] (in degrees)."""
        if self.isSpherical():
            return self.__temp.get('centerof', [[0,0]])
        else:
            return self.fromPoints(self.viewcenterOf())

    def sizeOf(self):
        """Return viewport size as [width, height] disregarding scale (in points)."""
        return [self.scaleX, self.scaleY]

    def viewsizeOf(self):
        """Return rect. of visible area (in points)."""
        left, right = [self.scaleX * self.slider.var.get() * x for x in self.dw.xview()]
        top, bottom = [self.scaleY * self.slider.var.get() * y for y in self.dw.yview()]
        return [left, top, right, bottom]

    def viewcenterOf(self):
        """Return center of visible area (in points)."""
        rect = self.viewsizeOf()
        return [ (rect[0] + rect[2]) / 2.0,
                 (rect[1] + rect[3]) / 2.0 ]

    def langOf(self):
        return self.__lang

    #-----------------------------------------------------

    def toPoints(self, coords=[], doscale=0):
        """Return list of `points` [pt1, pt2,...] from coords. Rev. to fromPoints.
        COORDS list of coords [[x,y],[x1,y1]...] (in degrees).
        DOSCALE (opt.) consider scale {1|0 (default)}."""
        points = []
        centerof = self.fromPoints(self.viewcenterOf())
        for x, y in coords:
            if self.project in (0, 101):
                x = float(x)
                y = [self.toMercator(float(y)), float(y)][self.project != 101]
                x, y = self.rotateZ([x, y], centerof)
                y = -y
            elif self.project == 203:
                tmp = self.toSphere([x, y])
                if not tmp:
                    continue
                x, y = self.rotateZ(tmp)
            _x = x * self.delta + self.halfX 
            _y = y * self.delta + self.halfY
            if doscale:
                points += [_x * self.slider.var.get(), _y * self.slider.var.get()]
            else:
                points += [_x, _y]
        return points

    def fromPoints(self, points=[], dorotatez=1, dosphere=0):
        """Return list of coords [[x,y],[x1,y1]...] from `points`(in degrees). Rev. to toPoints.
        Call rotateZ if DOROTATEZ and `fromSphere if DOSPHERE.
        POINTS list [pt1, pt2,...] of `points`."""
        b, coords = 0, []
        center_x, center_y = self.viewcenterOf()
        for point in points:
            if not b:
                x, center_x = [(point / self.slider.var.get() - self.halfX) / self.delta for point in [point, center_x]]
            else:
                y, center_y = [-(point / self.slider.var.get() - self.halfY) / self.delta for point in [point, center_y]]
                if self.isSpherical() and dosphere:
                    if dorotatez:
                        x, y = self.rotateZ([x, y])
                    _coords = self.fromSphere([x, y])
                    if _coords:
                        coords += [_coords]
                else:
                    if dorotatez:
                        x, y = self.rotateZ([x, y], [[center_x, center_y]], reverse=1)
                    y = [self.fromMercator(y), y][self.project != 101]
                    coords += [[x, y]]
            b = not b
        return coords

    def toCoords(self, strcoords):
        """Return list of coords [[x,y],[x1,y1]...] from string (in degrees).
        STRCOORDS string of coords, e.g. '(x,y),(x1,y1),...'."""
        regstr = '(-?\d+\.?\d*)[ \t]*,[ \t]*(-?\d+\.?\d*)'
        coords = []
        if strcoords:
            coords = [[float(x), float(y)] for x, y in re.findall(regstr, strcoords)]
        return coords

    def fromWKT(self, wkt):
        """Return list of coords from wkt-string.
        WKT string, e.g. 'MULTIPOINT((0 0),(20 30))'."""
        r = '(-?\\d+\\.?\\d*)[ \t]+[ \t]*(-?\\d+\\.?\\d*)'
        r1 = '((?:POINT|MULTIPOINT|LINESTRING|MULTILINESTRING|POLYGON|MULTIPOLYGON)[^a-zA-Z]+)'
        # wkt-string -> type and coords
        wkt = wkt.replace("(", "[").replace(")", "]")
        tp = wkt[:wkt.find("[")]
        # recurse call
        if (tp in ('GEOMETRYCOLLECTION')):
            m = re.findall(r1, wkt[:len(wkt)-1])
            coords = []
            for x in m:
                coords += self.fromWKT(x.rstrip(","))
            return coords
        try:
            e = eval(re.sub(r, '[\\1,\\2]', wkt[wkt.find("["):]))
        except:
            return
        if (tp in ('MULTIPOINT')):
            return [[tp, [[[x]] for x in e]]]
        if (tp in ('POINT', 'LINESTRING')):
            return [[tp, [[e]]]]
        if (tp in ('MULTILINESTRING', 'POLYGON')):
            return [[tp, [e]]]
        if (tp in ('MULTIPOLYGON')):
            return [[tp, e]]

    def toMercator(self, y, ylimit=None):
        """Return latitude in Mercator project. Rev. to fromMercator.
        Y latitude (in degrees).
        YLIMIT (opt.) limit (default ylimit)."""
        if not ylimit:
            ylimit = self.ylimit
        if abs(y) > ylimit:
            return self.toMercator([-1, 1][y > 0] * ylimit)
        else:
            return degrees(log(tan(radians(y) / 2.0 + atan(1))))

    def fromMercator(self, y):
        """Return latitude from Mercator project. Rev. to toMercator.
        Y latitude (in degrees)."""
        return degrees(2.0 * (atan(e**(radians(y))) - atan(1)))

    def toSphere(self, coords):
        """Return list of two `points` for Spherical projection.
        COORDS coords list [x,y] (in degrees)."""
        self.__temp['centerof'] = centerof = self.__temp.get('centerof', [[0,0]])
        x, y, center_x, center_y = [radians(float(x)) for x in coords + centerof[0]]
        center_x += pi
        if (sin(y) * sin(center_y) - cos(y) * cos(center_y) * cos(center_x - x)) > 0:
            return [ degrees(cos(y) * sin(center_x - x)),
                     degrees(-sin(y) * cos(center_y) - sin(center_y) * cos(y) * cos(center_x - x)) ]

    def fromSphere(self, coords):
        """Return [x,y] (in degrees) or empty list [] if out from Spherical project. Rev. to toSphere. 
        Original code was taken from `gctpc` project (inverse ortho projection).
        COORDS coords list [x,y] (in degrees)."""
        # internal
        asinz = lambda x: asin([x, ([-1.0, 1.0][x > 1.0])][abs(x) > 1.0])
        adjust_lon = lambda x: [(x - ([1, -1][x < 0] * 2.0 * pi)), x][abs( x ) < pi]
        EPSLN = 1.0e-10
        # args
        centerof = self.__temp.get('centerof', [[0,0]])
        x, y, center_x, center_y = [radians(float(x)) for x in coords + centerof[0]]
        #a = 1
        rh = sqrt(x * x + y * y) + EPSLN
        if rh > 1:
            return []
        sin_p14 = sin(center_y)
        cos_p14 = cos(center_y)
        z = asinz( rh / 1 )
        sinz = sin( z )
        cosz = cos( z )
        lon = center_x
        if ( abs(rh) <= EPSLN ):
            lat = center_y
        lat = asinz( cosz * sin_p14 + (y * sinz * cos_p14) / rh )
        con = abs(center_y) - pi / 2.0
        if ( abs(con) <= EPSLN ):
            if ( center_y >= EPSLN ):
                lon = adjust_lon( center_x + atan2(x, y) )
            else:
                lon = adjust_lon( center_x - atan2(-x, y) )
        con = cosz - sin_p14 * sin(lat)
        if ((abs(con) >= EPSLN) or (abs(x) >= EPSLN)):
            lon = adjust_lon(center_x + atan2((x * sinz * cos_p14), (con * rh)));
        x = degrees(lon)
        y = degrees(lat)
        return [x, y]

    def rotateZ(self, coords, centerof=[[0,0]], reverse=0):
        """Return [X,Y] rotated around Z-axis with angle."""
        roll = self.__temp.get('z_angle', 0)
        if ( roll ):
            x, y, center_x, center_y = coords + centerof[0]
            roll = radians(roll)
            if reverse: roll = -roll
            r = sqrt((center_x - x) * (center_x - x) + (y - center_y) * (y - center_y))
            if r:
                a = acos((center_x - x) / r)
                if ( y < center_y ): a = 2.0 * pi - a
                coords = [ center_x - r * cos(roll + a),
                           center_y + r * sin(roll + a) ]
        return coords

    #-----------------------------------------------------

    def distance(self, coords):
        """Return the length of the great circle between two points (in km).
        COORDS points list [[x,y],[x1,y1]] (in degrees)."""
        x, y, x1, y1 = [radians(x) for x in coords[0] + coords[1]]
        return 6378.136 * acos(cos(y) * cos(y1) * cos(x - x1) + sin(y) * sin(y1))

    def interpolateCoords(self, coords, scalestep=500):
        """Return list of coords as interpol. of two points [[x,y],[x1,y1]].
        COORDS points list [[x,y],[x1,y1]] (in degrees).
        SCALESTEP step (in km)."""
        x, y, x1, y1 = coords[0] + coords[1]
        scalestep = int(self.distance(coords) / scalestep)
        if not scalestep:
            return coords
        scale_dx = (x1 - x) / scalestep
        scale_dy = (y1 - y) / scalestep
        _x, _y = x, y
        interpol_pts = [[_x, _y]]
        for i in range(scalestep):
            _x += scale_dx
            _y += scale_dy
            interpol_pts += [[_x, _y]]
        return interpol_pts

def setLanguage(lang='', tr='dbcarta'):
    """Return tuple (`translation function`, `lang.name`) for language.
    LANG (opt.) language {en|ru (locale lang default)}.
    TR (opt.) translation file (dbcarta default)."""
    _ = lambda msg : msg
    try:
        if not lang:
            import locale
            lang = locale.getdefaultlocale()[0].split('_')[0]
        if lang == 'ru':
            import gettext
            g = gettext.translation(tr, os.path.join(sys.path[0], 'i18n', 'locale'), (lang,))
            if sys.version_info[0] == 3:
                _ = g.gettext
            else:
                _ = lambda msg : g.gettext(msg.decode('utf8'))
    except:
        pass
    return _

def startCarta():
    """Create dbCarta instance.
    Return tuple of instances (`dbCarta`,`Main window`)."""
    master = Tk()
    master.columnconfigure(0, weight=1)
    master.rowconfigure(0, weight=1)
    _dbcarta = dbCarta(master)
    return (_dbcarta, master)

if __name__ == '__main__':
    dw, master = startCarta()
    dw.loadCarta(dw.createMeridians())
    dw.centerCarta()
    master.mainloop()
    master.destroy()
