# -*- coding: utf-8 -*-

"""
**ipipeline.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    UI common Module.

**Others:**

"""

#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
def startDrag(output, dragSource):
    data = QByteArray()
    stream = QDataStream(data, QIODevice.WriteOnly)
    stream << QString(output)
    mimeData = QMimeData()
    mimeData.setData("application/x-text", data)
    drag = QDrag(dragSource)
    drag.setMimeData(mimeData)
    drag.start(Qt.CopyAction)

