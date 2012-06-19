# -*- coding:utf-8 -*-




from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys




try : 
    import maya.cmds as cmds
    MAYA = 1
except : 
    MAYA = 0


class Notice( QDialog ):
    def __init__(self  ,  message , count =5 , parent = None   ):
        QDialog.__init__( self , parent )        
        
        self.parent = parent
        self.count = count
        self.message = unicode( message )
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label.setText( self.message )
        self.label.setFont(QFont('Arial' , 14) )

                
        self.close_btn = QPushButton( self )
        self.close_btn.setText( 'close' )
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.close_btn.sizePolicy().hasHeightForWidth())        
        self.close_btn.setSizePolicy(sizePolicy)
        self.close_btn.setBaseSize(QSize(3, 0))
        self.close_btn.clicked.connect( lambda evt :self.closeEvent( evt ) )
                
                
        self.gridLayout = QGridLayout( self )   
        self.gridLayout.addWidget(self.close_btn, 1, 2, 1, 1)        
#        self.gridLayout.addWidget(self.checkBox, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        
        self.loadSettings()
              
#        self.openCount = 0  
        
        self.resize( 300 , 100 )        
        self.setWindowTitle( 'Notice' )
        if self.openCount < 5:
            self.show()        
      
    def loadSettings(self):
        settings = QSettings("DIGITAL idea", "Notice")
        if settings.contains("openCount"):
#            self.openCount = settings.value("openCount").toInt()
            self.openCount = int( settings.value("openCount").toString() )
        
    def closeEvent(self, event):
        settings = QSettings("DIGITAL idea", "Notice")
        settings.setValue('openCount' , self.openCount + 1 )        
        self.close()
    
    def resetSettings(self):
        settings = QSettings("DIGITAL idea", "Notice")
        settings.setValue('openCount' , 0 )
        
    

    
def notice( message  , count =5, parent = None ):
    if MAYA:
        global app    
        try:        
            app.close()        
        except :        
            app = Notice( message=message , count =  count , parent = parent )
#        app.show()
    else : 
        app = QApplication(sys.argv)
        mainWin = Notice( message=message , count =  count , parent = parent )
#        mainWin.show()
        sys.exit(app.exec_())    



if __name__ == '__main__':
    message = '''
테스트 테스트
테스트
테스트임
'''
    
    notice(  message  )
#    notice.resetSettings()
    
    