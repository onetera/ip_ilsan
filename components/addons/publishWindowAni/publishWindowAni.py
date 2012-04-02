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
class PublishWindowAni(QDialog):
    """
    This class is the **DI_aniTransfer** class.
    """

    def __init__(self, level2, level3, subjectName, devel1, devel2, publishFile, o_filename, parent=None):
        """
        This method initializes the class.
        
        :param parent: ( QWidget )
        """
        super(PublishWindowAni, self).__init__(parent)
        uic.loadUi(Constants.applicationDirectory+"components/addons/publishWindowAni/ui/Publish_Window_Ani.ui", self)
        self.tableWidget.setAcceptDrops(True)
        self.tableWidget.dropEvent = self.lwDropEvent
        self.tableWidget.dragMoveEvent = self.lwDragMoveEvent
        self.tableWidget.dragEnterEvent = self.lwDragEnterEvent

        self.o_filename = o_filename

        self.level2 = level2
        self.level3 = level3
        self.subjectName = subjectName
        self.develSceneFolder = os.path.dirname(str(devel1))
        self.publishSceneFolder = os.path.dirname(str(publishFile))

        self.Devel1_lineEdit.setText(os.path.basename(devel1))
        self.Devel2_lineEdit.setText(os.path.basename(devel2))
        self.Publish_lineEdit.setText(os.path.basename(publishFile))

        if not QFileInfo(devel1).isFile():
            self.Devel1_label.setText('OK')
            self.Devel1_label.setStyleSheet("color: green")

        if not QFileInfo(devel2).isFile():
            self.Devel2_label.setText('OK')
            self.Devel2_label.setStyleSheet("color: green")

        if QFileInfo(publishFile).isFile():
            self.Publish_label.setText('already exists.')
            self.Publish_label.setStyleSheet("color: red")
        else:
            self.Publish_label.setText('OK')
            self.Publish_label.setStyleSheet("color: green")

        self.createConnections()

        self.loadSettings()

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

        if self.tableWidget.rowCount():
            res = ','.join(buffer)
            selectedAsset = "{"+res+"}"

            #if self.groupBox.isChecked():
            if self.Devel1_radioButton.isChecked():
                develFile = self.Devel1_lineEdit.text()
            elif self.Devel2_radioButton.isChecked():
                develFile = self.Devel2_lineEdit.text()
            #else:
            #    develFile = ""
    
            publishFile = self.Publish_lineEdit.text()
            if self.Publish_label.text() != "OK":
                if not self.confirmDialog("Confirm", "Are you sure you want to overwrite %s?" % publishFile):
                    return

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

            if not self.groupBox.isChecked():
                develFile = self.o_filename

            self.parent().savePublish(self.groupBox.isChecked(), self.checkBox_close.isChecked(), develFile, publishFile, self.commentText.toPlainText(), status, progress, ctime, application, selectedAsset)
            #self.parent().savePublish(self.commentText.toPlainText(), status, progress, ctime, application, selectedAsset)
            #def savePublish(self, develFile, publishFile, comment, status, progress, ctime, application, selectedAsset=[]):
            self.close()
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

    def confirmDialog(self, title, text):
        msg = QMessageBox.question(self, title, text, QMessageBox.Ok | QMessageBox.Cancel)
        if msg != QMessageBox.Ok:
            return False
        return True

    def closeEvent(self, e):
        settings = QSettings("DIGITAL idea", "iPipeline")
        settings.beginGroup("publish")
        settings.setValue("saveDevel", self.groupBox.isChecked())
        settings.setValue("closeFile", self.checkBox_close.isChecked())
        settings.endGroup()

    def loadSettings(self):
        settings = QSettings("DIGITAL idea", "iPipeline")
        settings.beginGroup("publish")
        if settings.contains("saveDevel"):
            self.groupBox.setChecked(settings.value("saveDevel").toBool())
        if settings.contains("closeFile"):
            self.checkBox_close.setChecked(settings.value("closeFile").toBool())