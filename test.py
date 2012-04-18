import os
import sys
import re
import shutil
import time
# third-party imports
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

def test():
    print 'save' 
    
app = QtGui.QApplication(sys.argv)

w = QtGui.QWidget()
buttonbox = QtGui.QDialogButtonBox( QtGui.QDialogButtonBox.Save )#, QtGui.QDialogButtonBox.Close)

buttonbox.setParent(w)
save_btn = buttonbox.addButton( QtGui.QDialogButtonBox.Save )
for x in dir(buttonbox):
    if x[0] != '_':
        print x
#w.connect( save_btn , QtCore.SIGNAL("clicked()"), test )
w.connect( buttonbox , QtCore.SIGNAL('saved()') ,  test )


w.resize(250, 150)
w.move(300, 300)
w.setWindowTitle('Simple')
w.show()

sys.exit(app.exec_())




