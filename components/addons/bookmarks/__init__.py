# -*- coding: utf-8 -*-

from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import os

if os.getenv('LOGNAME') == 'DIGITALIDEA\\d10218':
    
    sys.path.append( '/home/d10218/work/ipipeline' )
    from foundations.globals.constants import Constants
else :    
    from foundations.globals.constants import Constants


class Bookmarks( QFrame ):
    def __init__(self , parent = None ):
        QFrame.__init__( self , parent )
        uic.loadUi(Constants.bookmark_ui, self)
        
    def addbmItem( showcode , level1 , level2 , level3 ):
        result = '_'.join( [showcode,level1,level2,level3] )
        item = QListWidgetItem( result )
        self.bm_list.addItem( item )
        
    def delbmItem( item ):
        self.bm_list.removeItemWidget( self.bm_list.currentItem )
            
        
        
        

def bookmark_console():
    app = QApplication(sys.argv)
    mainWin = Bookmarks()   
    mainWin.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    bookmark_console()