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
class SelectionTool(QDialog):

    def __init__(self, tab, devFolder, pubFolder, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(Constants.applicationDirectory+"components/tools/animation/selectionTool/ui/Selection_Tool.ui", self)

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

    def SelectClicked(self, folder, fileName):
        if self.tab == 1:
            enableNamespace = 1
        elif self.tab == 2:
            enableNamespace = 0
        if len(fileName):
            each_sel = os.path.join(str(folder), str(fileName))
            mel.eval('DI_selection %s "%s"' % (enableNamespace, each_sel))
        else:
            print "// Warning: Couldn't find file."

    def getFiles(self, path, mode, ext):
        children = QDir(path).entryList(QDir.Files|QDir.NoDotAndDotDot)
        if mode == "devel":
            pattern_re = re.compile('v[\d]{2}_w[\d]{2}(.|_[\w]+.)%s$' % ext)
        elif mode == "publish":
            pattern_re = re.compile('v[\d]{2}(.|_[\w]+.)%s$' % ext)
        return sorted(filter(pattern_re.search, children), reverse=True)

