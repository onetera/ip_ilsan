# -*- coding: utf-8 -*-

"""
**selectionTool.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    Selection Tool Module.

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
class MultipleImportReference(QDialog):

    def __init__(self, tab, devFolder, pubFolder, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(Constants.applicationDirectory+"components/tools/animation/multipleImportReference/ui/Multiple_Import_Reference.ui", self)

        self.tab = tab
        self.devFolder = devFolder
        self.pubFolder = pubFolder

        devScriptFolder = os.path.join(devFolder, "script")
        pubScriptFolder = os.path.join(pubFolder, "script")
        devList = self.getFiles(devScriptFolder, "devel", "txt")
        pubList = self.getFiles(pubScriptFolder, "publish", "txt")
        
        self.Devel_comboBox.addItems(devList)
        self.Publish_comboBox.addItems(pubList)

        self.connect(self.Devel_Select_pushButton, SIGNAL("clicked()"),
                     lambda: self.SelectClicked(devScriptFolder, self.Devel_comboBox.currentText()))
        self.connect(self.Publish_Select_pushButton, SIGNAL("clicked()"),
                     lambda: self.SelectClicked(pubScriptFolder, self.Publish_comboBox.currentText()))
        self.connect(self.Close_pushButton, SIGNAL("clicked()"),
                     self.close)

    def accept(self):
        pass