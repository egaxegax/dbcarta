#!/usr/bin/env python
# -*- coding: koi8-r -*-
# egax

import os, os.path, sys, qt

IN_DIR='.'
OUT_DIR='xpm'

#codec = qt.QTextCodec().codecForLocale()
app = qt.QApplication(sys.argv)
os.chdir(IN_DIR)
if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)
for in_file in os.listdir('.'):
    print(in_file, qt.QPixmap(in_file).save(OUT_DIR + '/' + in_file[:len(in_file) - 3] + 'xpm', "XPM"))
		    
