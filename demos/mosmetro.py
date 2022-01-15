#!/usr/bin/env python
"""
Moscow Metro Map 2022.
Ported from https://github.com/egaxegax/dbcartajs project.
"""

from __init__ import *
from dbcarta import *
from data.mosmetro import *

_ = setLanguage(tr='mosmetro')

def create_dbcarta(master, **kw):
    global dw
    dw = dbCarta(master, **kw)

def create_tlist(master):
    master.title(_('Stations'))
    master.geometry('200x800+%s+%s' % (10, 20))
    fmain = Frame(master)
    fmain.pack(fill='both', expand=1)
    fmain.columnconfigure(0, weight=1)
    fmain.rowconfigure(0, weight=1)
    global tlist
    tlist = TableList(fmain, 
        activestyle = 'none', 
        columns = (0, '#', 10, _('Station'), -1, _('Abbr')),
        setfocus=1, 
        selectmode='extended', 
        selecttype='row', 
        stretch = 'all',
        stripebackground='#e0e8f0',
        width=50)
    def sortbycolumn(table, col):
        order = "-increasing"
        if tlist.sortcolumn() == int(col) and tlist.sortorder() == "increasing":
            order = "-decreasing"
        tlist.sortbycolumn(col, order)
    def showcoord():
        try:    cursel = tlist.getcurselection()
        except: cursel = ()
        for row in cursel:
            n, label, key = row
            for ftag, value in dw.mflood.items():
                if key in ftag:
                    dw.centerCarta([value['coords'][0]])
    tlist.configure(labelcommand=sortbycolumn)
    tlist.bind('<<TablelistSelect>>', (lambda event: showcoord()))
    tlist.columnconfigure(0, sortmode='integer')
    tlist.grid(column=0, row=0, sticky='nsew')
    scroll_y = Scrollbar(fmain, orient='vertical', command=tlist.yview)
    scroll_y.grid(column=1, row=0, sticky='ns')
    tlist.config(yscrollcommand=scroll_y.set)

def fill_tlist():
    for row in MSTATIONS:
        key, label = row[1], row[1]
        if len(row) > 3 and row[3]:
            label = row[3]
        tlist.insert('end', tuple([tlist.index('end'), label, key]))

root = Tk()
root.geometry('1000x800+%s+%s' % (220, 20))
root.protocol('WM_DELETE_WINDOW', root.quit)
create_dbcarta(root, bg='white', viewportx=450, viewporty=450)
root.title('Moscow Metro 2022')
dw.slider.var.set(dw.slider.var.get() * 2.0)
dw.scaleCarta()
dw.centerCarta()
# define new layers
route = lambda o: o.update({'cls': 'Line', 'width': o.get('width', 5), 'anchor': o.get('anchor', 'w')}) or o
route_ext = lambda o: route(o.update({'dash': [2,4]}) or o)
inch = lambda o: route(o.update({'fg': o.get('fg', '#ddd'), 'bg': 'white', 'width': o.get('width', 5)}) or o)
inch_ext = lambda o: inch(o.update({'dash': [3,1], 'width': 3}) or o)
river = lambda o: route(o.update({'fg': '#daebf4', 'smooth': 1, 'labelcolor': '#5555ff'}) or o)
rail = lambda o: route(o.update({'cls': 'Line', 'fg': o.get('fg', '#ccc'), 'width': 1}) or o)
rail_d = lambda o: rail(o.update({'fg': '#fff', 'dash': [5,5]}) or o)
label = lambda o: o.update({'cls': 'Dot', 'labelcolor': '#aaa', 'fg': o.get('fg', '#fff'), 'anchor': o.get('anchor', 'w')}) or o
station = lambda o: o.update({'cls': 'Dot', 'fg': o.get('fg', '#000'), 'bg': o.get('bg', 'white'), 'size': o.get('size', 3), 'width': o.get('width', 1), 'labelscale': 1}) or o
st_mck = lambda o: station({'fg': '#f76093', 'size': o.get('size', 2), 'labelcolor': '#aaa', 'anchor': o.get('anchor', 'w')}) or o
st_mcd = lambda o: station({'size': 1, 'labelcolor': '#aaa', 'anchor': o.get('anchor', 'w')}) or o    
inch_mck = lambda o: inch(o.update({'dash': [2,3], 'width': 2}) or o)
inch_mn = lambda o: inch(o.update({'dash': [1,1], 'fg': '#000', 'width': 2}) or o)
inch_mcd = lambda o: inch(o.update({'dash': [1,2], 'fg': '#aaa', 'width': 2}) or o)
inst_mck = lambda o: st_mck(o.update({'size': 2, 'labelcolor': o['fg'], 'bg': o['fg']}) or o)
inst_mcd = lambda o: st_mcd(o.update({'size': 1, 'labelcolor': o['fg'], 'bg': o['fg']}) or o)
inst = lambda o: station(o.update({'size': o.get('size', 3), 'labelcolor': o['fg'], 'bg': o['fg']}) or o)
inst_d = lambda o: inst(o.update({'size': 2, 'width': 1}) or o)
# lines
dw.mopt.update({
    'r1':        route({'fg': '#ed1b35'}),
    'r1_ext':    route_ext({'fg': '#ed1b35'}),
    'r2':        route({'fg': '#44b85c'}),
    'r2_ext':    route_ext({'fg': '#44b85c'}),
    'r3':        route({'fg': '#0078bf'}),
    'r3_ext':    route_ext({'fg': '#0078bf'}),
    'r4':        route({'fg': '#19c1f3'}),
    'r4A':       route({'fg': '#19c1f3'}),
    'r5':        route({'fg': '#894e35'}),
    'r6':        route({'fg': '#f58631'}),
    'r6_ext':    route_ext({'fg': '#f58631'}),
    'r7':        route({'fg': '#8e479c'}),
    'r7_ext':    route_ext({'fg': '#8e479c'}),
    'r8':        route({'fg': '#ffcb31'}),
    'r8_ext':    route_ext({'fg': '#ffcb31'}),
    'r9':        route({'fg': '#a1a2a3'}),
    'r10':       route({'fg': '#b3d445'}),
    'r10_ext':   route_ext({'fg': '#b3d445'}),
    'r11':       route({'fg': '#79cdcd'}),
    'r11_ext':   route_ext({'fg': '#79cdcd'}),
    'r11A':      route({'fg': '#79cdcd'}),
    'r12':       route({'fg': '#acbfe1'}),
    'r12_ext':   route_ext({'fg': '#acbfe1'}),
    'r13':       route({'fg': '#2c87c5', 'width': 2}),
    'r14':       rail({'fg': '#f76093', 'width': 2}),
    'r14_d':     rail_d({'width':2}),
    'r15':       route({'fg': '#de62be'}),
    'r16':       route({'fg': '#554d26'}),
    'r16_ext':   route_ext({'fg': '#554d26'}),
    'inch':      inch({}),
    'inch_ext':  inch_ext({}),
    'inch_mck':  inch_mck({}),
    'inch_mn':   inch_mn({}),
    'inch_mcd':  inch_mcd({}),
    'mkad':      route({'fg': '#c8c8ff', 'width': 1}),
    'moskvar':   river({'width': 15}),
    'moskvac':   river({'width': 5}),
    'strogino':  river({'width': 5}),
    'vodootvod': river({'width': 5}),
    'yauza':     river({'width': 5}),
    'nagatino':  river({'width': 6}),
    'grebnoy':   river({'width': 3}),
    'moskvar_t': river({'rotate': 48, 'anchor': 'nw'}),
    'moskvac_t': river({'rotate': -90, 'anchor': 'w'}),
    'yauza_t':   river({'rotate': 45, 'anchor': 'nw'}),
    't':         rail({}),
    't_d':       rail_d({}),
    'rd1':       rail({'fg': '#fa842f'}),
    'rd1_d':     rail_d({}),
    'rd2':       rail({'fg': '#29c0d3'}),
    'rd2_d':     rail_d({}),
    'svo_t':     label({'anchor': 'e'}),
    'svo_d_t':   label({'anchor': 'ne'}),
    'vko_t':     label({'anchor': 'w'}),
    'vko_d_t':   label({'anchor': 'n'}),
    'dme_t':     label({'anchor': 'w'}),
    'dme_d_t':   label({'anchor': 'n'})      ,
    'mkad_t':    label({'anchor': 'n'}),
})
# stations
dw.mopt.update({
    's1':        station({'fg': dw.mopt['r1']['fg'], 'anchor': 'w'}),
    's1_1':      inst({'fg': dw.mopt['r1']['fg'], 'anchor': 'w'}),
    's1_2':      inst({'fg': dw.mopt['r1']['fg'], 'anchor': 'e'}),
    's1_4':      inst({'fg': dw.mopt['r1']['fg'], 'anchor': 'nw'}),
    's1_5':      station({'fg': dw.mopt['r1']['fg'], 'anchor': 'e'}),
    's1_6':      station({'fg': dw.mopt['r1']['fg'], 'anchor': 'nw'}),
    's1_7':      station({'fg': dw.mopt['r1']['fg']}),
    's1_8':      station({'fg': dw.mopt['r1']['fg'], 'anchor': 'sw'}),
    's2':        station({'fg': dw.mopt['r2']['fg'], 'anchor': 'w'}),
    's2_1':      station({'fg': dw.mopt['r2']['fg']}),
    's2_2':      inst({'fg': dw.mopt['r2']['fg'], 'anchor': 'e'}),
    's2_3':      inst({'fg': dw.mopt['r2']['fg']}),
    's2_4':      station({'fg': dw.mopt['r2']['fg'], 'anchor': 'e'}),
    's2_6':      station({'fg': dw.mopt['r2']['fg'], 'anchor': 'nw'}),
    's2_7':      inst({'fg': dw.mopt['r2']['fg'], 'anchor': 'ne'}),
    's3':        station({'fg': dw.mopt['r3']['fg'], 'anchor': 'w'}),
    's3_1':      station({'fg': dw.mopt['r3']['fg'], 'anchor': 'e'}),
    's3_3':      inst({'fg': dw.mopt['r3']['fg'], 'anchor': 'se'}),
    's3_4':      inst({'fg': dw.mopt['r3']['fg'], 'anchor': 'sw'}),
    's3_5':      inst({'fg': dw.mopt['r3']['fg'], 'anchor': 'ne'}),
    's3_7':      inst({'fg': dw.mopt['r3']['fg'], 'anchor': 'e'}),
    's3_8':      inst({'fg': dw.mopt['r3']['fg'], 'anchor': 'se'}),
    's4':        station({'fg': dw.mopt['r4']['fg'], 'anchor': 'w'}),
    's4_1':      station({'fg': dw.mopt['r4']['fg'], 'anchor': 'e'}),
    's4_2':      inst({'fg': dw.mopt['r4']['fg'], 'anchor': 'e'}),
    's4_3':      station({'fg': dw.mopt['r4']['fg'], 'anchor': 'sw'}),
    's4_5':      inst_d({'fg': dw.mopt['r4']['fg']}),
    's4_6':      station({'fg': dw.mopt['r4']['fg'], 'anchor': 'se'}),
    's4_7':      station({'fg': dw.mopt['r4']['fg'], 'anchor': 'ne'}),
    's4A':       station({'fg': dw.mopt['r4A']['fg'], 'anchor': 'w'}),
    's4A_1':     inst({'fg': dw.mopt['r4A']['fg'], 'anchor': 'sw'}),
    's4A_2':     inst({'fg': dw.mopt['r4A']['fg'], 'anchor': 'e'}),
    's5':        inst({'fg': dw.mopt['r5']['fg']}),
    's5_1':      inst({'fg': dw.mopt['r5']['fg'], 'anchor': 'se'}),
    's5_2':      inst({'fg': dw.mopt['r5']['fg'], 'anchor': 'w'}),
    's6':        station({'fg': dw.mopt['r6']['fg'], 'anchor': 'w'}),
    's6_1':      station({'fg': dw.mopt['r6']['fg'], 'anchor': 'e'}),
    's6_2':      inst({'fg': dw.mopt['r6']['fg'], 'anchor': 'w'}),
    's6_3':      inst({'fg': dw.mopt['r6']['fg'], 'anchor': 'se'}),
    's6_4':      inst({'fg': dw.mopt['r6']['fg'], 'anchor': 'nw'}),
    's6_5':      inst({'fg': dw.mopt['r6']['fg'], 'anchor': 'e'}),
    's6_6':      inst({'fg': dw.mopt['r6']['fg'], 'anchor': 'ne'}),
    's6_7':      inst({'fg': dw.mopt['r6']['fg'], 'anchor': 'sw'}),
    's7':        station({'fg': dw.mopt['r7']['fg'], 'anchor': 'e'}),
    's7_1':      inst({'fg': dw.mopt['r7']['fg'], 'anchor': 'e'}),
    's7_2':      inst({'fg': dw.mopt['r7']['fg'], 'anchor': 'sw'}),
    's7_3':      inst({'fg': dw.mopt['r7']['fg'], 'anchor': 'nw'}),
    's7_4':      station({'fg': dw.mopt['r7']['fg'], 'anchor': 'sw'}),
    's7_5':      inst_d({'fg': dw.mopt['r7']['fg']}),
    's7_6':      station({'fg': dw.mopt['r7']['fg'], 'anchor': 'w'}),
    's7_7':      station({'fg': dw.mopt['r7']['fg'], 'anchor': 'se'}),
    's7_8':      station({'fg': dw.mopt['r7']['fg'], 'anchor': 'ne'}),
    's7_9':      station({'fg': dw.mopt['r7']['fg']}),
    's7_10':     inst({'fg': dw.mopt['r7']['fg']}),
    's7_11':     inst({'fg': dw.mopt['r7']['fg'], 'anchor': 'ne'}),
    's8':        station({'fg': dw.mopt['r8']['fg'], 'anchor': 'w'}),
    's8_1':      inst({'fg': dw.mopt['r8']['fg'], 'anchor': 'w'}),
    's8_2':      inst({'fg': dw.mopt['r8']['fg'], 'anchor': 'nw'}),
    's8_3':      inst({'fg': dw.mopt['r8']['fg']}),
    's8_4':      inst({'fg': dw.mopt['r8']['fg'], 'anchor': 'e'}),
    's8_5':      inst({'fg': dw.mopt['r8']['fg'], 'anchor': 'se'}),
    's8_6':      inst_d({'fg': dw.mopt['r8']['fg']}),
    's9':        station({'fg': dw.mopt['r9']['fg'], 'anchor': 'w'}),
    's9_1':      inst({'fg': dw.mopt['r9']['fg'], 'anchor': 'e'}),
    's9_2':      inst({'fg': dw.mopt['r9']['fg'], 'anchor': 'w'}),
    's9_3':      inst({'fg': dw.mopt['r9']['fg'], 'anchor': 'nw'}),
    's9_4':      station({'fg': dw.mopt['r9']['fg'], 'anchor': 'e'}),
    's9_5':      inst({'fg': dw.mopt['r9']['fg'], 'anchor': 'sw'}),
    's9_6':      inst({'fg': dw.mopt['r9']['fg'], 'anchor': 'se'}),
    's10':       station({'fg': dw.mopt['r10']['fg'],  'anchor': 'e'}),
    's10_1':     station({'fg': dw.mopt['r10']['fg'], 'anchor': 'w'}),
    's10_2':     inst({'fg': dw.mopt['r10']['fg'], 'anchor': 'w'}),
    's10_3':     inst({'fg': dw.mopt['r10']['fg'], 'anchor': 'n'}),
    's10_4':     inst_d({'fg': dw.mopt['r10']['fg']}),
    's10_5':     station({'fg': dw.mopt['r10']['fg'],  'anchor': 'ne'}),
    's11':       station({'fg': dw.mopt['r11']['fg'], 'anchor': 'nw'}),
    's11_1':     station({'fg': dw.mopt['r11']['fg'], 'anchor': 'w'}),
    's11_2':     station({'fg': dw.mopt['r11']['fg'], 'anchor': 'e'}),
    's11_3':     inst({'fg': dw.mopt['r11']['fg']}),
    's11_4':     inst({'fg': dw.mopt['r11']['fg'], 'anchor': 'sw'}),
    's11_5':     inst_d({'fg': dw.mopt['r11']['fg']}),
    's11_6':     station({'fg': dw.mopt['r11']['fg'], 'anchor': 'se'}),
    's11_7':     inst({'fg': dw.mopt['r11']['fg'], 'anchor': 'w'}),
    's11_8':     station({'fg': dw.mopt['r11']['fg'], 'anchor': 'se'}),
    's11_9':     inst({'fg': dw.mopt['r11']['fg'], 'anchor': 'e'}),
    's11_10':    station({'fg': dw.mopt['r11']['fg'], 'anchor': 'sw'}),
    's11_11':    inst({'fg': dw.mopt['r11']['fg'], 'anchor': 'nw'}),
    's11_12':    inst({'fg': dw.mopt['r11']['fg'], 'anchor': 'ne'}),
    's11_13':    inst({'fg': dw.mopt['r11']['fg'], 'anchor': 'n'}),
    's11_14':    inst({'fg': dw.mopt['r11']['fg'], 'anchor': 'se'}),
    's11_15':    station({'fg': dw.mopt['r11']['fg'], 'anchor': 'n'}),
    's11A':      inst_d({'fg': dw.mopt['r11A']['fg']}),
    's11A_1':    station({'fg': dw.mopt['r11A']['fg'], 'anchor': 'se'}),
    's11A_2':    inst({'fg': dw.mopt['r11A']['fg'], 'anchor': 'e'}),    
    's12':       station({'fg': dw.mopt['r12']['fg'], 'anchor': 'se'}),
    's12_1':     station({'fg': dw.mopt['r12']['fg'], 'anchor': 'n'}),
    's12_2':     station({'fg': dw.mopt['r12']['fg'], 'anchor': 'nw'}),
    's12_3':     inst({'fg': dw.mopt['r12']['fg']}),
    's12_4':     station({'fg': dw.mopt['r12']['fg'], 'anchor': 'ne'}),
    's12_5':     inst({'fg': dw.mopt['r12']['fg'], 'anchor': 'nw'}),
    's13':       inst({'fg': dw.mopt['r13']['fg'], 'size': 2, 'anchor': 'n'}),
    's13_1':     inst({'fg': dw.mopt['r13']['fg'], 'size': 2, 'anchor': 'w'}),
    's14':       st_mck({'anchor': 'w'}),
    's14_1':     st_mck({'anchor': 'nw'}),
    's14_2':     st_mck({'anchor': 'e'}),
    's14_3':     st_mck({'anchor': 'se'}),
    's14_4':     st_mck({'anchor': 'sw'}),
    's14_5':     inst_mck({'fg': dw.mopt['r14']['fg'], 'anchor': 'w'}),
    's14_6':     inst_mck({'fg': dw.mopt['r14']['fg'], 'anchor': 'nw'}),
    's14_7':     inst_mck({'fg': dw.mopt['r14']['fg'], 'anchor': 'e'}),
    's14_8':     inst_mck({'fg': dw.mopt['r14']['fg'], 'anchor': 'se'}),
    's14_9':     inst_mck({'fg': dw.mopt['r14']['fg'], 'anchor': 'sw'}),
    's15':       station({'fg': dw.mopt['r15']['fg'], 'anchor': 'w'}),
    's15_1':     station({'fg': dw.mopt['r15']['fg'], 'anchor': 'e'}),
    's15_2':     inst({'fg': dw.mopt['r15']['fg'], 'anchor': 'w'}),
    's15_3':     inst_d({'fg': dw.mopt['r15']['fg'], 'anchor': 'w'}),
    's16':       station({'fg': dw.mopt['r16']['fg'], 'anchor': 'w'}),
    's16_1':     inst({'fg': dw.mopt['r16']['fg'], 'anchor': 'nw'}),
    's16_2':     inst_d({'fg': dw.mopt['r16']['fg'], 'anchor': 'nw'}),
    'sd1':       st_mcd({'fg': dw.mopt['rd1']['fg'], 'anchor': 'w'}),
    'sd2':       st_mcd({'fg': dw.mopt['rd2']['fg'], 'anchor': 'w'}),
    'sd2_1':     inst_mcd({'fg': dw.mopt['rd2']['fg']})
})
dw.loadCarta(MLINES)
dw.loadCarta(MLABELS)
dw.loadCarta(MSTATIONS)
master = Toplevel()
create_tlist(master)
fill_tlist()
root.mainloop()
root.destroy()
