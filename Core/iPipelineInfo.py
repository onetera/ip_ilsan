# -*- coding: utf-8 -*-

"""
**ipipelineInfo.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    iPipelineInfo Module.

**Others:**

"""

#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import os
import sys
import re
import glob
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#***********************************************************************************************
#***    Internal imports.
#***********************************************************************************************
from Core.Note.Note import NoteContainer

#***********************************************************************************************
#***    Global variables.
#***********************************************************************************************
SCENEFILE_RE= re.compile('v[0-9]{2}_w[0-9]{2}.mb')
SCENEFILE_WITH_SUBJECT_RE = re.compile('v[0-9]{2}_w[0-9]{2}_[a-zA-Z0-9]+.mb')
VER_RE = re.compile('_v[0-9]{2}')
WIP_RE = re.compile('_w[0-9]{2}')

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
class iPipelineInfo(object):
    """
    This class is the **iPipelineInfo** class.
    """

    def getDate(self):
        #date = QDate.currentDate().toString("MM/dd/yyyy")
        date = QDate.currentDate()
        return date

    def getTime(self):
        #time = QTime.currentTime().toString()
        time = QTime.currentTime()
        return time

    def hasPublish(self):
        publish = 'publish_file'
        return QFile(publish).isReadable()

    def hasPlayblast(self):
        playblastFile = 'playblastFile'
        return QFile(playblastFile).isReadable()

    def getDevels(self, tab, level1, level2, level3, archive=None):
        develFiles = []
        i = 0
        devel = self.getFileName(tab, level1, level2, level3, "devel", i)
        while(len(devel)):
            develFiles.append(devel)
            i+=1
            devel = self.getFileName(tab, level1, level2, level3, "devel", i)
        return develFiles

    def getDepth(self, level1, level2, level3):
            depth = 0
            if len(level1):
                depth+=1
                if len(level2):
                    depth+=1
                    if len(level3):
                        depth+=1
            return depth
        
    def getFileName(self, tab, level1, level2, level3, mode, offset=0, archive=0, selFile=""):
        depth = self.getDepth(level1, level2, level3)
        
        fileName = ""
        devFolder = 'dev'
        pubFolder = 'pub'
        previewFileName = '.preview.jpg'
        scenesFolder = 'scenes'
        
        
        if mode=="parentFolder":
            if depth==3:
                self.getFileName(tab, level1, level2, "", "folder")
            elif depth==2:
                self.getFileName(tab, level1, "", "", "folder")
            elif depth==1:
                pass
            else:
                fileName=""
        else:
            if tab==1:
                print 'self.libPath : ' , self.libPath
                fileName += self.libPath                
            elif tab==2:
                fileName += self.shotPath
            else:
                return ""

            if archive:
                projectPath = self.showPath + "/" + self.currOpenProjectName + "/"
                fileName = fileName.replace(self.currProjectPath, projectPath)
#                print 'archive projectPath : ' , projectPath
            
            if len(level1):
                fileName += level1+"/"
                print 'leve1...OK :' ,level1
                if len(level2):
                    fileName += level2+"/"
                    print 'leve2...OK :' ,level2

                    if len(level3):
                        fileName += level3+"/"
                        print 'leve3...OK :' ,level3
                    print 'mode : ' , mode
                    if mode=="devFolder":
                        fileName += devFolder

                    elif mode=="pubFolder":
                        fileName += pubFolder

                    elif mode=="sceneFolder":
                        fileName += devFolder+"/"+scenesFolder+"/"
                        print 'scene Dolder....OK'

                    elif mode=="previewFile":
                        fileName = self.getFileName(tab, level1, level2, level3, "sceneFolder", offset, archive)
                        if len(fileName):
                            pass
                        fileName += previewFileName

                    elif mode=="playblastFile":
                        fileName = self.getFileName(tab, level1, level2, level3, "sceneFolder", offset, archive)
                        if sys.platform == "linux2":
                            ext = "mv"
                        elif sys.platform == "darwin":
                            ext = "mov"
                        elif sys.platform == "win32":
                            ext = "avi"
                        else:
                            return
                        playblastFileName = ".playblast."+ext
                        fileName += playblastFileName

                    elif mode=="playblastFile2":
                        develFile = str(self.getFileName(tab, level1, level2, level3, "devel", offset, archive))
                        devFolder = os.path.dirname(develFile).replace("/dev/scenes", "/dev/preview")
                        basename = os.path.basename(develFile)
                        basename = os.path.splitext(basename)[0]
                        playblastFileName = os.path.join(devFolder, basename, basename)
                        fileName = playblastFileName

                    elif mode=="devel":
                        sceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", offset, archive))
                        develFiles = glob.glob(sceneFolder+"*.mb")
                        develFiles = filter(SCENEFILE_RE.search, develFiles)
                        develFiles = sorted(develFiles)
                        develNum = len(develFiles)
                        if develNum:
                            if (develNum-1-offset) >= 0:
                                fileName = develFiles[develNum-1-offset]
                            else:
                                fileName = ""
                        else:
                            fileName = ""
                            devel = ""

                    elif mode=="subject":
                        sceneFolder = self.getFileName(tab, level1, level2, level3, "sceneFolder", offset, archive)
                        develFiles = glob.glob(sceneFolder)
                        develFiles = filter(SCENEFILE_WITH_SUBJECT_RE.search, develFiles)
                        develFiles = sorted(develFiles)
                        develNum = len(develFiles)
                        if develNum:
                            if (develNum-1-offset) >= 0:
                                fileName = develFiles[develNum-1-offset]
                            else:
                                fileName = ""
                        else:
                            fileName = ""
                            devel = ""

                    elif mode=="nextDevel":
                        fileName = self.getFileName(tab, level1, level2, level3, "sceneFolder", offset, archive)
                        sceneFolder = str(fileName+'/*.mb')
                        fileList = glob.glob(sceneFolder)
                        l = sorted(fileList, reverse=True)
                        latestDevel = 0
                        if len(l):
                            latestFileName = l[0]
                            devel = os.path.basename(latestFileName)
                            ver = VER_RE.findall( str(devel) )[0][1:]
                            wip = int(WIP_RE.findall( str(devel) )[0][2:])
                            wip = 'w'+str(wip+1).zfill(2)
                        else:
                            ver ='v01'
                            wip ='w01'
                        fileName = fileName+'/'+level2+'_'+level3+'_'+ver+'_'+wip+'.mb'

                    elif mode=="nextVersion":
                        fileName = self.getFileName(tab, level1, level2, level3, "sceneFolder", offset, archive)
                        pubFolder = self.getFileName(tab, level1, level2, level3, "pubFolder", offset, archive)
                        sceneFolder = str(fileName+'/*.mb')
                        fileList = glob.glob(sceneFolder)
                        l = sorted(fileList, reverse=True)
                        latestVersion = 0
                        if len(l):
                            latestFileName = l[0]
                            devel = os.path.basename(latestFileName)
                            ver = int(VER_RE.findall( str(devel) )[0][2:])
                            ver = 'v'+str(ver).zfill(2)
                        else:
                            ver ='v01'
                        fileName = pubFolder+'/scenes/'+level2+'_'+level3+'_'+ver+'.mb'
                    
                    elif mode=="historyFile":
                        print 'historyFile.......OK'
                        fileName = self.getFileName(tab, level1, level2, level3, "sceneFolder", offset, archive)                        
                        if len(level3):
                            fileName += level2+"_"+level3+"_ComponentNote.xml"
                            print 'XML fileName : ' , fileName
                            
                    elif mode=="childFolder":
                        if depth == 2:
                            pass
                        elif depth == 3:
                            fileName = ""

                    elif mode=="folderTest":
                        fileName = QString(str(fileName).split('dev/scenes/')[0])
                    else :
                        print 'mode false...........'
                else : 
                    print 'false..........level2'
            else : 
                print 'false..........level1'
                

        
        return fileName

    def getCategory(self, tab, level1, level2, level3):
        if tab == 1:
            if len(level3):
                category = "component"
            elif len(level2):
                category = "asset"
            elif len(level1):
                category = "assetType"
        elif tab == 2:
            if len(level3):
                category = "shotComponent"
            elif len(level2):
                category = "shot"
            elif len(level1):
                category = "sequence"
        return category

    def getThumbnail(self, tab, level1, level2, level3):
        fileName = self.getFileName(tab, level1, level2, level3, "previewFile")
        return fileName

    def getCurrentlySelectedItem(self, tab, depth):
        """
        
        :param tab: ( Integer )
        :param depth: ( Integer )
        :return: ( List )
        """
        level1 = ''
        level2 = ''
        level3 = ''
        
        if tab == 1:
            if (depth > 0):
                selected = self.assetTypeScrollList.currentRow()
                if selected != -1:
                    level1 = self.assetTypes[selected]
            if (depth > 1):
                selected = self.assetScrollList.currentRow()
                if selected != -1:
                    level2 = self.assets[selected]
            if (depth > 2):
                selected = self.componentScrollList.currentRow()
                if selected != -1:
                    level3 = self.components[selected]
        
        elif tab == 2:
            if (depth > 0):
                selected = self.sequenceScrollList.currentRow()
                if selected != -1:
                    level1 = self.sequences[selected]
            if (depth > 1):
                selected = self.shotScrollList.currentRow()
                if selected != -1:
                    level2 = self.shots[selected]
            if (depth > 2):
                selected = self.shotComponentScrollList.currentRow()
                if selected != -1:
                    level3 = self.shotComponents[selected]
        
        item = [level1, level2, level3]
        return item
    
    def getEventNotes(self, tab, level1, level2, level3, offset=0, archive=0):
        historyFile = self.getFileName(tab, level1, level2, level3, "historyFile", offset, archive)
#        if historyFile == '' :
#            print 'historyFile...........Fasle'        
        #outString = ""
        nc = []
        if QFileInfo(historyFile).isFile():
            nc = NoteContainer()
            nc.importSAX(str(historyFile))
            #outString = n.readXML()
            nc = nc.getNotes(True)
        return nc

    def getChildren(self, tab, level1, level2, level3):
        childPath = self.getFileName(tab, level1, level2, level3, "childFolder")
        children = QDir(childPath).entryList(QDir.Dirs|QDir.NoDotAndDotDot)
        return children


if __name__ == '__main__' :    
    test = iPipelineInfo()  
    try : 
        if test.libPath:
            pass
    except:
        test.libPath = '/home/idea/temp/Show/awesome/assets/'
         
    kk =  test.getFileName( 1 , 'cha', 'humanA', 'rig', 'historyFile',)
    print kk
