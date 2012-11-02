# -*- coding: utf-8 -*-



#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
from Core.Note.Note import NoteContainer, Note
from Core.Workcode.Workcode import StandardTreeModel
from Core.iPipelineActions import iPipelineActions
from Core.iPipelineInfo import iPipelineInfo
from Core.iPipelineInit import iPipelineInit
from Core.iPipelineUtility import iPipelineUtility
from Core.itemModel import *
from Gui.Functions.assistantFunctions import assistantFunctions
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from components.addons.bookmarks.bookmarks import Bookmarks
from components.addons.information.information import Information
from components.addons.layerManager.layerManager import layerManager
from components.addons.publishWindow.publishWindow import PublishWindow
from components.addons.publishWindowAni.publishWindowAni import PublishWindowAni
from components.addons.workcodeManager.workcodeManager import WorkcodeManager
from components.tools.animation.animImport.animImport import AnimImport
from components.tools.animation.animTransfer.animTransfer import AnimTransfer
from components.tools.animation.multipleImportReference.multipleImportReference import MultipleImportReference
from components.tools.animation.selectionTool.selectionTool import SelectionTool
from components.tools.finalize.geoBake.geoBake import GeoBake # new mel script
from conndb import *
from foundations.globals.constants import Constants
from foundations.tractor import Tractor
#from lib.finalize.ShowCase.ShowCase import mrgo_CacheDialog, mrgoImportTool
from lib.itemModel import *
from logs import Logs, Logs
from xml2 import iXML
from xml_new import XmlNew
import Core.Note.Note2
import glob
import notice
import os , stat
import re
import sys
import ui.common
import userInfo
import logging
from xsend import Message


try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA = True
except :
    MAYA = False
    
    
#***********************************************************************************************
#***    Global Variables.
#***********************************************************************************************
APPLICATION_PATH = Constants.applicationDirectory
NO_PREVIEW_FILENAME = APPLICATION_PATH+"resources/noPreview.jpg"
SCENEFILE_RE = re.compile("v[0-9]{2}_w[0-9]{2}.mb")
SCENEFILE_WITH_SUBJECT_RE = re.compile("v[0-9]{2}_w[0-9]{2}_[\w]+.mb")
VER_WIP_RE = re.compile("v[0-9]{2}_w[0-9]{2}")
VER_RE = re.compile("_v[0-9]{2}")
WIP_RE = re.compile("_w[0-9]{2}")

APPLICATION_NAME = "iPipeline v0.3.2.2"
DEV_SHOW = 0




class iPipeline(QMainWindow,
                iPipelineInit, iPipelineActions, iPipelineInfo,iPipelineUtility,
                assistantFunctions):
    
    def __init__(self, parent=None):

        QMainWindow.__init__(self, parent)
        self.userinfo = userInfo.UserInfo()
        uic.loadUi(Constants.frameworkUIFile, self)
                
        
        self.sourceModule(Constants.DI_finalize)
        self.sourceModule(Constants.DI_ani)
        if  not 'd10218' in os.getenv( 'USERNAME' ):
             self.tabWidget.removeTab(3)              
             
        if 'win' in  sys.platform:
             self.showPath = r"\\10.0.200.100"
             self.isWinOS = True         
             self.reportError_btn.hide()    
        else :
            self.isWinOS = False
            if DEV_SHOW:
                self.showPath = "/home/d10218/temp/Show"                
            else:
                self.showPath = "/show"
                
                
        self.assetTypes = []
        self.assets = []
        self.components = []
        self.sequences = []
        self.shots = []
        self.shotComponents = []
        self.initialize()
        self.asset_devTabledata = []
        self.asset_pubTabledata = []
        self.shot_devTabledata = []
        self.shot_pubTabledata = []
        self.bookmarks = Bookmarks( self )
        self.workcodeModel = StandardTreeModel(self)
        self.workcodedata = self.workcodeModel.load(QString(Constants.workcodeFile))
            
        self.updateUI(0)    
        self.createConnections()
        try : 
            import MySQLdb
            self.db = MySQLdb.connect(host=Constants.wdSQLaddress , user='idea' , passwd='idea' , port=3366, db='wd' , charset='utf8')                
            DBconn = 'connected'
            self.db.close()
        except : 
            DBconn = 'disconnected'
        if self.userinfo.checkAccount():
            self.label_15.hide()                 
            self.userNameLineEdit.hide()
            self.userName = self.userinfo.num
            theMessage = u' 사번 : %s        이름 : %s        Department : %s        DB server : %s' % (self.userinfo.num , self.userinfo.name , self.userinfo.dept , DBconn)
            self.ip_statusBar.showMessage(theMessage) 
        else:
            
            if not self.isWinOS:
                self.ip_statusBar.showMessage(u'개인 계정으로 로그인 바랍니다. 조만간 개인 계정이 막혀 마야 사용이 불가능 해집니다.')
                self.userNameLineEdit.setText(self.userName)
            else :
                self.ip_statusBar.showMessage(u'Windows     DB server : %s' % DBconn)
                self.userNameLineEdit.setText(self.userName)
            
        
        self.setWindowTitle(APPLICATION_NAME) 
        self.setStyleSheet("font-size: 11px")
        

        
        self.projNameCombo.addItems(self.getDirectoryList(self.showPath))
        self.loadSettings()
#===============================================================================
#        
# Global
#        
#===============================================================================

    def createConnections(self):        
        #Global
        self.connect(self.projNameCombo, SIGNAL("currentIndexChanged(const QString&)"),
                     self.projectSelected)
        
        self.connect(self.bookmark_tbtn, SIGNAL("clicked()"),
                     self.showBookmarks )
        self.connect(self.bookmarks.bmAdd_btn, SIGNAL("clicked()"),
                     self.addBM )
        self.connect(self.bookmarks.bmDel_btn, SIGNAL("clicked()"),
                     self.delBM )
        self.connect(self.bookmarks.bookmark_list, SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
                     self.moveBookmarks )
        self.connect( self.reportError_btn , SIGNAL("clicked()"),
                     self.sendReportError )
        
        # Currently Open
        self.connect(self.currOpenSaveDevelButton, SIGNAL("clicked()"),
                     self.saveDevelSelected)
        self.connect(self.currOpenSavePublishButton, SIGNAL("clicked()"),
                     self.savePublishSelected)
        self.connect(self.currOpenCloseButton, SIGNAL("clicked()"),
                     self.closeFile)
        self.connect(self.currOpenExploreButton, SIGNAL("clicked()"),
                     self.exploreCurrent)
        self.connect(self.refreshOpenedButton , SIGNAL("clicked()") ,
                      self.refreshCurrentlyOpen) 
        self.connect(self.currOpenSnapshotButton, SIGNAL("clicked()"),
                     self.takeSnapshot)
        self.connect(self.currOpenRecordPlayblastButton, SIGNAL("clicked()"),
                     self.recordCurrentPlayblast)
        self.connect(self.preview_list, SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
                     self.playPreview)
       
       
        # ASSET Browser
        self.connect(self.assetTypeScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.updateAssetList)
        self.assetTypeScrollList.selectionModel().currentChanged.connect( self.updateAssetList )
        self.connect(self.assetScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.assetSelected)
        self.assetScrollList.selectionModel().currentChanged.connect( self.assetSelected )

        self.connect(self.componentScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.componentSelected)
        self.componentScrollList.selectionModel().currentChanged.connect( self.componentSelected )        
        self.connect(self.exploreAssetButton, SIGNAL("clicked()"),
                     lambda: self.exploreSelectd(1))
        self.connect(self.componentScrollList, SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
                     lambda: self.componentDoubleClicked( "devel"))
        self.connect(self.dev_assetTable, SIGNAL("itemDoubleClicked(QTableWidgetItem*)"),
                     lambda value: self.componentDoubleClicked( "devel", value) )
        self.connect(self.pub_assetTable, SIGNAL("itemDoubleClicked(QTableWidgetItem*)"),
                     lambda value: self.componentDoubleClicked( "publish", value))
        
        self.connect(self.dev_assetTable, SIGNAL("itemClicked(QTableWidgetItem*)"),
                     lambda value: self.selectTableItem( "devel", value) )
        self.connect(self.pub_assetTable, SIGNAL("itemClicked(QTableWidgetItem*)"),
                     lambda value: self.selectTableItem( "publish", value) )
        
        self.connect(self.assetTypeNewButton, SIGNAL("clicked()"),
                     self.newAssetTypeUI)
        self.connect(self.assetTypeRemoveButton, SIGNAL("clicked()"),
                     lambda: self.removeProcess(1, 1))
        self.connect(self.assetNewButton, SIGNAL("clicked()"),
                     self.newAssetUI)
        self.connect(self.assetRemoveButton, SIGNAL("clicked()"),
                     lambda: self.removeProcess(1, 2))
        self.connect(self.componentNewButton, SIGNAL("clicked()"),
                     self.newAssetComponentUI)
        self.connect(self.componentRemoveButton, SIGNAL("clicked()"),
                     lambda: self.removeProcess(1, 3))
        
        
        # Shot Browser
        self.connect(self.sequenceScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.updateShotList)
        self.sequenceScrollList.selectionModel().currentChanged.connect( self.updateShotList )
        self.connect(self.shotScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.shotSelected)
        self.shotScrollList.selectionModel().currentChanged.connect( self.shotSelected )
        
        self.connect(self.shotComponentScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.shotComponentSelected)
        self.shotComponentScrollList.selectionModel().currentChanged.connect( self.shotComponentSelected )
        
        self.connect(self.shotComponentScrollList, SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
                     lambda: self.componentDoubleClicked( "devel"))
        self.connect(self.dev_shotTable, SIGNAL("itemDoubleClicked(QTableWidgetItem*)"),
                     lambda value: self.componentDoubleClicked( "devel", value) )
        self.connect(self.pub_shotTable, SIGNAL("itemDoubleClicked(QTableWidgetItem*)"),
                     lambda value: self.componentDoubleClicked( "publish", value) )
        
        self.connect(self.dev_shotTable, SIGNAL("itemClicked(QTableWidgetItem*)"),
                     lambda value: self.selectTableItem( "devel", value) )
        self.connect(self.pub_shotTable, SIGNAL("itemClicked(QTableWidgetItem*)"),
                     lambda value: self.selectTableItem( "publish", value) )
        
        self.connect(self.sequenceNewButton, SIGNAL("clicked()"),
                     self.newSequenceUI)
        self.connect(self.sequenceRemoveButton, SIGNAL("clicked()"),
                     lambda: self.removeProcess(2, 1))
        self.connect(self.shotNewButton, SIGNAL("clicked()"),
                     self.newShotUI)
        self.connect(self.shotRemoveButton, SIGNAL("clicked()"),
                     lambda: self.removeProcess(2, 2))
        self.connect(self.shotComponentNewButton, SIGNAL("clicked()"),
                     self.newShotComponentUI)
        self.connect(self.shotComponentRemoveButton, SIGNAL("clicked()"),
                     lambda: self.removeProcess(2, 3))
        self.connect(self.exploreShotButton, SIGNAL("clicked()"),
                     lambda: self.exploreSelectd(2))
        
        # context menu  
        self.dev_assetTable.setContextMenuPolicy(Qt.CustomContextMenu)      
        self.pub_assetTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.dev_assetTable, SIGNAL("customContextMenuRequested(const QPoint&)"),
                     lambda value: self.componentMenu(value, 1, "devel"))        
        self.connect(self.pub_assetTable, SIGNAL("customContextMenuRequested(const QPoint&)"),
                     lambda value: self.componentMenu(value, 1, "publish"))
        self.dev_shotTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pub_shotTable.setContextMenuPolicy(Qt.CustomContextMenu)      
        self.connect(self.dev_shotTable, SIGNAL("customContextMenuRequested(const QPoint&)"),
                     lambda value: self.componentMenu(value, 2, "devel"))        
        self.connect(self.pub_shotTable, SIGNAL("customContextMenuRequested(const QPoint&)"),
                     lambda value: self.componentMenu(value, 2, "publish"))
        
        
        
    def componentMenu(self, pos, tab, mode):              
        saveAsCurrentDevAct = self.createAction("Create Current Scene into Devel" , self.saveAsCurrentDev)
        refAssetAct = self.createAction("reference (assetName:)", lambda: self.importReference(tab, "reference (assetName:)", mode, 0))
        importAssetAct = self.createAction("import (assetName:)", lambda: self.importReference(tab, "import (assetName:)", mode, 0))
        multipleImportAct = self.createAction("multiple import (assetname:)", lambda: self.multipleSelected(tab, mode, 1))
        multipleRefAct = self.createAction("multiple reference (assetname:)", lambda: self.multipleSelected(tab, mode, 0))
        importAct = self.createAction("import", lambda: self.importReference(tab, "import", mode, 0))        
        menu = QMenu()
        if mode == 'devel':
            menu.addAction(saveAsCurrentDevAct)
            menu.addSeparator()
        menu.addAction(refAssetAct)
        menu.addAction(multipleRefAct)
        menu.addSeparator()
        menu.addAction(importAct)
        menu.addAction(importAssetAct)
        menu.addAction(multipleImportAct)
        if tab == 1 :
            if mode == 'devel':
                menu.exec_(self.dev_assetTable.mapToGlobal(pos))                
            else :
                menu.exec_(self.pub_assetTable.mapToGlobal(pos))                
        else :
            if mode == 'devel':
                menu.exec_(self.dev_shotTable.mapToGlobal(pos))                
            else :
                menu.exec_(self.pub_shotTable.mapToGlobal(pos))

        
    def showBookmarks(self):        
        if self.bookmark_tbtn.isChecked():
            self.bookmarks.show()
            self.bookmarks.setGeometry( 430, 70,370,384  )
        else :
            self.bookmarks.close()

    def addBM(self):
        tab = self.tabWidget.currentIndex()
        level1 , level2 , level3 = self.getCurrentlySelectedItem(tab, 3)
        showcode = str( self.projNameCombo.currentText() )
        if '' in [level1,level2,level3,showcode]:
            return
        self.bookmarks.addbmitem( showcode,tab,level1,level2,level3 )                
        settings = QSettings("DIGITAL idea", "iPipeline")
        settings.setValue("bookmarks", self.bookmarks.BMlist )
        
    def delBM(self):        
        if self.bookmarks.bookmark_list.currentRow() == -1 : 
            return 
        self.bookmarks.delbmitem( self.bookmarks.bookmark_list.currentRow() )
        settings = QSettings("DIGITAL idea", "iPipeline")
        settings.setValue("bookmarks", self.bookmarks.BMlist )
    
    def moveBookmarks(self):
        if self.bookmarks.bookmark_list.currentRow() == -1 : 
           return 
        bm_list = self.bookmarks.bookmark_list
        targetText = self.bookmarks.BMlist[ self.bookmarks.bookmark_list.currentRow() ]
        showcode , atype , level1 , level2 , level3  = targetText.split('  ')
        tab = 1 if atype == 'asset' else 2 
        self.projNameCombo.setCurrentIndex( self.projNameCombo.findText(showcode) )        
        self.tabWidget.setCurrentIndex( tab )
        if tab == 1:
            self.assetTypeScrollList.setCurrentRow( self.findIndexlistWidget(self.assetTypeScrollList, level1) ) 
            self.updateAssetList(1)
            self.assetScrollList.setCurrentRow( self.findIndexlistWidget(self.assetScrollList ,level2) ) 
            self.assetSelected(1)
            self.componentScrollList.setCurrentRow( self.findIndexlistWidget(self.componentScrollList,level3) ) 
            self.componentSelected()
        elif tab == 2 :                                  
            self.sequenceScrollList.setCurrentRow( self.findIndexlistWidget( self.sequenceScrollList , level1 ) )
            self.updateShotList(True)            
            self.shotScrollList.setCurrentRow( self.findIndexlistWidget( self.shotScrollList , level2 ) )            
            self.shotSelected(1)             
            self.shotComponentScrollList.setCurrentRow( self.findIndexlistWidget( self.shotComponentScrollList , level3 ) )
            self.shotComponentSelected()
        self.bookmark_tbtn.setChecked( 0 )
        self.bookmarks.close()
            
    def sendReportError(self):
        level1 , level2 , level3 = self.getCurrentlySelectedItem(self.tabWidget.currentIndex() , 3)        
        self.reportError( self.userinfo.dept,self.userinfo.name ,self.tabWidget.currentIndex()
                          ,self.projNameCombo.currentText() ,level1 ,level2,level3 )
        self.mssg(u'잠시 기다리시면 방문 수리 해드리겠습니다. ')
        
    def projectSelected(self, item):
        self.activateProject(item)        
        self.updateAssetTypeList()   
        self.updateSequenceList()
        self.assetScrollList.setDragEnabled(False)
        self.shotScrollList.setDragEnabled(False)
        self.assetScrollList.mouseMoveEvent = None
        self.shotScrollList.mouseMoveEvent = None
        
        return True
    
    def exploreSelectd(self, tab):
        selectedItem = self.getCurrentlySelectedItem(tab, 3)
        self.openLocation(tab, selectedItem[0], selectedItem[1], selectedItem[2])

#    def updateComment(self , tab ):
#        level1 , level2 , level3 = self.getCurrentlySelectedItem(tab, 3)
#        project = str( self.projNameCombo.currentText() )
#        db = DBhandler()
#        db.dbConn()
#        if tab ==1: 
#            if level1 != '' and level2!='' and level3!='':            
#                self.asset_comment = db.getFetch( "call getcomment('%s','%s','%s','%s',1)" %(project,level1,level2,level3) )
#                self.asset_cmmtList.clear()                
#                self.asset_cmmtList.addItems( [ x[1] for x in self.asset_comment] )
#                self.asset_cmmtList.setAlternatingRowColors(True)
                
#        elif tab == 2:
#            
#            if level1 != '' and level2!='' and level3!='':
#                self.shot_comment = db.getFetch( "call getcomment('%s','%s','%s','%s',2)" %(project,level1,level2,level3) )
#                self.shot_cmmtList.clear()              
#                for i , y in enumerate( [ x[1] for x in self.shot_comment] ):
#                    item = QListWidgetItem( y )
#                    if i %2 == 0 :
#                        item.setBackground(Qt.gray)                    
#                    self.shot_cmmtList.addItem( item )
#                                    

    def componentDoubleClicked(self, mode, item=None):           
        selected = 1        
        self.currOpenTab = self.tabWidget.currentIndex()
        level1 , level2 , level3 = self.getCurrentlySelectedItem(self.currOpenTab, 3)
        self.currOpenProjectName = self.projNameCombo.currentText()
        self.currOpenSubject = ""        
        self.currOpenLevel1 = level1
        self.currOpenLevel2 = level2
        self.currOpenLevel3 = level3
        
        devFolder = str(self.getFileName(self.currOpenTab, level1 , level2 , level3 , "devFolder"))        
        sceneFile = self.getFileName(self.currOpenTab, level1 , level2 , level3 , "devel")

        
        if mode == "devel":
            path = devFolder
        elif mode == "publish":
            selected = 0
            path = str(self.getFileName(self.currOpenTab, level1 , level2 , level3 , "pubFolder"))
        if item is not None:             
            if self.currOpenTab == 1 :                
                if mode == "devel":
                    itemData = self.asset_devTabledata[ item.row() ]
                else:
                    itemData = self.asset_pubTabledata[ item.row() ]
            elif self.currOpenTab ==2 :                               
                if mode == "devel":
                    itemData = self.shot_devTabledata[ item.row() ]
                else :
                    itemData = self.shot_pubTabledata[ item.row() ]            
            self.componentOpened(devFolder, itemData[0], mode, self.currOpenTab, level1 , level2 , level3 , selected, path)         
        else: # item is None
                              # 버전별 씬파일 보여주는 다이얼로그            
            sceneFolder = str(self.getFileName(self.currOpenTab, level1 , level2 , level3 , "sceneFolder"))
            mayaFiles = glob.glob(sceneFolder + "*.mb")
            defaultFiles = filter(SCENEFILE_RE.search, mayaFiles)
            subjectFiles = filter(SCENEFILE_WITH_SUBJECT_RE.search, mayaFiles)
            subjectLists = {}
            for i in subjectFiles:
                fileName = os.path.basename(i).rsplit('_', 1)[-1]
                basename = os.path.splitext(fileName)[0]
                if subjectLists.get(basename) is None:
                    subjectLists[basename] = []
                subjectLists[basename].append(i)
            for subject in subjectLists.keys():
                subjectLists[subject] = sorted(subjectLists[subject])
            buffer = []
            for subject in subjectLists.keys():
                buffer.append(os.path.basename(subjectLists[subject][-1]))
            if len(defaultFiles):
                buffer.append(os.path.basename(defaultFiles[-1]))
            buffer = sorted(buffer, reverse=True)
            if len(buffer) == 1:
                logging.warning('buffer1 : %s' % buffer[-1] )
                sp = QListWidgetItem(buffer[0])
                self.componentOpened(devFolder, sceneFile, mode, self.currOpenTab, level1 , level2 , level3 , selected, path, sp)                
            elif len(buffer) == 0:
                logging.warning('buffer0')
                self.componentOpened(devFolder, sceneFile, mode, self.currOpenTab, level1 , level2 , level3 , selected,  path)                    
            else:     
                logging.warning( 'componentUI' )          
        

    
    def componentOpened(self, devFolder, sceneFile, mode, tab, level1 , level2 , level3 , selected, path, sp=None):             
        if sp is not None:
#            if self.isWinOS:
#                sceneFile = path + "\\scenes\\" + sp.text()
#            else :
            sceneFile = path + "/scenes/" + sp.text()
        self.currOpenFile = sceneFile.replace('/' , '\\') if self.isWinOS else sceneFile
        
        if not self.openItem("devel", devFolder, str(sceneFile)):              
            return        
        sceneFolder = str(self.getFileName(tab, level1 , level2 , level3 , "sceneFolder", 0, 1))
        devFolder   = str(self.getFileName(tab, level1 , level2 , level3 , "devFolder"))
        
        previewImage = path + ("/scenes/.%s.thumb.jpg" % os.path.basename(str(sceneFile)))
        if not QFileInfo(previewImage).isFile():
            previewImage = NO_PREVIEW_FILENAME
        
        if sceneFile == "":
            ver = "v01"
            wip = "w01"
            _filename = "%s_%s_%s_%s.mb" % (level2, level3, ver, wip)
            sceneFile = os.path.join(sceneFolder, str(_filename))
        else:                 
            ver = VER_RE.findall(str(sceneFile))[0][1:]
            if mode == "devel":
                wip = WIP_RE.findall(str(sceneFile))[0][1:]
            else:
                wip = ""
            if mode == "devel":
                ex = "(?<=w[0-9]{2}_).+?(?=.mb)"
            elif mode == "publish":
                ex = "(?<=v[0-9]{2}_).+?(?=.mb)"
            basename = os.path.basename(str(sceneFile))
            self.currOpenSubject = re.search( ex , basename ).group() if re.search( ex , basename ) != None else ''
            
                
        if tab == 1:
            tabName = "Asset"
            location = self.assetLocationField.text()
        elif tab == 2:
            tabName = "Shot"
            location = self.shotLocationField.text()        

        self.currOpenFileNameLabel.setText(os.path.basename(str(sceneFile)))
        self.currOpenProjectField.setText(self.currOpenProjectName)
        self.currOpenProdField.setText(tabName)
        self.currOpenFileField.setText(mode)
        self.currOpenSubjectField.setText(self.currOpenSubject)
        self.currOpenLevel1Field.setText( level1 )
        self.currOpenLevel2Field.setText( level2 )
        self.currOpenLevel3Field.setText( level3)
        self.currOpenVerField.setText(ver)
        self.currOpenWipField.setText(wip)
        self.currOpenSaveDevelButton.setEnabled(selected)
        self.currOpenSavePublishButton.setEnabled(selected)        
        self.currOpenCloseButton.setEnabled(True)
        self.currOpenSnapshotButton.setEnabled(True)
        self.currOpenRecordPlayblastButton.setEnabled(selected)
        self.currOpenExploreButton.setEnabled(True)
        self.currOpenLocationField.setText(location)
        self.currOpenPreviewImage.setPixmap(QPixmap(previewImage))
        
        self.tabWidget.setCurrentIndex(0)
        try:
            self.componentFileUI.close()
        except AttributeError:
            logging.info( 'Attribute Error' )
                        
        self.previewFiles = [ (os.path.basename(x).split('.')[0],x )for x in glob.glob( devFolder + os.sep + 'preview/*.mov')[::-1] ] if glob.glob( devFolder + os.sep + 'preview/*.mov') else []
        if self.previewFiles :
            self.preview_list.clear()
            self.preview_list.addItems( [x[0] for x in self.previewFiles] )

        wipmodel = WIPmodel(sceneFile)
        self.created_lb.setText( str(wipmodel.getCreatedDate() ) )
        self.latestUpdate_lb.setText( str(wipmodel.getLatestDate() ))
        self.finaldate_lb.setText( str(wipmodel.getFinalDate() ))
        self.elasedTime_lb.setText( str(wipmodel.getElapsedTime() ))
        
      

    def importReference(self, tab, ex, mode, atype):
        if not self.confirmDialog("Confirm", 'Are you sure you want to run "%s"?' % ex):
            return
        currSelected = self.getCurrentlySelectedItem(tab, 3)
        if mode == "devel":
            if tab == 1:
#                item = self.dev_assetTable.currentItem()
                item = self.asset_devTabledata[ self.dev_assetTable.currentRow() ]
            elif tab == 2:
#                item = self.dev_shotTable.currentItem()
                item = self.shot_devTabledata[ self.dev_shotTable.currentRow() ]
            path = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "devFolder")
        elif mode == "publish":
            if tab == 1:
#                item = self.pub_assetTable.currentItem()
                item = self.asset_pubTabledata[ self.pub_assetTable.currentRow() ]
            elif tab == 2:
#                item = self.pub_shotTable.currentItem()
                item = self.shot_pubTabledata[ self.pub_shotTable.currentRow() ]
            path = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "pubFolder")
        if item is None:
            return
        itemName = os.path.basename( item[0] )

        assetName = currSelected[1]
        fileName = item[0]
#        fileName = path + "/scenes/" + itemName
        
        if atype: # filename
            namespace = os.path.splitext(str(itemName))[0]  
        else: # assetName
            namespace = str(assetName)            
        if ex == "reference (assetName:)":
            if MAYA :
#                cmds.file( fileName, r=1 , gl=1,shd='shadingNetworks',namespace=namespace,lrd='all',options='v=0')
                commd = "file -r -gl -shd \"shadingNetworks\" -namespace \"%s\" -lrd \"all\" -options \"v=0\" \"%s\"" % (namespace, fileName)                
                mel.eval(commd)                                
        elif ex == "import (assetName:)":
            if MAYA :
                mel.eval("file -import -namespace \"%s\" -ra true -options \"v=0\"  -pr -loadReferenceDepth \"all\" \"%s\"" % (namespace, fileName))                
        elif ex == "import":
            if MAYA :
                mel.eval("file -import -type \"mayaBinary\" -rdn -rpr \"clash\" -options \"v=0;p=17\"  -pr -loadReferenceDepth \"all\" \"%s\"" % (fileName))
                
    def multipleSelected(self, tab, mode, sel):
        self.multipleImportUI = QDialog(self)
        label = QLabel("Number of Copies:")
        numRerference = QSpinBox()
        numRerference.setRange(1, 1000)
        ok = QPushButton("Ok")
        close = QPushButton("Close")
        self.connect(ok, SIGNAL("clicked()"),
                     lambda: self.multipleImport(sel, numRerference.value(), tab, mode))
        self.connect(close, SIGNAL("clicked()"),
                     self.multipleImportUI.close)
        layout2 = QHBoxLayout()
        layout2.addWidget(ok)
        layout2.addWidget(close)
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(numRerference)
        layout.addLayout(layout2)
        self.multipleImportUI.setLayout(layout)
        self.multipleImportUI.setWindowTitle("Multiple Import")
        self.multipleImportUI.show()

    def multipleImport(self, sel, numItems, tab, mode):
        currSelected = self.getCurrentlySelectedItem(tab, 3)
        if mode == "devel":
            if tab == 1:
                item = self.asset_devTabledata[ self.dev_assetTable.currentRow() ]
#                item = self.dev_assetTable.currentItem()
            elif tab == 2:
                item = self.shot_devTabledata[ self.dev_shotTable.currentRow() ]
#                item = self.dev_shotTable.currentItem()
            path = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "devFolder")
        elif mode == "publish":
            if tab == 1:
#                item = self.pub_assetTable.currentItem()
                item = self.asset_pubTabledata[ self.pub_assetTable.currentRow() ]
            elif tab == 2:
#                item = self.pub_shotTable.currentItem()
                item = self.shot_pubTabledata[ self.pub_shotTable.currentRow() ]
            path = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "pubFolder")
        if item is None:
            return
        itemName = os.path.basename( item[0] )
        assetName = str(currSelected[1])
        fileName = item[0]
        if sel:
            name = "multiple import (assetname:)"
            command = "Import"
        else:
            name = "multiple reference (assetname:)"
            command = "Reference"
        if not self.confirmDialog("Confirm", 'Are you sure you want to run "%s"?' % name):
            return
        if MAYA :
            mel.eval('DI_multiple%s %s "%s" "%s"' % (command, numItems, assetName, fileName))
        self.multipleImportUI.close()
        
        
        
        
#===============================================================================

# Asset Tab

#===============================================================================

    def updateAssetTypeList(self):
        currSelected = self.getCurrentlySelectedItem(1, 1)
        self.assetTypeScrollList.clear()
        self.assetTypes = []
        assetTypeList = self.getChildren(1, "", "", "")
        assetTypeList.sort()
        for row, assetType in enumerate(assetTypeList):
            self.assetTypes.append(assetType)
            self.assetTypeScrollList.addItem(assetType)
            if assetType == currSelected[0]:
                self.assetTypeScrollList.setCurrentRow(row)
        self.updateAssetList(1)
        
    
    def updateAssetList(self, preserveSelection=None):
        currSelected = self.getCurrentlySelectedItem(1, 2)
        self.assetScrollList.clear()
        self.assets = []
        active = 0
        if len(currSelected[0]):
            assetList = self.getChildren(1, currSelected[0], "", "")
            assetList.sort()
            for row, asset in enumerate(assetList):
                active = 1
                self.assets.append(asset)
                self.assetScrollList.addItem(asset)
                if ((asset == currSelected[1]) and (preserveSelection == 1)):                    
                    self.assetScrollList.setCurrentRow(row)
        if self.isSuperUser:
            self.assetTypeRemoveButton.setEnabled(len(currSelected[0]))
        self.assetNewButton.setEnabled(len(currSelected[0]))
        self.assetSelected(1)
        
    
    def assetSelected(self, preserveSelection=None):
        currSelected = self.getCurrentlySelectedItem(1, 3)
        self.componentScrollList.clear()
        self.components = []
        active = 0
        selected = 1
        if currSelected[1] == "":
            selected = 0        
        if self.isSuperUser:
            self.assetRemoveButton.setEnabled(selected)
        self.componentNewButton.setEnabled(selected)
        if selected:
            compList = self.getChildren(1, currSelected[0], currSelected[1], "")
            compList.sort()
            # updateShotMenus(currSelected[0], currSelected[1])
            for row, component in enumerate(compList):
                active = 1
                self.components.append(component)
                self.componentScrollList.addItem(component)
                if ((currSelected[2] == component) and (preserveSelection == 1)):                    
                    self.componentScrollList.setCurrentRow(row)
        self.componentSelected()

    def componentSelected(self):
        currSelected = self.getCurrentlySelectedItem(1, 3)
        selected = 1
        if currSelected[2] == "":
            selected = 0
        if self.isSuperUser:
            self.componentRemoveButton.setEnabled(selected)
        self.loadBrowse()        
        self.assetInformation()        
        

    def newAssetTypeUI(self):
        assetType, ok = QInputDialog.getText(self, "new asset type", "asset type name\n (no spaces or special characters):\n")
        if ok:
            if not self.confirmDialog("Confirm", 'Are you sure you want to create "%s"?' % assetType):
                return
            result = self.createNewItem(1, assetType, "", "", "folder")
            if len(result):
                self.updateAssetTypeList()

    def newAssetUI(self):
        selectedItem = self.getCurrentlySelectedItem(1, 1)
        assetName, ok = QInputDialog.getText(self, "create new asset", "asset name (no spaces or special characters):")
        if ok:
            if not self.confirmDialog("Confirm", 'Are you sure you want to create "%s"?' % assetName):
                return
            
            result = self.createNewItem(1, selectedItem[0], assetName, "", "folder")
            if len(result):
                self.updateAssetList(1)
                
    def newAssetComponentUI(self):
        selectedItem = self.getCurrentlySelectedItem(1, 3)
        self.taskUI(1, selectedItem[0], selectedItem[1], selectedItem[2])
        

    def assetInformation(self):        
        tab = 1
        level1 , level2 , level3 = self.getCurrentlySelectedItem(1, 3)
        folder = self.getFileName(tab, level1 , level2 , level3, "folder")
        if self.isWinOS:
            folder.replace( '/' , '\\')            
        self.assetLocationField.setText(folder)       
#        self.updateComment(1)  
        
    def loadBrowse(self):        
        tab= self.tabWidget.currentIndex()        
        level1 , level2 , level3 = self.getCurrentlySelectedItem( tab, 3)        
        if level1 == '' or level2 == '' or level3 == '':                             
            return False
        devPath = self.getFileName(tab, level1, level2, level3, "devFolder")
        pubPath = self.getFileName(tab, level1, level2, level3, "pubFolder")
        if self.isWinOS:
            devPath = devPath.replace( '/' , '\\' )
            pubPath = pubPath.replace( '/' , '\\' )
        devFiles =  self.getFiles(devPath, "devel", True)
        pubFiles =  self.getFiles(pubPath, "publish", True)
        project = str( self.projNameCombo.currentText() )
        readXML = 1
        
        
        if readXML :
            historyFile = self.getFileName(tab, level1, level2, level3, "historyFile")
            devTabledata = []
            pubTabledata = []
            for f in devFiles:
                if self.checkLevel2InFilename(f ,fileParser(f)['level2'] ):
                    fileinfo = fileParser(f)
                    ver = fileinfo['ver']
                    wip = fileinfo['wip']
                    subject = fileinfo['subject']
                    author = findOwner(f) if findOwner(f) !='' else self.finduser_nc( historyFile , ver , wip , subject)
                    comment = self.getComment_DB( tab , project , level1 , level2 , level3 , ver , wip , subject)
#                    comment = self.getComment_nc( historyFile, ver , wip , subject)
                    devTabledata.append( [f , author , fileinfo , time.ctime(os.stat(f)[stat.ST_MTIME]) , comment ] )
                
            for f in pubFiles:
                if self.checkLevel2InFilename(f ,fileParser(f)['level2'] ):
                    fileinfo = fileParser(f)
                    ver = fileinfo['ver']
                    wip = fileinfo['wip']
                    subject = fileinfo['subject']
                    author = findOwner(f) if findOwner(f) !='' else self.finduser_nc( historyFile , ver , wip , subject)
                    comment = self.getComment_DB( tab , project , level1 , level2 , level3 , ver , wip , subject)
#                    comment = self.getComment_nc( historyFile, ver , wip , subject)                    
                    pubTabledata.append( [f , author , fileinfo , time.ctime(os.stat(f)[stat.ST_MTIME]) , comment ] )
                    
        else :            
#            comment = self.getComment_DB( tab , project , level1 , level2 , level3 , ver , wip , subject)            
            devTabledata = [ [x , findOwner(x) , fileParser(x) , time.ctime(os.stat(x)[stat.ST_MTIME])  ] for x in devFiles \
                            if self.checkLevel2InFilename(x ,fileParser(x)['level2'] )] 
            pubTabledata = [ [x , findOwner(x) , fileParser(x) , time.ctime(os.stat(x)[stat.ST_MTIME]) ] for x in pubFiles \
                            if self.checkLevel2InFilename(x ,fileParser(x)['level2'] )]

        if  tab ==1:
            self.asset_devTabledata = devTabledata
            self.asset_pubTabledata = pubTabledata
            devTable = self.dev_assetTable
            pubTable = self.pub_assetTable
            
        elif tab ==2 :
            self.shot_devTabledata =  devTabledata 
            self.shot_pubTabledata =  pubTabledata
            devTable = self.dev_shotTable
            pubTable = self.pub_shotTable
        
        devTable.setRowCount( len( devTabledata ) )
        pubTable.setRowCount( len( pubTabledata ) )
        devTable.setColumnWidth(0 , 50)
        pubTable.setColumnWidth(0 , 50)
        devTable.setColumnWidth(1 , 100)
        pubTable.setColumnWidth(1 , 100)
        devTable.setColumnWidth(2 , 40)
        devTable.setColumnWidth(3 , 40)        
        pubTable.setColumnWidth(2 , 40)
        devTable.setColumnWidth(4 , 120)        
        pubTable.setColumnWidth(3 , 120)
        devTable.setColumnWidth(5 , 160)
        pubTable.setColumnWidth(4 , 160)
        devTable.setColumnWidth(6 , 200)
        pubTable.setColumnWidth(5 , 200)

        for i,x in enumerate( devTabledata ):            
            devTable.setItem( i , 0 , QTableWidgetItem( x[1] ) )
            devTable.setItem( i , 1 , QTableWidgetItem( x[2]['level2'] ) )
            devTable.setItem( i , 2 , QTableWidgetItem( x[2]['ver'] ) )
            devTable.setItem( i , 3 , QTableWidgetItem( x[2]['wip'] ) )
            devTable.setItem( i , 4 , QTableWidgetItem( x[2]['subject'] ) )
            devTable.setItem( i , 5 , QTableWidgetItem( x[3] ) )
            devTable.setItem( i , 6 , QTableWidgetItem( x[4] ) )
            devTable.resizeRowsToContents()
            devTable.setRowHeight( i , 22)
                  
            
        for i,x in enumerate( pubTabledata ):
            pubTable.setItem( i , 0 , QTableWidgetItem( x[1] ) )
            pubTable.setItem( i , 1 , QTableWidgetItem( x[2]['level2'] ) )
            pubTable.setItem( i , 2 , QTableWidgetItem( x[2]['ver'] ) )                
            pubTable.setItem( i , 3 , QTableWidgetItem( x[2]['subject'] ) )
            pubTable.setItem( i , 4 , QTableWidgetItem( x[3] ) )
            pubTable.setItem( i , 5 , QTableWidgetItem( x[4] ) )
            pubTable.resizeRowsToContents()
            pubTable.setRowHeight( i , 22)
            

    def selectTableItem(self , mode , item = None ):
        selected = 1        
        self.currOpenTab = self.tabWidget.currentIndex()
        level1 , level2 , level3 = self.getCurrentlySelectedItem(self.currOpenTab, 3)
        self.currOpenProjectName = self.projNameCombo.currentText()
        self.currOpenSubject = ""        
        self.currOpenLevel1 = level1
        self.currOpenLevel2 = level2
        self.currOpenLevel3 = level3
        
        if item is not None:             
            if self.currOpenTab == 1 : 
                previewImage_lb = self.assetPreviewImage               
                if mode == "devel":
                    itemData = self.asset_devTabledata[ item.row() ]
                else:
                    itemData = self.asset_pubTabledata[ item.row() ]
            elif self.currOpenTab ==2 : 
                previewImage_lb = self.shotPreviewImage                              
                if mode == "devel":
                    itemData = self.shot_devTabledata[ item.row() ]
                else :
                    itemData = self.shot_pubTabledata[ item.row() ]
        
        previewImage = os.path.dirname( str(itemData[0]) ) + ("/.%s.thumb.jpg" % os.path.basename(str(itemData[0])))        
        if not QFileInfo(previewImage).isFile():
            previewImage = NO_PREVIEW_FILENAME
            
        previewImage_lb.setPixmap( QPixmap( previewImage ) )
           
    def newSequenceUI(self):
        sequence, ok = QInputDialog.getText(self, "new sequence", "sequence name\n (no spaces or special characters):\n")
        if ok:
            if not self.confirmDialog("Confirm", 'Are you sure you want to create "%s"?' % sequence):
                return
            result = self.createNewItem(2, sequence, "", "", "folder")
            if len(result):
                self.updateSequenceList()
                
    def newShotUI(self):
        selectedItem = self.getCurrentlySelectedItem(2, 1)
        assetName, ok = QInputDialog.getText(self, "Create New Shot", "shot name (no spaces or special characters):")
        if ok:
            if not self.confirmDialog("Confirm", 'Are you sure you want to create "%s"?' % assetName):
                return
            result = self.createNewItem(2, selectedItem[0], assetName, "", "folder")
            if len(result):
                self.updateShotList(1)

    def newShotComponentUI(self):
        selectedItem = self.getCurrentlySelectedItem(2, 3)
        self.taskUI(2, selectedItem[0], selectedItem[1], selectedItem[2])

    def taskUI(self, tab, level1, level2, level3):
        w = WorkcodeManager(tab, level1, level2, level3, self.workcodedata, self.userinfo.name , self)
        w.show()
                        
    def updateSequenceList(self):
        currSelected = self.getCurrentlySelectedItem(2, 1)
        self.sequenceScrollList.clear()
        self.sequences = []
        sequenceList = self.getChildren(2, "", "", "")
        sequenceList.sort()
        for row, sequence in enumerate(sequenceList):
            self.sequences.append(sequence)
            self.sequenceScrollList.addItem(sequence)
            if sequence == currSelected[0]:                
                self.sequenceScrollList.setCurrentRow(row)
        self.updateShotList(True)                 
        

    def updateShotList(self, preserveSelection=None):
        currSelected = self.getCurrentlySelectedItem(2, 2)
        self.shotScrollList.clear()
        self.shots = []
        active = 0
        if len(currSelected[0]):
            shotList = self.getChildren(2, currSelected[0], "", "")
            shotList.sort()
            for row, shot in enumerate(shotList):
                active = 1
                self.shots.append(shot)
                self.shotScrollList.addItem(shot)
                if ((shot == currSelected[1]) and (preserveSelection == 1)):
                    self.shotScrollList.setCurrentRow(row)
        if self.isSuperUser:
            self.sequenceRemoveButton.setEnabled(len(currSelected[0]))
        self.shotNewButton.setEnabled(len(currSelected[0]))
        self.shotSelected(1)
        

    def shotSelected(self, preserveSelection=None):
        currSelected = self.getCurrentlySelectedItem(2, 3)
        self.shotComponentScrollList.clear()
        self.shotComponents = []
        active = 0
        selected = 1
        if currSelected[1] == "":
            selected = 0        
        if self.isSuperUser:
            self.shotRemoveButton.setEnabled(selected)
        self.shotComponentNewButton.setEnabled(selected)
        if selected:
            compList = self.getChildren(2, currSelected[0], currSelected[1], "")
            compList.sort()            
            for row, component in enumerate(compList):
                active = 1
                self.shotComponents.append(component)
                self.shotComponentScrollList.addItem(component)
                if ((currSelected[2] == component) and (preserveSelection == 1)):
                    self.shotComponentScrollList.setCurrentRow(row)
        self.shotComponentSelected()
        

    def shotComponentSelected(self):
        currSelected = self.getCurrentlySelectedItem(2, 3)
        selected = 1
        if currSelected[2] == "":
            selected = 0
        if self.isSuperUser:
            self.shotComponentRemoveButton.setEnabled(selected)
        self.shotInformation()
        self.loadBrowse()

    def shotInformation(self):
        tab = 2      
        level1 , level2 , level3 = self.getCurrentlySelectedItem(2, 3)
        folder = self.getFileName(tab, level1, level2, level3, "folder")
        self.shotLocationField.setText(folder)
#        self.updateComment(2)
                

        
        
        
#===========================================================================

#  Events

#===========================================================================        
    def saveAsCurrentDev(self ):                    
#        if not MAYA : return
        
        self.currOpenProjectName = self.projNameCombo.currentText()
        tab = self.tabWidget.currentIndex()
        level1 , level2 , level3 = self.getCurrentlySelectedItem(tab, 3)  
        
              
#        scenefile = '/show/TEMP/assets/char/linux/ani/dev/scenes/linux_ani_v01_w08.mb'
        if tab == 1:
            scenefile = self.asset_devTabledata[0][0] if self.asset_devTabledata != [] else ''
        elif tab ==2 :     
            scenefile = self.shot_devTabledata[0][0] if self.shot_devTabledata != [] else ''                        
           
        sceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1))              
        showcode = self.projNameCombo.currentText()
        
        if scenefile != '':            
            theFileParsed = fileParser( scenefile )
            basename = os.path.basename( scenefile )
            basepath = os.path.dirname( scenefile )
            mode = theFileParsed[ 'mode' ]
                    
            ver = int( theFileParsed[ 'ver' ] )
            wip = int( theFileParsed[ 'wip' ] ) if theFileParsed[ 'wip' ] != '0' else 1
            subject = theFileParsed[ 'subject' ]
            nver = str( int(ver) +1 ).zfill(2)
            nwip = str( int(wip) +1 ).zfill(2)
        else :
            scenefile = os.path.join( sceneFolder , str(level2) + '_' + str(level3) + '_v01_w01.mb' )                             
            ver = 1
            wip = 1
            nver = '01'
            nwip = '01'
            subject = ''
        
        if subject != '' :
            nbasename = '_'.join( [ str(level2) ,str(level3) , 'v'+str(ver).zfill(2) , 'w'+nwip , subject ] ) + '.mb'
            nbasename2 = '_'.join( [ str(level2) ,str(level3) , 'v'+nver , 'w'+'w01' , subject ] ) + '.mb'
        else :            
            nbasename = '_'.join( [ str(level2) ,str(level3) , 'v'+str(ver).zfill(2) , 'w'+nwip ] )+ '.mb'
            nbasename2 = '_'.join( [ str(level2) ,str(level3) , 'v'+nver , 'w01' ] )  + '.mb'
        
            
        curLatestVersion = os.path.join( sceneFolder , nbasename  )
        destinationFile = os.path.join( sceneFolder , nbasename2  )             
      
             
        info = Information("Save Current Into Devel", tab , level1 , level2, level3, 
                           ver, wip, subject, curLatestVersion, destinationFile, self)
        self.connect(info, SIGNAL("save"),
                     self.saveCurrentIntoDevel )
        info.show()
        
    def saveCurrentIntoDevel(self , destinationFile, comment, status, progress, ctime, subjectName):               
        ext = 'mb'
        tab = self.tabWidget.currentIndex()
        level1 , level2 , level3 = self.getCurrentlySelectedItem(tab, 3)                  
        
        sceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1))        
        fileName = os.path.basename(str(destinationFile))
        
        
        ver = int(VER_RE.findall(fileName)[0][2:])
        wip = int(WIP_RE.findall(fileName)[0][2:])        
        # model layer information
        if MAYA and str(level3) == 'model' and cmds.ls('model_layerInfo') == [] :
            print' creating model layer information'
            lm = layerManager()
            lm.createLMnode()
        
        theResultPath = os.path.join(sceneFolder , str(destinationFile))        
#        try:            
        cmds.file(rename=str(theResultPath))
        if ext == 'ma':
            mtype = 'mayaAscii'
        elif ext == 'mb':
            mtype = 'mayaBinary'
        else:
            mtype = 'mayaBinary'
            QMessageBox.warning(self, "warning", "openPipelineSaveWorkshop: Invalid file format (" + ext + ") specified: saving to Maya Binary")
                  
        
        cmds.file(save=True, type=mtype)
        if tab == 1:  
            result = AssetRegister(self.projNameCombo.currentText() , level1 , level2 , level3 , subjectName, ver , wip , self.userinfo.num, self.userinfo.name , comment)
        elif tab == 2:
            result = JobRegister(self.projNameCombo.currentText() , level1 , level2 , level3 , subjectName, ver , wip , self.userinfo.num , self.userinfo.name, comment)
            
        if not result:                        
            self.mssg(u'치명적 오류가 발생 하였습니다.\n아무것도 만지지 마시고 \nPipeline TD( 오호준 )에게 연락 주세요 ')
            return False

#        except :             
        
        if 'win' in sys.platform:                        
            os.system('type NUL>%s' % os.path.join(sceneFolder, str(destinationFile)))
        else:
            os.system('touch %s' % os.path.join(sceneFolder, str(destinationFile)))  
        if tab == 1 :
            result = createAsset(self.projNameCombo.currentText() , level1 , level2 , level3)
        elif tab == 2:
            result = createJob(self.projNameCombo.currentText() , level1 , level2 , level3)
        if not result:                   
            self.mssg(u'치명적 오류가 발생 하였습니다.\n아무것도 만지지 마시고 \nPipeline TD( 오호준 )에게 연락 주세요 ')
            return False               
        
        devFolder = str(self.getFileName(tab, level1, level2, level3, "devFolder"))
        try:
            if 'win' in sys.platform: 
                newProject = '/' + devFolder
            mel.eval('setProject "%s"' % devFolder)
        except:
            return True
        
        self.refreshCurrentlyOpen()     
        if MAYA :  
            self.takeSnapshot()            
        if tab == 1:
            self.loadBrowse()             
        elif tab ==2 :
            self.loadBrowse(mode=2)
        self.updateComment( tab )
        
        # xml 생성
        historyFile = str(self.getFileName(tab, level1, level2, level3, "historyFile", 0, 1))
        nc = NoteContainer()
        if QFileInfo(historyFile).isFile():
            nc.importSAX(historyFile)
        else:
            open(historyFile, 'w')
        nc.addN(Note(self.userinfo.name, # author
                    self.getDate(), # date
                    self.getTime(), # time
                    "devel", # event
                    ver, # version
                    wip, # wipversion
                    subjectName, # subject                    
                    fileName,
                    sceneFolder[:-1]
#                    status,
#                    progress,
#                    ctime,
#                    "",
#                    application
                    ))
        nc.exportXML(historyFile)
        nc.ibXML(os.path.join(str(sceneFolder), ".%s.xml" % fileName))
        
    def saveDevelSelected(self):        
        tab = self.currOpenTab
        level1 , level2 , level3 = self.currOpenLevel1 , self.currOpenLevel2 , self.currOpenLevel3        
        subjectName = str(self.currOpenSubjectField.text())
        sceneFileName = str(self.currOpenFileNameLabel.text())

        sceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1))
        sceneFiles = glob.glob(sceneFolder + "*.mb")
        
        ver_wip = VER_WIP_RE.findall(sceneFileName)[0] 
        currVer = int(ver_wip[1:3])
        currWip = int(ver_wip[-2:])

        if QFileInfo(os.path.join(sceneFolder, sceneFileName)).isFile():
            while True:
                currWip += 1
                curLatestVersion = os.path.join(sceneFolder, sceneFileName.replace(ver_wip, ver_wip[:-2] + str(currWip).zfill(2)))
                if not QFileInfo(curLatestVersion).isFile():
                    break
        else:
            curLatestVersion = os.path.join(sceneFolder, sceneFileName)

                    # 서브젝트가 존재할 때
        if len(subjectName):
            subjectLists = {}
            subjectFiles = filter(SCENEFILE_WITH_SUBJECT_RE.search, sceneFiles)
            for i in subjectFiles:
                _fileName = os.path.basename(i)
                _ver_wip = VER_WIP_RE.findall(_fileName)[0]
                fileName = _fileName.split(_ver_wip)[-1][1:] # remove underscore
                basename = os.path.splitext(fileName)[0]
                if subjectLists.get(basename) is None:
                    subjectLists[basename] = []
                subjectLists[basename].append(i)

            for subject in subjectLists.keys():
                subjectLists[subject] = sorted(subjectLists[subject])

            if len(subjectLists):
                subjects = subjectLists[subjectName]
                subjects = sorted(subjects, reverse=True)                
                destinationFile = subjects[0]
                ver = VER_WIP_RE.findall(os.path.basename(str(destinationFile)))[0]
                nVer = ver[:-2] + str(int(ver[-2:]) + 1).zfill(2)
                destinationFile = destinationFile.replace(ver, nVer)
                if curLatestVersion == destinationFile :
                    nVer = "v%s_w01" % (str(int(ver[1:3]) + 1).zfill(2))
                    destinationFile = destinationFile.replace(ver, nVer)
#                    destinationFile = develFile2Latest.replace(ver, nVer)                
            else:
                                        # 초기화 버전
                destinationFile = os.path.join(sceneFolder, "%s_%s_v01_w01_%s.mb" % (level2, level3, str(self.currOpenSubjectField.text())))
                    # 서브젝트가 존재하지 않을 때
        else:
            defaultFiles = filter(SCENEFILE_RE.search, sceneFiles)
                       
            if len(defaultFiles):
                destinationFile = sorted(defaultFiles)[-1]
                ver = VER_WIP_RE.findall(os.path.basename(str(curLatestVersion)))[0]                                                
                nVer = "v%s_w01" % (str(int(ver[1:3]) + 1).zfill(2))
                destinationFile = curLatestVersion.replace(ver, nVer)
            else:
                                        # 초기화 버전
                destinationFile = os.path.join(sceneFolder, "%s_%s_v01_w01.mb" % (level2, level3))
        
        info = Information("Save Devel", tab , level1 , level2, level3, currVer, currWip, subjectName, 
                           curLatestVersion, destinationFile, self)
        self.connect(info, SIGNAL("save"),
                     self.saveDevel)
        info.show()

    def saveDevel(self, destinationFile, comment, status, progress, ctime, subjectName , tab):
        ext = 'mb'
        level1 = self.currOpenLevel1Field.text()
        level2 = self.currOpenLevel2Field.text()
        level3 = self.currOpenLevel3Field.text()

        sceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1))        
        fileName = os.path.basename(str(destinationFile))
        
        ver = int(VER_RE.findall(fileName)[0][2:])
        wip = int(WIP_RE.findall(fileName)[0][2:])

        if MAYA:
            if str(level3) == 'model' and cmds.ls('model_layerInfo') == [] :
                print' creating model layer information'
                lm = layerManager()
                lm.createLMnode()
            else:
                print 'failed create lm node...........'        
        
        
        cmds.file(rename=str(destinationFile))
        if ext == 'ma':
            mtype = 'mayaAscii'
        elif ext == 'mb':
            mtype = 'mayaBinary'
        else:
            mtype = 'mayaBinary'
            QMessageBox.warning(self, "warning", "openPipelineSaveWorkshop: Invalid file format (" + ext + ") specified: saving to Maya Binary")

        cmds.file(save=True, type=mtype)
        if tab == 1:            
            theresult = AssetRegister(self.projNameCombo.currentText() , level1 , level2 , 
                          level3 , subjectName, ver , wip , self.userinfo.num, 
                          self.userinfo.name , comment)
        elif tab == 2:                
            theresult = JobRegister(self.projNameCombo.currentText() , level1 , level2 , 
                        level3 , subjectName, ver , wip , self.userinfo.num, 
                        self.userinfo.name , comment)
            
        if theresult :
            self.mssg(u'Database 서버에 성공적으로 등록 되었습니다.')

        
        if 'win' in sys.platform:                        
            os.system('type NUL>%s' % os.path.join(sceneFolder, str(destinationFile)))
        else:
            os.system('touch %s' % os.path.join(sceneFolder, str(destinationFile)))
              
        if str(level3) == 'model':
            lm = layerManager()
            lm.writeXML(os.path.join(sceneFolder, str(level2) + '_' + str(level3) + '.layml'))
            
        self.refreshCurrentlyOpen()     
        if MAYA :  
            self.takeSnapshot()            
        if tab == 1:
            self.loadBrowse()             
        elif tab ==2 :
            self.loadBrowse()
        self.updateComment( tab )
            
        historyFile = str(self.getFileName(tab, level1, level2, level3, "historyFile", 0, 1))
        nc = NoteContainer()
        if QFileInfo(historyFile).isFile():
            nc.importSAX(historyFile)
        else:
            open(historyFile, 'w')
        nc.addN(Note(self.userinfo.name, # author
                    self.getDate(), # date
                    self.getTime(), # time
                    "devel", # event
                    ver, # version
                    wip, # wipversion
                    subjectName, # subject
                    unicode(comment), # comment
                    fileName,
                    sceneFolder[:-1]
#                    status,
#                    progress,
#                    ctime,
#                    "",
#                    application
                    ))
        nc.exportXML(historyFile)
        nc.ibXML(os.path.join(str(sceneFolder), ".%s.xml" % fileName))

    def savePublishSelected(self):
        tab = self.currOpenTab
        level1 , level2 , level3 = self.currOpenLevel1 , self.currOpenLevel2 , self.currOpenLevel3

        subjectName = str(self.currOpenSubjectField.text())
        sceneFileName = str(self.currOpenFileNameLabel.text())
        
        pubFolder = str(self.getFileName(tab, level1, level2, level3, "pubFolder", 0, 1))
        pubScenesFolder = os.path.join(pubFolder, "scenes")
        devSceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1))

        o_filename = os.path.join(devSceneFolder, sceneFileName)
        logging.warning('level : %s,%s,%s' , level1 , level2 , level3)
        logging.warning('devSceneFolder : %s' , devSceneFolder)
        # new
        mayaFiles = glob.glob(devSceneFolder + "*.mb")
        develVer = 1
        develWip = 1

        ver_wip = VER_WIP_RE.findall(sceneFileName)[0] # return v01_w02
        currVer = int(ver_wip[1:3])
        currWip = int(ver_wip[-2:])

        if QFileInfo(os.path.join(devSceneFolder, sceneFileName)).isFile():
            while True:
                currWip += 1
                develFile = os.path.join(devSceneFolder, sceneFileName.replace(ver_wip, ver_wip[:-2] + str(currWip).zfill(2)))
                if not QFileInfo(develFile).isFile():
                    break
        else:
            develFile = os.path.join(devSceneFolder, sceneFileName)

                    # 서브젝트가 존재할 때
        if len(subjectName):
            subjectLists = {}
            subjectFiles = filter(SCENEFILE_WITH_SUBJECT_RE.search, mayaFiles)
            for i in subjectFiles:
                _fileName = os.path.basename(i)
                _ver_wip = VER_WIP_RE.findall(_fileName)[0]
                fileName = _fileName.split(_ver_wip)[-1][1:] # remove underscore
                basename = os.path.splitext(fileName)[0]
                if subjectLists.get(basename) is None:
                    subjectLists[basename] = []
                subjectLists[basename].append(i)

            for subject in subjectLists.keys():
                subjectLists[subject] = sorted(subjectLists[subject])

            if len(subjectLists):                
                subjects = subjectLists[subjectName]                
                subjects = sorted(subjects, reverse=True)
                develFile2Latest = subjects[0]
                ver = VER_WIP_RE.findall(os.path.basename(str(develFile2Latest)))[0]
                nVer = ver[:-2] + str(int(ver[-2:]) + 1).zfill(2)
                develFile2 = develFile2Latest.replace(ver, nVer)
                if develFile == develFile2:
                    nVer = "v%s_w01" % (str(int(ver[1:3]) + 1).zfill(2))
                    develFile2 = develFile2Latest.replace(ver, nVer)                
                publishFile = os.path.join(pubScenesFolder, "%s_%s_v%s_%s.mb" % (level2, level3, str(currVer).zfill(2), str(self.currOpenSubjectField.text())))
            else:  
                logging.warning( 'There are no subject list  ' )              
                return
                    # 서브젝트가 존재하지 않을 때
        else:
            defaultFiles = filter(SCENEFILE_RE.search, mayaFiles)
                             # 씬파일들이 존재할 때
            if len(defaultFiles):                                        
                develFile2Latest = defaultFiles[-1]
                                        # 선택된 파일을 버전 파싱
                ver = VER_WIP_RE.findall(os.path.basename(str(develFile2Latest)))[0]
                                        # 버전 카운트
                nVer = ver[:-2] + str(int(ver[-2:]) + 1).zfill(2)
                develFile2 = develFile2Latest.replace(ver, nVer)
                if develFile == develFile2:
                    nVer = "v%s_w01" % (str(int(ver[1:3]) + 1).zfill(2))
                    develFile2 = develFile2Latest.replace(ver, nVer)                
                publishFile = os.path.join(pubScenesFolder, "%s_%s_v%s.mb" % (level2, level3, str(currVer).zfill(2)))
            else:
                logging.warning( 'There are no default Files  ' )
                return
        
        info = PublishWindow(level2, level3, subjectName, develFile, develFile2, publishFile, o_filename, self)
        self.connect(info, SIGNAL("save"),
                     self.savePublish)
        info.show()

    def savePublish(self, enableSave, closeSceneFile, develFile, publishFile, comment, status, progress, ctime,  recordPreview , selectedAsset=[]):        
        warning = False
        ext = 'mb'
        level1 = self.currOpenLevel1Field.text()
        level2 = self.currOpenLevel2Field.text()
        level3 = self.currOpenLevel3Field.text()
        tab = self.currOpenTab        

        subjectName = str(self.currOpenSubjectField.text())
        sceneFileName = str(self.currOpenFileNameLabel.text())

        pubFolder = str(self.getFileName(tab, level1, level2, level3, "pubFolder", 0, 1))
        pubSceneFolder = os.path.join(pubFolder, "scenes")
        devSceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1))

        if not len(develFile):
            enableSave = False
            develFile = sceneFileName

        develFile = os.path.join(devSceneFolder, str(develFile))
        publishFile = os.path.join(pubSceneFolder, str(publishFile))

        scriptFolder = os.path.join(pubFolder, "script")
        animFolder = os.path.join(pubFolder, "data", "anim")

        publishBasename = os.path.basename(publishFile)
        publishBasename = os.path.splitext(publishBasename)[0]
        dirname = os.path.dirname(str(publishFile))
        basename = os.path.basename(str(publishFile))
        base, ext = os.path.splitext(basename)

        verString = VER_RE.findall(basename)[0]
        publishVer = int(verString[2:])
        publishWip = 0

        devVerString = VER_WIP_RE.findall(os.path.basename(str(develFile)))[0]
        develVer = int(devVerString[1:3])
        develWip = int(devVerString[5:7])

        # ani 워크코드만을 위한 경로
        txtFile = str(os.path.join(scriptFolder, publishBasename + '.txt'))
        animFile = str(os.path.join(animFolder, publishBasename + '.anim'))

        geoCacheFolder = os.path.join(pubFolder, "data", "geoCache", publishBasename)

        if ext == '.ma':
            mtype = 'mayaAscii'
        elif ext == '.mb':
            mtype = 'mayaBinary'
        else:
            mtype = 'mayaBinary'            

        # devel file 저장
        if enableSave:
            if self.userinfo.dept == 'Render':
                cmds.setAttr( 'defaultRenderGlobals.ren' , 'mayaSoftware' , type='string' )
                if cmds.objExists("vraySettings"):
                    cmds.delete( 'vraySettings') 
            cmds.file(rename=develFile)
            cmds.file(save=True, type=mtype)        
#            if MAYA :
#                mel.eval('DI_animTransfer "%s" "%s" %s' % (animFile, txtFile, selectedAsset))

        # publishFolder 내에 생성되지 않은 폴더가 존재할 경우 폴더 생성
        if not QDir(dirname).exists():            
            os.makedirs(dirname)
                    # 저장된 파일을 publish 폴더로 복사            
        if 'win' in sys.platform:
            try:
                cmds.file(rename=publishFile)
                cmds.file(save=True, type=mtype)
                cmds.file(rename=develFile)
                success = 1
            except:
                success = 0
        else:
            try:
                os.system('cp -rfv %s %s' % (develFile, publishFile))
                success = 1
            except : 
                success = 0
        currDate = self.getDate()
        currTime = self.getTime()       

        self.currOpenVerField.setText("v" + str(develVer).zfill(2))
        self.currOpenWipField.setText("v" + str(develWip).zfill(2))        
        self.currOpenFileNameLabel.setText(os.path.basename(develFile))        

                  

        playblastFile = ''        
        startFrame = cmds.getAttr("defaultRenderGlobals.startFrame")
        endFrame = cmds.getAttr("defaultRenderGlobals.endFrame")
        
#        if recordPreview : 
#              playblastFile = self.recordPubPlayblast()        
   
        Logs(self.userinfo.name , self.userinfo.num , self.getDate().toString() ,
              self.getTime().toString() , level2 , startFrame ,
              endFrame , publishFile , playblastFile , comment)
                
        if success == 1:
            if tab == 1:            
                theresult = AssetRegister(self.projNameCombo.currentText() , level1 , level2 , level3 , subjectName, develVer , 0 , self.userinfo.num , self.userinfo.name , comment)                
            elif tab == 2:
                theresult = JobRegister(self.projNameCombo.currentText() , level1 , level2 , level3 , subjectName, develVer , 0 , self.userinfo.num , self.userinfo.name, comment)
            if theresult : 
                self.mssg(u'Database 서버에 성공적으로 퍼블리쉬 되었습니다.')            
        else :
            self.mssg(u'치명적 오류가 발생 하였습니다.\n아무것도 만지지 마시고 \nPipeline TD( 오호준 )에게 연락 주세요 ')
        if closeSceneFile:
            self.closeFile2()

        self.refreshCurrentlyOpen()     
        if MAYA :  
            self.takeSnapshot()            
        if tab == 1:
            self.loadBrowse()             
        elif tab ==2 :
            self.loadBrowse()
        self.updateComment( tab )
   
        # xml 추가
        historyFile = str(self.getFileName(tab, level1, level2, level3, "historyFile", 0, 1))
        nc = NoteContainer()
        if QFileInfo(historyFile).isFile():
            nc.importSAX(historyFile)
        else:
            open(historyFile, 'w')
        # publish 추가
        nc.add(Note(self.userinfo.name, # author
                    currDate, # date
                    currTime, # time
                    "publish", # event
                    publishVer, # version
                    publishWip, # wipversion
                    subjectName, # subject
                    unicode(comment)     # comment
                    ))
        if enableSave:
            # devel 추가
            nc.addN(Note(self.userinfo.name, # author
                        currDate, # date
                        currTime, # time
                        "devel", # event
                        develVer, # version
                        develWip, # wipversion
                        subjectName, # subject
                        unicode(comment), # comment
                        os.path.basename(develFile),
                        str(devSceneFolder)[:-1]
#                        status,
#                        progress,
#                        ctime,
#                        "",
#                        application
                        ))
        # xml 저장
        nc.exportXML(historyFile)
        if enableSave:
            nc.ibXML(os.path.join(str(devSceneFolder), ".%s.xml" % os.path.basename(develFile)))
        devXML = os.path.join(str(devSceneFolder), ".%s.xml" % os.path.basename(develFile))
        pubXML = os.path.join(os.path.dirname(publishFile), ".%s.xml" % os.path.basename(publishFile))
        devImage = self.takeSnapshot()
        pubImage = os.path.join(pubSceneFolder, ".%s.thumb.jpg" % os.path.basename(publishFile))

        if 'win' in sys.platform:  
            os.system("copy %s %s" % (devXML, pubXML))          
            os.system("copy %s %s" % (devImage, pubImage))
        else :            
            os.system("cp -rf %s %s" % (devXML, pubXML))
            os.system("cp -rf %s %s" % (devImage, pubImage))

    def exploreCurrent(self):
        level1 = self.currOpenLevel1
        level2 = self.currOpenLevel2
        level3 = self.currOpenLevel3
        tab = self.currOpenTab
        self.openLocation(tab, level1, level2, level3, 0, 1)

    def refreshCurrentlyOpen(self):
        if not MAYA : return        
        sceneFile = cmds.file(q=1 , l=1)[0]  
        scenefileParsed = fileParser( sceneFile )        

        self.currOpenProjectName = scenefileParsed['prj']
        self.currOpenTab = scenefileParsed['tab']
        self.currOpenSubject = scenefileParsed['subject']
        self.currOpenLevel1 = scenefileParsed['level1']
        self.currOpenLevel2 = scenefileParsed['level2']
        self.currOpenLevel3 = scenefileParsed['level3']
        ver = 'v'+ scenefileParsed['ver']
        wip = 'w'+ scenefileParsed['wip'] if scenefileParsed['wip'] != '0' else ''
           
        if self.currOpenTab == 1:
            TabName = "Asset"   
            tabName = "assets"
        elif self.currOpenTab == 2:
            TabName = "Shot"  
            tabName = "seq"
              
        mode = scenefileParsed['mode']        
        if mode == "dev":                      
            path = str(self.getFileName(self.currOpenTab, self.currOpenLevel1, self.currOpenLevel2, self.currOpenLevel3, "devFolder"))                                 
            selected = 1  
            theMode = 'devel'          
        elif mode == "pub":
            path = str(self.getFileName(self.currOpenTab , self.currOpenLevel1, self.currOpenLevel2, self.currOpenLevel3, "pubFolder"))
            selected = 0
            theMode = 'publish'        
        
        if len(self.currOpenSubject):
            fileName = "." + self.currOpenLevel2 + "_" + self.currOpenLevel3 + "_" + ver + "_" + wip + "_" + self.currOpenSubject + ".mb.thumb.jpg"
        else:
            fileName = "." + self.currOpenLevel2 + "_" + self.currOpenLevel3 + "_" + ver + "_" + wip + ".mb.thumb.jpg" 
        previewImage = path + ("/scenes/" + fileName)                
        if not QFileInfo(previewImage).isFile():
            previewImage = NO_PREVIEW_FILENAME            
#        location = self.showPath + '/' + os.path.dirname('/'.join(scenefileParsed[:-2]))
        location = os.path.join( self.showPath , self.currOpenProjectName , 
                                 tabName , self.currOpenLevel1 , 
                                 self.currOpenLevel2 , self.currOpenLevel3  )
        if self.isWinOS:
           location = self.showPath + '\\' + self.currOpenProjectName + '\\' + \
                                 tabName + '\\' + self.currOpenLevel1 + '\\' + \
                                 self.currOpenLevel2 + '\\' + self.currOpenLevel3 
            
         
        self.currOpenFileNameLabel.setText(os.path.basename(str(sceneFile)))
        self.currOpenProjectField.setText(self.currOpenProjectName)
        self.currOpenProdField.setText(TabName)
        self.currOpenFileField.setText( theMode )
        self.currOpenSubjectField.setText(self.currOpenSubject)
        self.currOpenLevel1Field.setText(self.currOpenLevel1)
        self.currOpenLevel2Field.setText(self.currOpenLevel2)
        self.currOpenLevel3Field.setText(self.currOpenLevel3)
        self.currOpenVerField.setText(ver)
        self.currOpenWipField.setText(wip)
        self.currOpenSaveDevelButton.setEnabled(selected)
        self.currOpenSavePublishButton.setEnabled(selected)        
        self.currOpenCloseButton.setEnabled(True)
        self.currOpenSnapshotButton.setEnabled(True)
        self.currOpenRecordPlayblastButton.setEnabled(selected)        
        
        self.currOpenExploreButton.setEnabled(True)
        self.currOpenPreviewImage.setPixmap(QPixmap(previewImage))
        self.currOpenLocationField.setText(location)    
        devFolder   = str(self.getFileName(self.currOpenTab, self.currOpenLevel1 , self.currOpenLevel2 , self.currOpenLevel3 , "devFolder"))
        previewFiles = [ (os.path.basename(x).split('.')[0],x )for x in glob.glob( devFolder + os.sep + 'preview/*.mov')[::-1] ] if glob.glob( devFolder + os.sep + 'preview/*.mov') else []
        if previewFiles :
            self.preview_list.clear()
            self.preview_list.addItems( [x[0] for x in previewFiles] )
        
        wipmodel = WIPmodel(sceneFile)
        self.created_lb.setText( str(wipmodel.getCreatedDate() ) )
        self.latestUpdate_lb.setText( str(wipmodel.getLatestDate() ))
        self.finaldate_lb.setText( str(wipmodel.getFinalDate() ))
        self.elasedTime_lb.setText( str(wipmodel.getElapsedTime() ))
        
    def playPreview(self):        
        playblastFile = self.previewFiles[ self.preview_list.currentRow() ][1]
        if os.path.exists(playblastFile):            
            os.system('totem %s' % playblastFile)
        else:
            QMessageBox.warning(self, 'viewerPlast', "couldn't find playblast file " + playblastFile + '.')

        
    def takeSnapshot(self):
        level1 = self.currOpenLevel1
        level2 = self.currOpenLevel2
        level3 = self.currOpenLevel3
        tab = self.currOpenTab
        subject = self.currOpenSubjectField.text()
        ver = self.currOpenVerField.text()
        wip = self.currOpenWipField.text()
        if len(subject):
            fileName = "." + self.currOpenLevel2 + "_" + self.currOpenLevel3 + "_" + ver + "_" + wip + "_" + subject + ".mb.thumb.jpg"
        else:
            fileName = "." + self.currOpenLevel2 + "_" + self.currOpenLevel3 + "_" + ver + "_" + wip + ".mb.thumb.jpg"        
        image = self.createThumbnailN(tab, level1, level2, level3, fileName)
        if QFile.exists(image):
            self.currOpenPreviewImage.setPixmap(QPixmap(image))
        return image
         
    def recordCurrentPlayblast(self):
        if not self.confirmDialog("Confirm", 'Are you sure you want to record the scene?'):
            return
        level1 = self.currOpenLevel1
        level2 = self.currOpenLevel2
        level3 = self.currOpenLevel3
        tab = self.currOpenTab
        subject = self.currOpenSubjectField.text()
        ver = self.currOpenVerField.text()
        wip = self.currOpenWipField.text()

        if len(subject):
            fileName = self.currOpenLevel2 + "_" + self.currOpenLevel3 + "_" + ver + "_" + wip + "_" + subject + ".mov"
        else:
            fileName = self.currOpenLevel2 + "_" + self.currOpenLevel3 + "_" + ver + "_" + wip + ".mov"
        
        width = self.width_sp.value()
        height = self.height_sp.value() 
        previewScale = self.previewScale_spinBox.value() 
        playblastFile, startFrame, endFrame, ratio = self.recordPlayblastForSequenceN(tab, level1, level2, level3, width , height , fileName )
        priority = self.tracPriority_spinBox.value()
               
        Tractor(self.userinfo.cn, level2, level3, playblastFile, startFrame, endFrame, width, height, ratio , priority , previewScale )

        messageBox = QMessageBox(self)
        messageBox.setText('Success')
        messageBox.setWindowModality(Qt.WindowModal)
        messageBox.setIcon(QMessageBox.Information)
        closeButton = messageBox.addButton('Close', QMessageBox.AcceptRole)
        goButton = messageBox.addButton("Go to the Tractor Dashboard", QMessageBox.AcceptRole)
        messageBox.setDefaultButton(closeButton)
        messageBox.exec_()

        if messageBox.clickedButton() == goButton:
            QDesktopServices.openUrl(QUrl(Constants.tractorHome))
        elif messageBox.clickedButton() == closeButton:
            pass

    def closeFile(self):
        if MAYA:
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
                    pass
                elif messageBox.clickedButton() == messageBox.button(QMessageBox.Cancel):
                    return True        
        self.currOpenLevel1 = ""
        self.currOpenLevel2 = ""
        self.currOpenLevel3 = ""
        self.currOpenTab = 0
        if MAYA:
            cmds.file(new=True, force=True)        
        self.updateUI(0)
        return True


    def updateUI(self, mode, offset=None):
        if mode == 1:                     
            obj = [self.assetScrollList, self.componentScrollList]
            if offset is None: return
            for i in range(offset, len(obj)): obj[i].clear()
            
        elif mode == 2:            
            obj = [self.shotScrollList, self.shotComponentScrollList]
            if offset is None: return
            for i in range(offset, len(obj)): obj[i].clear()
            
        elif mode == 0:
            self.currOpenProjectField.clear()
            self.currOpenProdField.clear()
            self.currOpenFileField.clear()
            self.currOpenVerField.clear()
            self.currOpenWipField.clear()
            self.currOpenSubjectField.clear()
            self.currOpenLevel1Field.clear()
            self.currOpenLevel2Field.clear()
            self.currOpenLevel3Field.clear()
            self.currOpenSaveDevelButton.setEnabled(False)
            self.currOpenSavePublishButton.setEnabled(False)            
            self.currOpenCloseButton.setEnabled(False)
            self.currOpenSnapshotButton.setEnabled(False)
            self.currOpenRecordPlayblastButton.setEnabled(False)
#            self.refreshOpenedButton.setEnabled( False )
#            self.currOpenViewPlayblastButton.setEnabled(False)
            self.currOpenExploreButton.setEnabled(False)
            self.currOpenPreviewImage.setPixmap(QPixmap(NO_PREVIEW_FILENAME))
            self.currOpenLocationField.clear()
            
            self.preview_list.clear()
            self.created_lb.setText( '--/--/--' )
            self.latestUpdate_lb.setText( '--/--/--' )
            self.finaldate_lb.setText( '--/--/--' )
            self.elasedTime_lb.setText( '--/--/--' )
            
            
    def takeSnapshot(self):
        if not MAYA:
            return
        level1 = self.currOpenLevel1
        level2 = self.currOpenLevel2
        level3 = self.currOpenLevel3
        tab = self.currOpenTab
        subject = self.currOpenSubjectField.text()
        ver = self.currOpenVerField.text()
        wip = self.currOpenWipField.text()
        if len(subject):
            fileName = "." + self.currOpenLevel2 + "_" + self.currOpenLevel3 + "_" + ver + "_" + wip + "_" + subject + ".mb.thumb.jpg"
        else:
            fileName = "." + self.currOpenLevel2 + "_" + self.currOpenLevel3 + "_" + ver + "_" + wip + ".mb.thumb.jpg"        
        image = self.createThumbnailN(tab, level1, level2, level3, fileName)
        if QFile.exists(image):
            self.currOpenPreviewImage.setPixmap(QPixmap(image))

        return image
            
    def removeProcess(self, tab, depth):
       currSelected = self.getCurrentlySelectedItem(tab, depth)
       if not self.confirmDialog("Confirm", 'Are you sure you want to remove directory?'):
           return
       result = self.removeItem(tab, currSelected[0], currSelected[1], currSelected[2])
       if result:           
           self.updateAssetTypeList()
           self.updateSequenceList()
        
    def confirmDialog(self, title, text):
         msg = QMessageBox.question(self, title, text, QMessageBox.Ok | QMessageBox.Cancel)
         if msg != QMessageBox.Ok:
             return False
         return True
     
  
        
    def closeEvent(self, event):
        settings = QSettings("DIGITAL idea", "iPipeline")
        settings.setValue("projectname", self.projNameCombo.currentIndex())
        settings.setValue("geometry", self.geometry())
        settings.setValue( "currentTab" , self.tabWidget.currentIndex() )
        settings.setValue("assetWindowState", self.asset_splitter.saveState())
        settings.setValue("shotWindowState", self.shot_splitter.saveState())
        if self.tabWidget.currentIndex() ==1:
            settings.setValue( "level1" , self.assetTypeScrollList.currentRow() )
            settings.setValue( "level2" , self.assetScrollList.currentRow() )
            settings.setValue( "level3" , self.componentScrollList.currentRow() )
        elif self.tabWidget.currentIndex() ==2:
            settings.setValue( "level1" , self.sequenceScrollList.currentRow() )
            settings.setValue( "level2" , self.shotScrollList.currentRow() )
            settings.setValue( "level3" , self.shotComponentScrollList.currentRow() )
        settings.setValue("red_width", self.width_sp.value())
        settings.setValue("red_height", self.height_sp.value())
        app = None   

    def loadSettings(self):
        settings = QSettings("DIGITAL idea", "iPipeline")
        if settings.contains("projectname"):
            self.projNameCombo.setCurrentIndex( settings.value("projectname").toInt()[0] )
        if settings.contains("geometry"):
            self.setGeometry( settings.value("geometry").toRect() )
        if settings.contains("currentTab"):
            self.tabWidget.setCurrentIndex( settings.value("currentTab").toInt()[0] )
        if settings.contains("bookmarks"):              
            self.bookmarks.BMlist = [str(x.toString()) for x in settings.value("bookmarks").toList() ]
            self.bookmarks.updateBMlist() 
        if settings.contains("red_width"):
            self.width_sp.setValue( settings.value("red_width").toInt()[0] )
        if settings.contains("red_height"):
            self.height_sp.setValue( settings.value("red_height").toInt()[0] )
               
        if settings.value("currentTab").toInt()[0] ==1 :
            if settings.contains("level1"):                
                self.assetTypeScrollList.setCurrentRow( settings.value("level1").toInt()[0] )
                self.updateAssetList(1)                
            if settings.contains("level2"):    
                self.assetScrollList.setCurrentRow( settings.value("level2").toInt()[0] )
                self.assetSelected(1)
            if settings.contains("level3"):
                self.componentScrollList.setCurrentRow( settings.value("level3").toInt()[0] )
                self.componentSelected()
        elif settings.value("currentTab").toInt()[0] ==2 :
            if settings.contains("level1"):                
                self.sequenceScrollList.setCurrentRow( settings.value("level1").toInt()[0] )
                self.updateShotList(True)
            if settings.contains("level2"):    
                self.shotScrollList.setCurrentRow( settings.value("level2").toInt()[0] )
                self.shotSelected(1)
            if settings.contains("level3"):
                self.shotComponentScrollList.setCurrentRow( settings.value("level3").toInt()[0] )                
                self.shotComponentSelected()
                
        self.asset_splitter.restoreState(settings.value("assetWindowState").toByteArray())
        self.shot_splitter.restoreState(settings.value("shotWindowState").toByteArray())      
        
        

def ipipeline():
    if MAYA == True :
        global app    
        try:        
            app.close()        
        except :        
            app = iPipeline()
        app.show()
    else :
        pipeline_console()
        
    

def pipeline_console():
    app = QApplication(sys.argv)
    mainWin = iPipeline()   
    mainWin.show()
    sys.exit(app.exec_())

   
    


#***********************************************************************************************
#***    Launcher.
#***********************************************************************************************
if __name__ == "__main__":  
    
      
    ipipeline()
    
    
    
    




















    
    
    
    
    
    