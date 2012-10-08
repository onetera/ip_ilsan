# -*- coding: utf-8 -*-

"""
**iPipelineActions.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    iPipelineActions Module.

**Others:**

"""

#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import os,re , glob
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
try:    
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA = True
except ImportError:
    MAYA = False
from conndb import *    
import logging    
    
from components.addons.information.information import Information

SCENEFILE_RE = re.compile("v[0-9]{2}_w[0-9]{2}.mb")
SCENEFILE_WITH_SUBJECT_RE = re.compile("v[0-9]{2}_w[0-9]{2}_[\w]+.mb")
VER_WIP_RE = re.compile("v[0-9]{2}_w[0-9]{2}")
VER_RE = re.compile("_v[0-9]{2}")
WIP_RE = re.compile("_w[0-9]{2}")
#***********************************************************************************************
#***    Internal imports.
#***********************************************************************************************
#from foundations.globals.constants import Constants

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
class iPipelineActions(object):

    def activateProject(self, projName):
        self.currProjectName = projName
        if 'win' in  sys.platform:
            self.currProjectPath = self.showPath + "\\" + projName + "/"
        else :
            self.currProjectPath = self.showPath + "/" + projName + "/"
        self.shotPath = self.currProjectPath + "seq/"
        self.libPath =  self.currProjectPath + "assets/"
        self.deletePath = self.currProjectPath + "deleted" + "/"
        
        return True

    def checkItem(self):
        try:
            return cmds.file(query=True, modified=True)
        except:
            return

    def findIndexlistWidget( self , lwidget , txt ):        
        try : 
            result = [ lwidget.item(x).text() for x in xrange( lwidget.count()) ].index(txt)
        except :
            result = -1
        return result
        

    def openItem(self, type, newProject, devel):              
        if self.checkItem():
            logging.warning( 'checkItem' )         
            messageBox = QMessageBox(self)
            messageBox.setText('Would you like to Save Dev before editing Asset?')
            messageBox.setWindowModality(Qt.WindowModal)
            messageBox.setIcon(QMessageBox.Question)
            saveButton = messageBox.addButton('Save', QMessageBox.AcceptRole)
            unsaveButton = messageBox.addButton("Don't Save", QMessageBox.AcceptRole)
            messageBox.setDefaultButton(saveButton)
            messageBox.addButton(QMessageBox.Cancel)
            messageBox.exec_()
            currOpendFilename = cmds.file(q=1,l=1)[0]
            currOpendFilename = currOpendFilename.split('/')[1:]
            
            if messageBox.clickedButton() == saveButton:
#                if 'show' not in currOpendFilename or 'untitled' in currOpendFilename:                    
#                    cmds.file( s=1 )
#                    self.openSaveAs()
#                    return
                print currOpendFilename
                cmds.file( rename=cmds.file(q=1,l=1)[0] )
                cmds.file( s=1 )
#                self.openSaveAs()
            elif messageBox.clickedButton() == messageBox.button(QMessageBox.Cancel):
                return False    
#        try:
        if 'win' in sys.platform:                
            newProject = newProject.replace( '\\' , '\\\\' )
            newProject = '\\' + newProject                        
        mel.eval('setProject "%s"' % newProject)
#        except:                        
#            return True
        if QFileInfo(devel).isFile():
            if MAYA:
                print 'devel : ' , devel
                cmds.file(devel, open=True, force=True)
            else :
                logging.warning( 'Devel file exist : %s' % devel )
        elif type=="devel" and not QFileInfo(devel).isFile():
            messageBox = QMessageBox(self)
            messageBox.setText("You are about to edit an item for the first time. Would you like to start with an new scene, or the currently open scene?")
            messageBox.setWindowModality(Qt.WindowModal)
            messageBox.setIcon(QMessageBox.Question)
            newSceneButton = messageBox.addButton('New Scene', QMessageBox.AcceptRole)
            currentSceneButton = messageBox.addButton('Current Scene', QMessageBox.AcceptRole)
            messageBox.setDefaultButton(currentSceneButton)
            messageBox.addButton(QMessageBox.Cancel)
            messageBox.exec_()
            if messageBox.clickedButton() == newSceneButton:
                cmds.file(new=True, force=True)
                if self.tabWidget.currentIndex() ==1 :                    
                    createAssetJob(self.projNameCombo.currentText() , self.currOpenLevel1 , self.currOpenLevel2 , self.currOpenLevel3)
                    self.mssg( u'어셋이 Database 서버에 최초 등록 하였습니다.\n' )
                elif self.tabWidget.currentIndex() ==2:
                    createJob( self.projNameCombo.currentText() , self.currOpenLevel1 , self.currOpenLevel2 , self.currOpenLevel3)
                    self.mssg( u'샷이 Database 서버에 최초 등록 하였습니다.\n' ) 
            elif messageBox.clickedButton() == messageBox.button(QMessageBox.Cancel):
                return False        
        else:
            QMessageBox.warning(self, "openItem", "OpenItem: File Not Found \n")
            return False
        return True

    def openItem2(self, type, tab, level1, level2, level3, versionOffset):
        folder = self.getFileName(tab, level1, level2, level3, "folder")
        depth = self.getDepth(level1, level2, level3)
        if depth > 1 and QDir(folder).exists() and (type == "devel" or type == "publish"):
            version = 0
            currLevel1 = self.currOpenLevel1
            if self.checkItem() and len(currLevel1):
                print 'confirm'
            
            fileToOpen = self.getFileName(tab, level1, level2, level3, type, versionOffset)
            latestDevel = self.getFileName(tab, level1, level2, level3, type, 0)
            subject = self.getFileName(tab, level1, level2, level3, "subject", 0)
            category = self.getCategory(tab, level1, level2, level3)
            if QFileInfo(fileToOpen).isReadable():
                #version = self.getVersionFromFile
                cmds.file(fileToOpen, open=True, force=True)
            elif type == "devel" and not QFileInfo(latestDevel).isReadable():
                #choice
                print 'New Scene'
                cmds.file(new=True, force=True)
            
            self.currOpenType = type
            #self.currOpenVersion = version
            self.currOpenCategory = category
            self.currOpenLevel1 = level1
            self.currOpenLevel2 = level2
            self.currOpenLevel3 = level3
            self.currOpenTab = tab
            print category, level1, level2, level3, tab
        else:
            QMessageBox.warning(self, "openItem", "OpenItem: File Not Found \n")
            return False
        return True

    def createNewItem(self, tab, level1, level2, level3, mode):
        error = ""
        itemPath = self.getFileName(tab, level1, level2, level3, mode)
        print 'itemPath : ' , itemPath
        depth = self.getDepth(level1, level2, level3)
        print 'dept : ' , depth
        if (depth and len(itemPath)):
            if QDir(itemPath).exists():
                error += "already exists."
            if len(error):
                print "createNewItem: %s" % error
                return ""
            else:
                # 디렉토리 생성
                QDir().mkpath(itemPath)
                if depth == 1 or depth == 2:
                    pass
                if depth == 3:
                    pass
                return itemPath
        else:
            print "createNewItem: Parameters incorrect, no new item created."
            return ""

    def closeFile(self):
        try:
            if cmds.file(q=True, mf=True):
                messageBox = QMessageBox(self)
                messageBox.setText('Would you like to Save devel before editing closing?')
                messageBox.setWindowModality(Qt.WindowModal)
                #messageBox.setIcon(QMessageBox.Question)
                saveButton = messageBox.addButton('Save', QMessageBox.AcceptRole)
                unsaveButton = messageBox.addButton("Don't Save", QMessageBox.AcceptRole)
                messageBox.setDefaultButton(unsaveButton)
                messageBox.addButton(QMessageBox.Cancel)
                messageBox.exec_()
                if messageBox.clickedButton() == saveButton:
                    print 'save button'
                elif messageBox.clickedButton() == messageBox.button(QMessageBox.Cancel):
                    return True
        except:
            pass
        self.currOpenLevel1 = ""
        self.currOpenLevel2 = ""
        self.currOpenLevel3 = ""
        self.currOpenTab = 0

        try:
            cmds.file(new=True, force=True)
        except:
            pass
        self.updateUI('currOpen')

        return True

    def closeFile2(self):
        self.currOpenLevel1 = ""
        self.currOpenLevel2 = ""
        self.currOpenLevel3 = ""
        self.currOpenTab = 0

        try:
            cmds.file(new=True, force=True)
        except:
            pass
        self.updateUI('currOpen')

        return True

    def openLocation(self, tab, level1, level2, level3, offset=0, archive=0):
        path = self.getFileName(tab, level1, level2, level3, "folder", offset, archive)
        if QDir(path).exists():
            if sys.platform == "linux2":
                cmd = "nautilus "+path
            elif sys.platform == "darwin":
                cmd = "open -a finder "+path
            elif sys.platform == "win32":
                cmd = "explorer "+path
            else:
                return
            proc = QProcess.startDetached(cmd)
        else:
            print "openLocation: couldn't find folder "+path+"."

    def recordPlayblast(self, tab, level1, level2, level3):
        playblastFile = self.getFileName(tab, level1, level2, level3, "playblastFile")
        cmds.playblast(filename=str(playblastFile), forceOverwrite=True, format="movie", viewer=False, showOrnaments=False , os=1 )
        previewFolder = os.path.dirname(playblastFile)
        os.chmod( previewFolder , 0777 )
        return playblastFile

    def recordPlayblastForSequence(self, tab, level1, level2, level3, offset=0, archive=0):
        # "/Users/higgsdecay/test"
        playblastFile = self.getFileName(tab, level1, level2, level3, "playblastFile2", offset, archive)
        # create the preview folder
        previewFolder = os.path.dirname(playblastFile)
        if not os.path.exists(previewFolder):
            os.makedirs(previewFolder)
            os.chmod( previewFolder , 0777 )
        else : 
            os.chmod( previewFolder , 0777 )
        startFrame = cmds.getAttr("defaultRenderGlobals.startFrame")
        endFrame = cmds.getAttr("defaultRenderGlobals.endFrame")
        format = cmds.getAttr("defaultRenderGlobals.imageFormat")
        
        width = cmds.getAttr("defaultResolution.width")
        height = cmds.getAttr("defaultResolution.height")
        ratio = cmds.getAttr("defaultResolution.deviceAspectRatio")
        
        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
        # playblast -startTime 1 -endTime 10  -format iff -filename "/Users/higgsdecay/output/ACR_rig_v02_w03" 
        #-forceOverwrite  -sequenceTime 0 -clearCache 0 -viewer 1 -showOrnaments 1 -fp 4 -percent 50 -widthHeight 1920 1080;
        
        cmds.playblast(startTime=startFrame, endTime=endFrame, format="image",
                       filename=str(playblastFile), showOrnaments=False, viewer=False, percent=100,os=1,
                       sequenceTime=False, forceOverwrite=True,
                       widthHeight=[int(width), int(height)])
        cmds.setAttr("defaultRenderGlobals.imageFormat", format)
        
        return (playblastFile+".####.jpg", int(startFrame), int(endFrame), int(width), int(height), ratio)

    def createThumbnail(self, tab, level1, level2, level3, offset=0, archive=0):
        fileName = self.getFileName(tab, level1, level2, level3, "previewFile", offset, archive)
        currFrame = cmds.currentTime(query=True)
        format = cmds.getAttr("defaultRenderGlobals.imageFormat")
        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
        cmds.playblast(frame=currFrame, format="image", completeFilename=str(fileName), showOrnaments=False, viewer=False, widthHeight=[164, 105], percent=100 , os=1)
        cmds.setAttr("defaultRenderGlobals.imageFormat", format)
        return fileName

    def recordPlayblastForSequenceN(self, tab, level1, level2, level3, width , height , fileName , folder = 'devFolder' ):
        # "/Users/higgsdecay/test"
        playblastFile = os.path.join(str(self.getFileName(tab, level1, level2, level3, folder , 0, 1)), "preview", os.path.splitext(str(fileName))[0], str(fileName))
        # create the preview folder
        previewFolder = os.path.dirname(playblastFile)
        if not os.path.exists(previewFolder):
            os.makedirs(previewFolder)
            os.chmod( previewFolder , 0777 )
        startFrame = cmds.getAttr("defaultRenderGlobals.startFrame")
        endFrame = cmds.getAttr("defaultRenderGlobals.endFrame")
        format = cmds.getAttr("defaultRenderGlobals.imageFormat")
        
#        width = cmds.getAttr("defaultResolution.width")
#        height = cmds.getAttr("defaultResolution.height")
        ratio = cmds.getAttr("defaultResolution.deviceAspectRatio")
        cams = [ x for x in cmds.ls(typ='camera') if cmds.getAttr(x+'.renderable')]
        thecam = cmds.listRelatives( cams[0] , p = 1) if cams != [] else None

        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
        # playblast -startTime 1 -endTime 10  -format iff -filename "/Users/higgsdecay/output/ACR_rig_v02_w03" 
        #-forceOverwrite  -sequenceTime 0 -clearCache 0 -viewer 1 -showOrnaments 1 -fp 4 -percent 50 -widthHeight 1920 1080;
        cmds.playblast(startTime=startFrame, endTime=endFrame, format="image",percent = 100 , qlt = 100,
                       filename=os.path.splitext(str(playblastFile))[0], showOrnaments=False, viewer=False, os=1,
                       sequenceTime=False, forceOverwrite=True,
                       widthHeight=[int(width), int(height)]  )
        
        for x in glob.glob( previewFolder+os.sep+'*.*' ):
            os.chmod(x , 0777)
        cmds.setAttr("defaultRenderGlobals.imageFormat", format)
        return (playblastFile, int(startFrame), int(endFrame), ratio)
        #return (playblastFile+".####.jpg", int(startFrame), int(endFrame), int(width), int(height), ratio)

    def createThumbnailN(self, tab, level1, level2, level3, fileName):
        fileName = self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1)+fileName
        currFrame = cmds.currentTime(query=True)
        format = cmds.getAttr("defaultRenderGlobals.imageFormat")
        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
        cmds.playblast(frame=currFrame, format="image", completeFilename=str(fileName), showOrnaments=False, viewer=False, widthHeight=[164, 105], percent=100 , os=1)
        cmds.setAttr("defaultRenderGlobals.imageFormat", format)
        return fileName

    def viewPlayblast(self, tab, level1, level2, level3):
        playblastFile = self.getFileName(tab, level1, level2, level3, 'playblastFile')
        if os.path.exists(playblastFile):
            os.system('open %s' % playblastFile)
        else:
            QMessageBox.warning(self, 'viewerPlast', "couldn't find playblast file " + playblastFile + '.')

    def removeItem(self, tab, level1, level2, level3):
        originalPath = self.getFileName(tab, level1, level2, level3, "folder")
        newPath = self.deletePath + QDir(originalPath).dirName()+"_deleted_"
        j = 0
        while QDir(newPath+QString.number(j)).exists():
            j+=1
        newPath = newPath+QString.number(j)
        if not QDir().exists(self.deletePath):
            QDir().mkpath(self.deletePath)
        result = QDir().rename(originalPath, newPath)
        if not result:
            print "error: Remove failed. Folder %s could not be moved to the 'deleted' folder. \nA folder or file may be in use outside of Maya."
            return 0

        return True
    
    def mssg(self, msg):
        messageBox = QMessageBox(self)
        messageBox.setText(unicode(msg))
        messageBox.setWindowModality(Qt.WindowModal)
        messageBox.setIcon(QMessageBox.Information)
        closeButton = messageBox.addButton('Close', QMessageBox.AcceptRole)
        messageBox.exec_()
    
    
if __name__ == '__main__' :
    thePath = '/show/sample/assets/char/ttt/'
    QDir().mkpath(thePath)