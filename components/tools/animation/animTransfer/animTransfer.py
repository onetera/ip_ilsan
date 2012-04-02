# -*- coding: utf-8 -*-

"""
**animTransfer.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    Anim Transfer Module.

**Others:**

"""

#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import os
import sys
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
try:
    import maya.cmds as cmds
    import maya.mel as mel
except ImportError:
    pass

#***********************************************************************************************
#***    Internal imports.
#***********************************************************************************************
from foundations.globals.constants import Constants

#***********************************************************************************************
#***    Module attributes.
#***********************************************************************************************
__author__ = "Seo Jungwook"
__copyright__ = "Copyright (C) 2011 - Seo Jungwook"
__maintainer__ = "Seo Jungwook"
__email__ = "rndvfx@gmail.com"
__status__ = "Production"

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
class AnimTransfer(QDialog):
    """
    This class is the **DI_aniTransfer** class.
    """

    def __init__(self, alone=None, parent=None):
        """
        This method initializes the class.
        
        :param parent: ( QWidget )
        """
        super(AnimTransfer, self).__init__(parent)
        if alone is None:
            uic.loadUi(Constants.applicationDirectory+"components/tools/animation/animTransfer/ui/Anim_Transfer.ui", self)
        else:
            uic.loadUi(Constants.applicationDirectory+"components/tools/animation/animTransfer/ui/Anim_Transfer_Alone.ui", self)
        self.alone = alone
        self.tableWidget.setAcceptDrops(True)
        self.tableWidget.dropEvent = self.lwDropEvent
        self.tableWidget.dragMoveEvent = self.lwDragMoveEvent
        self.tableWidget.dragEnterEvent = self.lwDragEnterEvent
        
        self.createConnections()

    def createConnections(self):
        self.connect(self.removeButton, SIGNAL("clicked()"), self.removeItemSelected)

    def removeItemSelected(self):
        row = self.tableWidget.currentRow()
        if row >= 0:
            self.tableWidget.removeRow(row)

    def accept(self):
        buffer = []
        for row in range(self.tableWidget.rowCount()):
            path = str(self.tableWidget.item(row, 2).text())
            buffer.append('"'+ path + '"')

        if self.alone is None:
            if self.tableWidget.rowCount():
                res = ','.join(buffer)
                selectedAsset = "{"+res+"}"
    
                if self.wipButton.isChecked():
                    status = "WIP"
                    progress = 50
                elif self.tempButton.isChecked():
                    status = "TEMP"
                    progress = 10
                elif self.finishButton.isChecked():
                    status = "FINISH"
                    progress = 100
    
                ctime = 1
                application = 'iMaya'
    
                #self.parent().savePublish(self.commentText.toPlainText(), status, progress, ctime, application, selectedAsset)
                #def savePublish(self, develFile, publishFile, comment, status, progress, ctime, application, selectedAsset=[]):
                #self.emit(SIGNAL("run"), filename, self.commentTextEdit.toPlainText(), status, progress, ctime, application, self.subjectName)
                self.close()
            else:
                print "[debug] couldn't find assets."
        else:
            if self.tableWidget.rowCount():
                pass
            else:
                print "[debug] couldn't find assets."

    #===========================================================================
    # enable the drag and drop
    #===========================================================================
    def lwDragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-text"):
            event.accept()
        else:
            event.ignore()

    def lwDragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-text"):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def lwDropEvent(self, event):
        if event.mimeData().hasFormat("application/x-text"):
            data = event.mimeData().data("application/x-text")
            stream = QDataStream(data, QIODevice.ReadOnly)
            text = QString()
            stream >> text
            currSelected = text.split(":")
            if  len(self.tableWidget.findItems(currSelected[1], Qt.MatchExactly)):
                event.ignore()
            else:
                prod = QTableWidgetItem(currSelected[0])
                assetName = QTableWidgetItem(currSelected[1])
                scriptFolder = QDir(currSelected[2])
                if scriptFolder.exists():
                    scriptFiles = scriptFolder.entryList(QStringList("*.txt"), QDir.Files | QDir.NoDotAndDotDot)
                    if len(scriptFiles):
                        scriptFiles = sorted(scriptFiles, reverse=True)
                        filename = currSelected[2]+"/"+scriptFiles[0]
                    else:
                        filename = ""
                else:
                    filename = ""
                if filename == "":
                    QMessageBox.warning(self, "Error", "Couldn't find script file.")
                    event.ignore()
                else:
                    filename = QTableWidgetItem(filename)
                    i = self.tableWidget.rowCount()
                    self.tableWidget.setRowCount(i+1)
                    self.tableWidget.setItem(i, 0, prod)
                    self.tableWidget.setItem(i, 1, assetName)
                    self.tableWidget.setItem(i, 2, filename)
                    event.accept()
        else:
            event.ignore()
