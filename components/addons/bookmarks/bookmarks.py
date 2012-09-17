# -*- coding: utf-8 -*-


from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys , os

   

if os.getenv('LOGNAME') == 'DIGITALIDEA\\d10218':
    import sys
    sys.path.append( '/home/d10218/work/ipipeline' )
    from foundations.globals.constants import Constants
else :    
    from foundations.globals.constants import Constants



class Bookmarks( QFrame ):
    def __init__(self , parent=None ):
        QFrame.__init__( self , parent )
        uic.loadUi(Constants.bookmark_ui, self)
        self.close()
        self.BMlist = []
        
        
    def addbmitem(self , showcode ,tap , level1 , level2 , level3):
        atype = 'asset' if tap == 1 else 'shot'
        result = '  '.join( [str(showcode) ,atype, str(level1) , str(level2) , str(level3) ])
        if not result in self.BMlist:        
            self.BMlist.append( result )        
            self.updateBMlist()
        

    def delbmitem(self , index ):
        temp = self.BMlist.pop( index )
        self.updateBMlist()
        return temp

    def updateBMlist(self):
        self.bookmark_list.clear()
        self.bookmark_list.addItems( self.BMlist )
        
    

def bookmark_console():
    app = QApplication(sys.argv)
    mainWin = Bookmarks()   
    mainWin.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    bookmark_console()    
    
    
    
    
             