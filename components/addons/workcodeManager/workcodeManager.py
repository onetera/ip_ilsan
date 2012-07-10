# -*- coding: utf-8 -*-

"""
**workcodeManager.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    Workcode Manager Module.

**Others:**

"""
#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

#***********************************************************************************************
#***    Internal imports.
#***********************************************************************************************
from foundations.globals.constants import Constants
from Core.Note.Note import NoteContainer, Note

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
class WorkcodeManager(QDialog):

    def __init__(self, tab, level1, level2, level3, workcodedata, userName, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(Constants.applicationDirectory+"components/addons/workcodeManager/ui/Workcode_Manager.ui", self)

        self.tab = tab
        self.level1 = level1
        self.level2 = level2
        self.level3 = level3
        self.workcodedata = workcodedata
        self.userName = userName
        self.Workcode_listWidget.addItems(sorted(self.workcodedata.keys()))
        self.getFileName = self.parent().getFileName
        self.assetSelected = self.parent().assetSelected
        self.shotSelected = self.parent().shotSelected

    def accept(self):
        taskName = str(self.Workcode_listWidget.currentItem().text())
        root = str(self.getFileName(self.tab, self.level1, self.level2, taskName, "folderTest"))
        historyFile = self.getFileName(self.tab, self.level1, self.level2, taskName, "historyFile")        
        if os.path.exists(root):
            print "already exists."
        else:            
            createFolderList = []
            devFolder = os.path.join(root, "dev")
            pubFolder = os.path.join(root, "pub")
            workspaceFile = os.path.join(str(devFolder), "workspace.mel")
            createFolderList.append(devFolder)
            createFolderList.append(pubFolder)            
            subFolderList = self.workcodedata[taskName]
             
            source_workspace = Constants.workspaceDirectory + "/" + taskName + ".mel"
            
            
            if not QFileInfo(source_workspace).isFile():
                return
            for sub in subFolderList:
                createFolderList.append(os.path.join(devFolder, sub))
            # 디렉토리 생성
            for folder in createFolderList:
                os.makedirs(folder)
                if 'preview' in folder:
                    os.chmod( folder , 0777 )
            QFile.copy(source_workspace, workspaceFile)
            # workspace.mel 의 퍼미션을 읽기모드로 변경
            os.chmod(workspaceFile, 0555)

            nc = NoteContainer()
            nc.add(Note(self.userName,  # author
                        self.getDate(), # date
                        self.getTime(), # time
                        "created",      # event
                        comment=""      # comment
                        ))
            # scenes 폴더에 xml 파일 생성
            nc.exportXML(historyFile)
            if self.tab == 1: # Asset
                self.assetSelected(1)
            elif self.tab == 2: # Shot
                self.shotSelected(1)

        self.close()

    def getDate(self):
        #date = QDate.currentDate().toString("MM/dd/yyyy")
        date = QDate.currentDate()
        return date

    def getTime(self):
        #time = QTime.currentTime().toString()
        time = QTime.currentTime()
        return time
