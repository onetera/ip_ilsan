# -*- coding: utf-8 -*-


#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import sys
import os
import re



#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
class iPipelineInit(object):

    def initialize(self):       
        self.userName = re.search('d\d{5}' , os.getenv('USERNAME') ).group() if 'DIGITALIDEA' in os.getenv('USERNAME')  else os.getenv('USERNAME')        
        self.currProjectName = ""
        self.currentUser = "default"
        superUserList = ['d10021', 'd10230', 'd10060', 'd10165' , 'd10058' , 'd10068' , 'd10166' , 'd10218' ]
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
        
        