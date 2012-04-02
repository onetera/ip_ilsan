# -*- coding: utf-8 -*-

"""
**animImport.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    Geo Bake Module.

**Others:**

"""
#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import os
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
#***    Module classes and definitions.
#***********************************************************************************************
class GeoBake(QDialog):

    def __init__(self, start_frame, end_frame, location, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(Constants.applicationDirectory+"components/tools/finalize/geoBake/ui/Geo_Bake.ui", self)

        # set the variables
        self.lineEdit_startFrame.setText(QString.number(start_frame))
        self.lineEdit_endFrame.setText(QString.number(end_frame))
        self.lineEdit_location.setText(location)

        self.connect(self.toolButton_location, SIGNAL("clicked()"), self.locationButton)

        self.setWindowTitle("geoBake")

    def locationButton(self):
        dirName = QFileDialog.getExistingDirectory(self, QString.fromLocal8Bit("저장할 위치를 지정하세요."), self.lineEdit_location.text())
        if dirName:
            self.lineEdit_location.setText(dirName)

    def accept(self):
        startFrame = self.lineEdit_startFrame.text()
        endFrame = self.lineEdit_endFrame.text()
        location = self.lineEdit_location.text()

        try:
            startFrame = int(startFrame)
            endFrame = int(endFrame)
        except:
            QMessageBox.warning(self, QString.fromLocal8Bit("경고"),
                                QString.fromLocal8Bit("[startFrame, endFrame] 숫자만 입력하세요."))
            return

        if not QDir(location).exists():
            msg = QMessageBox.question(self, QString.fromLocal8Bit("디렉토리생성"),
                    QString.fromLocal8Bit("%s\n디렉토리가 존재하지 않습니다. 생성하시겠습니까?" % str(location)),
                    QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Ok:
                os.makedirs(str(location))
            else:
                return

        try:
            mel.eval('DI_geoBake %s %s "%s"' % (startFrame, endFrame, location))
        except:
            pass

        QMessageBox.information(self, QString.fromLocal8Bit("성공"),
                            QString.fromLocal8Bit("geoBake가 완료되었습니다."))

        self.close()

        print 'through'

    def errorMessage(self):
        QMessageBox.warning(self, QString.fromLocal8Bit("경고"),
                            QString.fromLocal8Bit("리스트에 아무런 데이터가 없습니다."))
