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
    standAlone = False
except ImportError:
    standAlone = True
    
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
    """
    This class is the **iPipelineActions** class.
    """
    def activateProject(self, projName):
        self.currProjectName = projName
        self.currProjectPath = self.showPath + "/" + projName + "/"
        self.shotPath = self.currProjectPath + "seq/"
        self.libPath =  self.currProjectPath + "assets/"
        self.deletePath = self.currProjectPath + "deleted" + "/"
        
        return True

#    def openSaveAs(self):
#        theFile = cmds.fileDialog2(dialogStyle=2)[0]
#        cmds.file(rename = theFile )
#        cmds.file( save = 1  )
           
    def openItem(self, type, newProject, devel):
        
        if self.checkItem():
            """check modified current file or not"""
            
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
                if 'show' not in currOpendFilename or 'untitled' in currOpendFilename:
                    self.openSaveAs()
                    return
                self.openSaveAs()
#                level1 ,level2 , level3 = currOpendFilename[3:6]                
#                tab = 'Asset' if currOpendFilename[2] == 'assets' else 'Shot'
#                sceneFileName = currOpendFilename[-1]                
#                subjectName = str(self.currOpenSubjectField.text())
#                ver_wip = VER_WIP_RE.findall( sceneFileName )[0] # return v01_w02
#                currVer = int(ver_wip[1:3])
#                currWip = int(ver_wip[-2:])
#                sceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1))   
#                sceneFiles = glob.glob(sceneFolder+"*.mb")                 
#                curLatestVersion = os.path.join(sceneFolder, sceneFileName.replace(ver_wip, ver_wip[:-2]+str(currWip).zfill(2)))
#                
#                if len(subjectName):
#                    subjectLists = {}
#                    subjectFiles = filter(SCENEFILE_WITH_SUBJECT_RE.search, sceneFiles)
#                    for i in subjectFiles:
#                        _fileName = os.path.basename(i)
#                        _ver_wip = VER_WIP_RE.findall(_fileName)[0]
#                        fileName = _fileName.split(_ver_wip)[-1][1:] # remove underscore
#                        basename = os.path.splitext(fileName)[0]
#                        if subjectLists.get(basename) is None:
#                            subjectLists[basename] = []
#                        subjectLists[basename].append( i )
#        
#                    for subject in subjectLists.keys():
#                        subjectLists[subject] = sorted(subjectLists[subject])
#        
#                    if len(subjectLists):
#                        #try:
#                        subjects = subjectLists[subjectName]
#                        subjects = sorted(subjects, reverse=True)
#                        destinationFile = subjects[0]
#                        ver = VER_WIP_RE.findall( os.path.basename(str(destinationFile)))[0]
#                        nVer = ver[:-2]+str(int(ver[-2:])+1).zfill(2)
#                        destinationFile = destinationFile.replace(ver, nVer)
#                        #except KeyError:
#                        #    destinationFile = os.path.join(sceneFolder, "%s_%s_v01_w01_%s.mb" % (level2, level3, str(self.currOpenSubjectField.text())))
#                    else:
#                        # 초기화 버전
#                        destinationFile = os.path.join(sceneFolder, "%s_%s_v01_w01_%s.mb" % (level2, level3, str(self.currOpenSubjectField.text())))
#        
#                # 서브젝트가 존재하지 않을 때
#                else:
#                    defaultFiles = filter(SCENEFILE_RE.search, sceneFiles)
#                    if len(defaultFiles):
#                        destinationFile = defaultFiles[-1]
#                        ver = VER_WIP_RE.findall( os.path.basename(str(destinationFile)))[0]
#                        nVer = ver[:-2]+str(int(ver[-2:])+1).zfill(2)
#                        destinationFile = destinationFile.replace(ver, nVer)
#                    else:
#                        # 초기화 버전
#                        destinationFile = os.path.join(sceneFolder, "%s_%s_v01_w01.mb" % (level2, level3))
                
#                info = Information("Save Devel", level2, level3, currVer, currWip, subjectName, curLatestVersion, destinationFile, self)
#                self.connect( info , SIGNAL("save"), self.saveDevel)
#                info.show()                
                
    #                self.saveDevel( devel , "saved before opening new item", "WIP", 50, 1, "iMaya" , "" )
            elif messageBox.clickedButton() == messageBox.button(QMessageBox.Cancel):
                return False
            
        
            # set the current project
        try:
            if 'win' in sys.platform: 
                newProject = '/' + newProject
            mel.eval('setProject "%s"' % newProject)
        except:
            return True

        print 'devel : ' ,devel
        if QFileInfo(devel).isFile():
            cmds.file(devel, open=True, force=True)
            print 'theFile is exist'
            
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
        cmds.playblast(filename=str(playblastFile), forceOverwrite=True, format="movie", viewer=False, showOrnaments=False)
        return playblastFile

    def recordPlayblastForSequence(self, tab, level1, level2, level3, offset=0, archive=0):
        # "/Users/higgsdecay/test"
        playblastFile = self.getFileName(tab, level1, level2, level3, "playblastFile2", offset, archive)
        # create the preview folder
        previewFolder = os.path.dirname(playblastFile)
        if not os.path.exists(previewFolder):
            os.makedirs(previewFolder)
#            os.chmod( previewFolder , 0775 )
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
                       filename=str(playblastFile), showOrnaments=False, viewer=False, percent=50,
                       sequenceTime=False, forceOverwrite=True,
                       widthHeight=[int(width), int(height)])
        cmds.setAttr("defaultRenderGlobals.imageFormat", format)
        return (playblastFile+".####.jpg", int(startFrame), int(endFrame), int(width), int(height), ratio)

    def createThumbnail(self, tab, level1, level2, level3, offset=0, archive=0):
        fileName = self.getFileName(tab, level1, level2, level3, "previewFile", offset, archive)
        currFrame = cmds.currentTime(query=True)
        format = cmds.getAttr("defaultRenderGlobals.imageFormat")
        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
        cmds.playblast(frame=currFrame, format="image", completeFilename=str(fileName), showOrnaments=False, viewer=False, widthHeight=[164, 105], percent=100)
        cmds.setAttr("defaultRenderGlobals.imageFormat", format)
        return fileName

    def recordPlayblastForSequenceN(self, tab, level1, level2, level3, fileName , previewScale ):
        # "/Users/higgsdecay/test"
        playblastFile = os.path.join(str(self.getFileName(tab, level1, level2, level3, "devFolder", 0, 1)), "preview", os.path.splitext(str(fileName))[0], str(fileName))
        # create the preview folder
        previewFolder = os.path.dirname(playblastFile)
        if not os.path.exists(previewFolder):
            os.makedirs(previewFolder)
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
                       filename=os.path.splitext(str(playblastFile))[0], showOrnaments=False, viewer=False, percent= previewScale ,
                       sequenceTime=False, forceOverwrite=True,
                       widthHeight=[int(width), int(height)])
        cmds.setAttr("defaultRenderGlobals.imageFormat", format)
        return (playblastFile, int(startFrame), int(endFrame), int(width), int(height), ratio)
        #return (playblastFile+".####.jpg", int(startFrame), int(endFrame), int(width), int(height), ratio)

    def createThumbnailN(self, tab, level1, level2, level3, fileName):
        fileName = self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1)+fileName
        currFrame = cmds.currentTime(query=True)
        format = cmds.getAttr("defaultRenderGlobals.imageFormat")
        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
        cmds.playblast(frame=currFrame, format="image", completeFilename=str(fileName), showOrnaments=False, viewer=False, widthHeight=[164, 105], percent=100)
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
    
    
if __name__ == '__main__' :
    thePath = '/show/sample/assets/char/ttt/'
    QDir().mkpath(thePath)