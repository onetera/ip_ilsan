# -*- coding: utf-8 -*-

"""
**iPipelineUtility.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    iPipelineUtility Framework Module

**Others:**

"""

#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import re
import glob
from PyQt4.QtCore import *
from PyQt4.QtGui import *
try:
    import maya.cmds as cmds
    import maya.mel as mel
    standAlone = False
except ImportError:
    standAlone = True

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
class iPipelineUtility(object):
    """
    This class is the **iPipelineUtility** class.
    """

    def createNewFolder(self, path):
        """
        
        :param path: ( QString )
        :return: ( Integer )
        """
        status = 0
        if not QDir(path).exists():
            if QDir().mkpath(path):
                status = 0
            else:
                status = 1
        else:
            status = 2
        return status

    def getDepth(self, level1, level2, level3):
        """
        
        :param level1: ( QString )
        :param level2: ( QString )
        :param level3: ( QString )
        :return: ( Integer )
        """
        depth = 0
        if len(level1):
            depth+=1
            if len(level2):
                depth+=1
                if len(level3):
                    depth+=1
        return depth

    def getVersionFromFile(self, file):
        """
        
        :param file: ( QString )
        :return: ( QString )
        """
        file = str(file) # unicode to string
        version_re = re.compile('v[0-9]{2}_w[0-9]{2}')
        return version_re.findall(file)[0]

    def getDirectoryList(self, path):
        """        
        :param path: Provided path. ( QString )
        :return: ( List )
        """
        dirList = QDir(path).entryList(QDir.Dirs|QDir.NoDotAndDotDot)
        return dirList

    def sourceModule(self, path):
        melFiles = QDir(path).entryList(QDir.Files|QDir.NoDotAndDotDot)
        print "----- Sourcing " + path + "------"
        for eachFile in melFiles:
            if eachFile.endsWith(".mel"):
                scriptFile = path + "/" + eachFile
                cmdString = "source \"" + scriptFile + "\""
                print "//// Source: " + cmdString
                if standAlone == True : return 
                mel.eval(cmdString)
        return buffer

    def getFiles(self, path, mode, reverse=False):
        searchMayaFile = str(path+"/scenes/*.mb")
        children = glob.glob(searchMayaFile)
        if mode == "devel":
            pattern_re = re.compile('v[\d]{2}_w[\d]{2}(.|_[\w]+.)mb')
        elif mode == "publish":
            pattern_re = re.compile('v[\d]{2}(.|_[\w]+.)mb')
        if reverse:
            return sorted(filter(pattern_re.search, children), reverse=True)
        else:
            return sorted(filter(pattern_re.search, children))

if __name__ == "__main__":
    thePath = QDir('/show').entryList(QDir.Dirs|QDir.NoDotAndDotDot)
    print thePath
    print '======================================='
    for x in dir(thePath):
        if x[0] != '_':
            print x
    
#    i = iPipelineUtility()
#    i.sourceModule('/Users/higgsdecay/work/di/ipipeline/scripts/openPipeline')
#    print i.getVersionFromFile('test_v01_w01.mb')
#    print i.getDepth("test", "test2", "test3")
#    for mel in i.sourceModule('/Users/higgsdecay/work/di/ipipeline/scripts/openPipeline'):
#        print mel
#    i.getVersionFromFile("AA03_comp_v01_w01.mb")
