#!/usr/bin/env python
"""
Moscow Metro Map 2014.
Ported from dbCartajs project at github.com.
"""

from __init__ import *
from dbcarta import *
from demodata.mosmetro import *

def create_dbcarta(master, **kw):
    global _
    _ = setLanguage('', 'mosmetro')
    global dbcarta
    dbcarta = dbCarta(master, **kw)
    return dbcarta

def create_tlist(master):
    master.title(_('Station List'))
    fmain = Frame(master)
    fmain.pack(fill='both', expand=1)
    fmain.columnconfigure(0, weight=1)
    fmain.rowconfigure(0, weight=1)
    global tlist
    tlist = TableList(fmain, 
        activestyle = 'none', 
        columns = (0, '#', 10, _('Station'), 0, _('Name')),
        setfocus=1, 
        selectmode='extended', 
        selecttype='row', 
        stretch = 'all',
        stripebackground='#e0e8f0',
        width=50)
    def exitcmd(ev):
        dbcarta.clearLayers('UserLine')
    def sortbycolumn(table, col):
        order = "-increasing"
        if tlist.sortcolumn() == int(col) and tlist.sortorder() == "increasing":
            order = "-decreasing"
        tlist.sortbycolumn(col, order)
    def showcoord():
        ftype = 'UserLine'
        dbcarta.clearLayers(ftype)
        try:    cursel = tlist.getcurselection()
        except: cursel = ()
        for row in cursel:
            n, label, ftag = row
            coords = dbcarta.mflood[ftag]['coords']
            dbcarta.centerCarta(coords)
            left, top, right, bottom = dbcarta.viewsizeOf()
            try:    px, py = dbcarta.toPoints(coords, doscale=1)
            except: continue
            dbcarta.dw.create_line([left, py, right, py, px, py, px, top, px, bottom], tags=(ftype + '.1',ftype))
            dbcarta.dw.create_text([px, py], anchor=dbcarta.mopt[ftype]['anchor'], text=str(n), tags=(ftype + '.1',ftype))
    tlist.bind('<Destroy>', exitcmd)
    tlist.configure(labelcommand=sortbycolumn)
    tlist.columnconfigure(0, sortmode='integer')
    tlist.grid(column=0, row=0, sticky='nsew')
    scroll_y = Scrollbar(fmain, orient='vertical', command=tlist.yview)
    scroll_y.grid(column=1, row=0, sticky='ns')
    tlist.config(yscrollcommand=scroll_y.set)
    fbutt = Frame(fmain)
    fbutt.grid(column=0, row=2)
    btadd = Button(fbutt, text=_('Show'), command=showcoord)
    btadd.grid(column=0, row=0)

def fill_tlist():
    for ftag, value in dbcarta.mflood.items():
        if dbcarta.mopt[value['ftype']]['cls'] == 'Dot' and ftag[5] == 's':
            if value.get('label'):
                tlist.insert('end', tuple([tlist.index('end'), value['label'], ftag]))

if __name__ == '__main__':
    root = Tk()
    root.geometry('800x600+%s+%s' % (200, 50))
    dw = create_dbcarta(root, bg='white', viewportx=450, viewporty=450)
    root.title(_('Moscow Metro Map'))
    dw.slider.var.set(dw.slider.var.get() * 2.0)
    dw.scaleCarta()
    dw.centerCarta()
    # define new layers
    route = lambda o: o.update({'cls': 'Line', 'width': o.get('width', 5), 'anchor': o.get('anchor', 'w')}) or o
    route_d = lambda o: route(o.update({'dash': [2,4]}) or o)
    interchange = lambda o: route(o.update({'fg': o.get('fg', '#000000'), 'width': o.get('width', 8)}) or o)
    interchange_d = lambda o: interchange(o.update({'fg': '#FFFFFF', 'width': 6}) or o)
    river = lambda o: route(o.update({'fg': '#E2FCFC', 'smooth': 1, 'labelcolor': '#5555FF'}) or o)
    aeroexpress = lambda o: route(o.update({'fg': '#DDDDDD'}) or o)
    aeroexpress_d = lambda o: route(o.update({'fg': '#FFFFFF', 'width': 4, 'dash': [10,10]}) or o)
    station = lambda o: o.update({'cls': 'Dot', 'bg': o.get('bg', 'white'), 'size': o.get('size', 3), 'width': o.get('width', 3), 'labelscale': 1}) or o
    inst = lambda o: station(o.update({'size': o.get('size', 3), 'labelcolor': o['fg'], 'bg': o['fg']}) or o)
    inst_d = lambda o: inst(o.update({'size': 2, 'width': 1}) or o)
    # lines
    dw.mopt.update({
        'r1': route({'fg': '#ED1B35'}),
        'r2': route({'fg': '#44B85C'}),
        'r3': route({'fg': '#0078BF'}),
        'r4': route({'fg': '#19C1F3'}),
        'r5': route({'fg': '#894E35'}),
        'r6': route({'fg': '#F58631'}),
        'r7': route({'fg': '#8E479C'}),
        'r8': route({'fg': '#FFCB31'}),
        'r9': route({'fg': '#A1A2A3'}),
        'r10': route({'fg': '#B3D445'}),
        'r11': route({'fg': '#79CDCD'}),
        'r12': route({'fg': '#ACBFE1'}),
        'rTPK': route_d({'fg': '#554D26'}),
        'rKOZH': route_d({'fg': '#DE62BE'})
    })
    # lines ext
    dw.mopt.update({
        'r1_ext': route_d({'fg': dw.mopt['r1']['fg']}),
        'r2_ext': route_d({'fg': dw.mopt['r2']['fg']}),
        'r6_ext': route_d({'fg': dw.mopt['r6']['fg']}),
        'r7_ext': route_d({'fg': dw.mopt['r7']['fg']}),
        'r8_ext': route_d({'fg': dw.mopt['r8']['fg']}),
        'r10_ext': route_d({'fg': dw.mopt['r10']['fg']}),
        'r12_ext': route_d({'fg': dw.mopt['r12']['fg']})
    })
    # interchanges
    dw.mopt.update({
        'interchange': interchange({}),
        'interchange_d': interchange_d({})
    })
    # rivers
    dw.mopt.update({
        'moskva_canal': river({'width': 5, 'rotate': -90}),
        'strogino_lake_exit': river({'cls': 'Polygon', 'bg': river({})['fg'], 'width': 5}),
        'vodootvodny_canal': river({'width': 5}),
        'yauza_river': river({'width': 5, 'rotate': 45, 'anchor': 'nw'}),
        'Nagatino_Kozhukhovo': river({'width': 5}),
        'Nagatino_poyma': river({'width': 6}),
        'grebnoy_canal': river({'width': 3}),
        'moskva_river': river({'width': 15, 'rotate': 45, 'anchor': 'nw'})
    })
    # rails
    dw.mopt.update({
        'monorail': route({'fg': '#2C87C5', 'width': 2, 'labelcolor': '#2C87C5', 'anchor': 'sw'}),
        'monorail_legend': route({'fg': '#2C87C5', 'width': 2}),
        'sheremetyevo_express_line': aeroexpress({'anchor': 'e'}),
        'sheremetyevo_express_line_d': aeroexpress_d({'anchor': 'ne'}),
        'vnukovo_express_line': aeroexpress({'anchor': 'w'}),
        'vnukovo_express_line_d': aeroexpress_d({'anchor': 'n'}),
        'domodedovo_express_line': aeroexpress({'anchor': 'w'}),
        'domodedovo_express_line_d': aeroexpress_d({})
    })
    # stations
    dw.mopt.update({
        's1': station({'fg': dw.mopt['r1']['fg'], 'anchor': 'w'}),
        's1_1': inst({'fg': dw.mopt['r1']['fg'], 'anchor': 'w'}),
        's1_2': inst({'fg': dw.mopt['r1']['fg'], 'anchor': 'e'}),
        's1_3': inst({'fg': dw.mopt['r1']['fg'], 'anchor': 'sw'}),
        's1_4': inst({'fg': dw.mopt['r1']['fg'], 'anchor': 'nw'}),
        's2': station({'fg': dw.mopt['r2']['fg']}),
        's2_1': inst({'fg': dw.mopt['r2']['fg']}),
        's2_2': inst({'fg': dw.mopt['r2']['fg'], 'anchor': 'e'}),
        's2_3': inst({'fg': dw.mopt['r2']['fg'], 'anchor': 'sw'}),
        's2_4': station({'fg': dw.mopt['r2']['fg'], 'anchor': 'e'}),
        's2_5': inst({'fg': dw.mopt['r2']['fg'], 'anchor': 'ne'}),
        's2_6': station({'fg': dw.mopt['r2']['fg'], 'anchor': 'nw'}),
        's3': station({'fg': dw.mopt['r3']['fg'], 'anchor': 'w'}),
        's3_1': station({'fg': dw.mopt['r3']['fg'], 'anchor': 'e'}),
        's3_2': station({'fg': dw.mopt['r3']['fg'], 'anchor': 'ne'}),
        's3_3': inst({'fg': dw.mopt['r3']['fg'], 'anchor': 'sw'}),
        's3_4': inst({'fg': dw.mopt['r3']['fg'], 'anchor': 'sw'}),
        's3_5': inst({'fg': dw.mopt['r3']['fg'], 'anchor': 'ne'}),
        's3_6': inst({'fg': dw.mopt['r3']['fg'], 'anchor': 'w'}),
        's3_6': inst({'fg': dw.mopt['r3']['fg'], 'anchor': 'e'}),
        's4': station({'fg': dw.mopt['r4']['fg']}),
        's4_1': station({'fg': dw.mopt['r4']['fg'], 'anchor': 'ne'}),
        's4_2': inst({'fg': dw.mopt['r4']['fg'], 'anchor': 'e'}),
        's4_3': station({'fg': dw.mopt['r4']['fg'], 'anchor': 'sw'}),
        's4_4': inst({'fg': dw.mopt['r4']['fg'], 'anchor': 'ne'}),
        's4_5': inst_d({'fg': dw.mopt['r4']['fg']}),
        's4_6': station({'fg': dw.mopt['r4']['fg'], 'anchor': 's'}),
        's5': inst({'fg': dw.mopt['r5']['fg']}),
        's5_1': inst({'fg': dw.mopt['r5']['fg'], 'anchor': 'sw'}),
        's5_2': inst({'fg': dw.mopt['r5']['fg'], 'anchor': 'nw'}),
        's6': station({'fg': dw.mopt['r6']['fg'], 'anchor': 'w'}),
        's6_1': station({'fg': dw.mopt['r6']['fg'], 'anchor': 'e'}),
        's6_2': inst({'fg': dw.mopt['r6']['fg'], 'anchor': 'w'}),
        's6_3': inst({'fg': dw.mopt['r6']['fg'], 'anchor': 'sw'}),
        's6_4': inst({'fg': dw.mopt['r6']['fg'], 'anchor': 'nw'}),
        's6_5': inst({'fg': dw.mopt['r6']['fg'], 'anchor': 'e'}),
        's7': station({'fg': dw.mopt['r7']['fg'], 'anchor': 'e'}),
        's7_1': inst({'fg': dw.mopt['r7']['fg'], 'anchor': 'e'}),
        's7_2': inst({'fg': dw.mopt['r7']['fg'], 'anchor': 'sw'}),
        's7_3': inst({'fg': dw.mopt['r7']['fg'], 'anchor': 'nw'}),
        's7_4': station({'fg': dw.mopt['r7']['fg'], 'anchor': 'sw'}),
        's7_5': inst_d({'fg': dw.mopt['r7']['fg']}),
        's7_6': inst({'fg': dw.mopt['r7']['fg'], 'anchor': 'w'}),
        's7_7': station({'fg': dw.mopt['r7']['fg'], 'anchor': 's'}),
        's8': station({'fg': dw.mopt['r8']['fg'], 'anchor': 'w'}),
        's8_1': inst({'fg': dw.mopt['r8']['fg']}),
        's8_2': inst({'fg': dw.mopt['r8']['fg'], 'anchor': 'nw'}),
        's8_4': inst({'fg': dw.mopt['r8']['fg'], 'anchor': 'ne'}),
        's8_5': inst({'fg': dw.mopt['r8']['fg'], 'anchor': 'sw'}),
        's8_6': inst_d({'fg': dw.mopt['r8']['fg']}),
        's9': station({'fg': dw.mopt['r9']['fg'], 'anchor': 'w'}),
        's9_1': inst({'fg': dw.mopt['r9']['fg'], 'anchor': 'e'}),
        's9_2': inst({'fg': dw.mopt['r9']['fg'], 'anchor': 'w'}),
        's9_3': inst({'fg': dw.mopt['r9']['fg'], 'anchor': 'nw'}),
        's9_4': station({'fg': dw.mopt['r9']['fg'], 'anchor': 'e'}),
        's9_5': inst({'fg': dw.mopt['r9']['fg'], 'anchor': 'sw'}),
        's9_6': inst({'fg': dw.mopt['r9']['fg'], 'anchor': 'sw'}),
        's10': station({'fg': dw.mopt['r10']['fg'], 'anchor': 'e'}),
        's10_1': station({'fg': dw.mopt['r10']['fg'], 'anchor': 'w'}),
        's10_2': inst({'fg': dw.mopt['r10']['fg'], 'anchor': 'w'}),
        's10_3': inst({'fg': dw.mopt['r10']['fg'], 'anchor': 'ne'}),
        's10_4': inst_d({'fg': dw.mopt['r10']['fg']}),
        's11': station({'fg': dw.mopt['r11']['fg'], 'anchor': 's'}),
        's11_1': inst({'fg': dw.mopt['r11']['fg'], 'anchor': 'nw'}),
        's11_2': inst_d({'fg': dw.mopt['r11']['fg']}),
        's12': station({'fg': dw.mopt['r12']['fg'], 'anchor': 's'}),
        's12_1': station({'fg': dw.mopt['r12']['fg'], 'anchor': 'n'}),
        's12_2': station({'fg': dw.mopt['r12']['fg'], 'anchor': 'nw'}),
        's12_3': station({'fg': dw.mopt['r12']['fg'], 'anchor': 'e'}),
        's12_4': inst({'fg': dw.mopt['r12']['fg'], 'anchor': 'w'}),
        's12_5': inst({'fg': dw.mopt['r12']['fg'], 'anchor': 'nw'}),
        'sTPK': station({'fg': dw.mopt['rTPK']['fg'], 'anchor': 'nw'}),
        'sTPK_1': station({'fg': dw.mopt['rTPK']['fg'], 'anchor': 'sw'}),
        'sTPK_2': station({'fg': dw.mopt['rTPK']['fg'], 'anchor': 'e'}),
        'sTPK_3': inst({'fg': dw.mopt['rTPK']['fg'], 'anchor': 'w'}),
        'sTPK_4': inst({'fg': dw.mopt['rTPK']['fg'], 'anchor': 'sw'}),
        'sTPK_5': inst_d({'fg': dw.mopt['rTPK']['fg']}),
        'sTPK_6': station({'fg': dw.mopt['rTPK']['fg'], 'anchor': 's'}),
        'sTPK_7': station({'fg': dw.mopt['rTPK']['fg'], 'anchor': 'w'}),
        'sKOZH': station({'fg': dw.mopt['rKOZH']['fg'], 'anchor': 'w'}),
        'sKOZH_1': station({'fg': dw.mopt['rKOZH']['fg'], 'anchor': 'e'}),
        'sKOZH_2': inst({'fg': dw.mopt['rKOZH']['fg'], 'anchor': 'w'}),
        'sKOZH_3': inst_d({'fg': dw.mopt['rKOZH']['fg'], 'anchor': 'w'}),
        'sMono': inst({'fg': dw.mopt['monorail']['fg'], 'size': 1, 'anchor': 'nw'}),
        'sMono_1': inst({'fg': dw.mopt['monorail']['fg'], 'size': 1, 'anchor': 'w'})
    })
    dw.loadCarta(MLINES)
    dw.loadCarta(MSTATIONS)
    master = Toplevel()
    create_tlist(master)
    fill_tlist()
    root.mainloop()
