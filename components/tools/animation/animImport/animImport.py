# -*- coding: utf-8 -*-

"""
**animImport.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    Anim Import Module.

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
class AnimImport(QDialog):

    def __init__(self, tab, devFolder, pubFolder, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(Constants.applicationDirectory+"components/tools/animation/animImport/ui/Anim_Import.ui", self)

        self.tab = tab
        self.devFolder = devFolder
        self.pubFolder = pubFolder

        devScriptFolder = os.path.join(devFolder, "script")
        devAnimFolder = os.path.join(devFolder, "data", "anim")
        pubScriptFolder = os.path.join(pubFolder, "script")
        pubAnimFolder = os.path.join(pubFolder, "data", "anim")

        devTxtList = self.getFiles(devScriptFolder, "devel", "txt")
        pubTxtList = self.getFiles(pubScriptFolder, "publish", "txt")
        devAnimList = self.getFiles(devAnimFolder, "devel", "anim")
        pubAnimList = self.getFiles(pubAnimFolder, "publish", "anim")
        
        self.Devel_Txt_comboBox.addItems(devTxtList)
        self.Devel_Anim_comboBox.addItems(devAnimList)
        self.Publish_Txt_comboBox.addItems(pubTxtList)
        self.Publish_Anim_comboBox.addItems(pubAnimList)

        self.connect(self.Devel_Import_pushButton, SIGNAL("clicked()"),
                     lambda: self.importClicked(devScriptFolder, self.Devel_Txt_comboBox.currentText(), devAnimFolder, self.Devel_Anim_comboBox.currentText()))
        self.connect(self.Publish_Import_pushButton, SIGNAL("clicked()"),
                     lambda: self.importClicked(pubScriptFolder, self.Publish_Txt_comboBox.currentText(), pubAnimFolder, self.Publish_Anim_comboBox.currentText()))
        self.connect(self.Close_pushButton, SIGNAL("clicked()"),
                     self.close)

    def importClicked(self, scriptFolder, txtFile, animFolder, animFile):
        if self.tab == 1:
            enableNamespace = 1
        elif self.tab == 2:
            enableNamespace = 0
        if len(txtFile) and len(animFile):
            txtFile = os.path.join(str(scriptFolder), str(txtFile))
            animFile = os.path.join(str(animFolder), str(animFile))
            mel.eval('DI_selection %s "%s"' % (enableNamespace, txtFile))
            mel.eval('DI_animImport "%s"' % animFile)
        else:
            print "// Warning: Couldn't find file."

    def getFiles(self, path, mode, ext):
        children = QDir(path).entryList(QDir.Files|QDir.NoDotAndDotDot)
        #if mode == "devel":
        #    pattern_re = re.compile('v[\d]{2}_w[\d]{2}(.|_[\w]+.)%s$' % ext)
        #elif mode == "publish":
        #    pattern_re = re.compile('v[\d]{2}(.|_[\w]+.)%s$' % ext)
        pattern_re = re.compile('.%s' % ext)
        return sorted(filter(pattern_re.search, children), reverse=True)

