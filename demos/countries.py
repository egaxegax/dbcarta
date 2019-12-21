#!/usr/bin/env python
"""
World countries.
"""

from __init__ import *
from dbcarta import *
from data.countriesd import *
from data.continents import *

def paint_dbcarta():
    cntrylist = list(COUNTRIES)
    cntrylist.sort()
    for _i, name, short_name, _icon in tlist.getcurselection():
        data = []
        icon = [None, icons.get(short_name)][check_legend_var.get()]
        legend = [None, name][check_legend_var.get()]
        for i, value in enumerate(COUNTRIES[cntrylist[int(_i)]]):
            data += [('Area', '%s.%s' % (short_name, i), value[1], value[2], [value[3]], icon)]
        dbcarta.loadCarta(data, docenter=1)

def clear_dbcarta():
    cntrylist = list(COUNTRIES)
    cntrylist.sort()
    ftags = []
    for ftag, value in dbcarta.mflood.items():
        if value['ftype'] == 'Area':
            for _i, name, short_name, _icon in tlist.getcurselection():
                for i, value in enumerate(COUNTRIES[cntrylist[int(_i)]]):
                    if ('Area_%s.%s' % (short_name, i)) in ftag:
                        ftags += [ftag]
    dbcarta.clearCarta(*ftags)

def create_dbcarta(master, **kw):
    global dbcarta
    dbcarta = dbCarta(master, **kw)
    return dbcarta

def create_tlist(master):
    fmain = Frame(master)
    fmain.pack(fill='both', expand=1)
    fmain.columnconfigure(0, weight=1)
    fmain.rowconfigure(0, weight=1)
    _ = setLanguage('', 'countries')
    global tlist
    tlist = TableList(fmain, 
        activestyle = 'none', 
        columns = (0, '#', 10, _('Country'), 0, _('Name'), 0, _('Flag')),
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
    tlist.configure(labelcommand=sortbycolumn)
    tlist.columnconfigure(0, sortmode='integer')
    tlist.grid(column=0, row=0, sticky='nsew')
    scroll_y = Scrollbar(fmain, orient='vertical', command=tlist.yview)
    scroll_y.grid(column=1, row=0, sticky='ns')
    tlist.config(yscrollcommand=scroll_y.set)

    global check_legend_var
    check_legend_var = IntVar()
    check_legend_var.set(1)
    check_legend = Checkbutton(fmain, text=_('With icon'), variable=check_legend_var)
    check_legend.grid(column=0,row=1)

    fbutt = Frame(fmain)
    fbutt.grid(column=0, row=2)
    btadd = Button(fbutt, text=_('Show'), command=paint_dbcarta)
    btadd.grid(column=0, row=0)
    btcls = Button(fbutt, text=_('Remove'), command=clear_dbcarta)
    btcls.grid(column=1, row=0)

def fill_tlist():
    """Fill country list."""
    global icons
    icons = {}
    _ = setLanguage('', 'countries')
    cntrylist = list(COUNTRIES)
    cntrylist.sort()
    for i, name in enumerate(cntrylist):
        short_name = COUNTRIES[name][0][2]
        try:
            icons[short_name] = PhotoImage(file=os.path.join(DEMOPATH, 'demodata', 'flags', short_name.lower() + '.gif'))
        except:
            pass
        tlist.insert('end', tuple([i, _(name), short_name]))
        tlist.cellconfigure('%s,3' % (i,), image=icons.get(short_name))
        i += 1

if __name__ == '__main__':
    root = Tk()
    dbcarta = create_dbcarta(root,
                             viewportx=500,
                             viewporty=250)
    dbcarta.changeProject(101)
    dbcarta.loadCarta(CONTINENTS)
    dbcarta.loadCarta(dbcarta.createMeridians())
    dbcarta.centerCarta([[-43,30]])
    create_tlist(root)
    fill_tlist()
    root.mainloop()
    