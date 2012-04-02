# -*- coding: utf-8 -*-

"""
**iPipelineInit.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    iPipelineInit Framework Module

**Others:**

"""

#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import sys
import os

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
class iPipelineInit(object):
    """
    This class is the **iPipelineInit** class.
    """

    def initialize(self):
        if sys.platform == "win32":
            self.userName = os.getenv('USERNAME')
        else:
            self.userName = os.getenv('USER')
        self.currProjectName = ""
        self.currentUser = "default"
        superUserList = ['higgsdecay', 'utd', 'wondermc', 'Administrator']
        self.isSuperUser = True if self.userName in superUserList else False
        if self.currProjectName == "":
            self.currOpenType = ""
            self.currOpenCategory = ""
            self.currOpenVersion = 0
            self.currOpenLevel1 = ""
            self.currOpenLevel2 = ""
            self.currOpenLevel3 = ""
            self.currOpenTab = 0
            self.currOpenProjectName = ""
            self.currProjectPath = ""
            self.libPath = ""
            self.shotPath = ""
            self.scriptsPath = ""
            self.rendersPath = ""
            self.particlesPath = ""
            self.texturesPath = ""
            self.archivePath = ""
            self.deletePath = ""
            self.workshopFormat = ""
            self.masterFormat = ""
            self.workshopName = ""
            self.masterName = ""
        else:
            pass

    def reset(self):
        self.currProjectName = ""
        self.initialize()