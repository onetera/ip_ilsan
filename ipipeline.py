# -*- coding: utf-8 -*-

"""
**ipipeline.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    iPipeline Framework Module.

**Others:**

"""

#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import sys
import os
import re
import glob
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

try:
    import maya.cmds as cmds
    import maya.mel as mel
    standAlone = False
except ImportError:
    standAlone = True
    
   

#***********************************************************************************************
#***    Internal imports.
#***********************************************************************************************
import ui.common



import Core.Note.Note2
from foundations.globals.constants import Constants
from foundations.tractor import Tractor
from Core.iPipelineActions import iPipelineActions
from Core.iPipelineInfo import iPipelineInfo
from Core.iPipelineInit import iPipelineInit
from Core.iPipelineUtility import iPipelineUtility
from Core.Note.Note import NoteContainer, Note
from Core.Workcode.Workcode import StandardTreeModel
from Gui.Functions.assistantFunctions import assistantFunctions
from components.tools.animation.animTransfer.animTransfer import AnimTransfer
from components.tools.animation.selectionTool.selectionTool import SelectionTool
from components.tools.animation.animImport.animImport import AnimImport
from components.tools.finalize.geoBake.geoBake import GeoBake # new mel script
from components.addons.information.information import Information
from components.addons.publishWindow.publishWindow import PublishWindow
from components.addons.publishWindowAni.publishWindowAni import PublishWindowAni
from components.addons.workcodeManager.workcodeManager import WorkcodeManager
from components.addons.layerManager.layerManager import layerManager

from components.tools.animation.multipleImportReference.multipleImportReference import MultipleImportReference
from py.finalize.ShowCase.ShowCase import mrgo_CacheDialog, mrgoImportTool

from xml2 import iXML
from xml_new import XmlNew


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

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************

PIPELINE_DEV = os.getenv( 'PIPELINE_DEV' )
DEV_SHOW = 0


class iPipeline(QMainWindow,
                iPipelineInit, iPipelineActions, iPipelineInfo,iPipelineUtility,
                assistantFunctions):
    """
    This class is the **iPipeline** class.
    """
#    __instance = None
#    def __new__(cls, *args, **kwargs):        
#        if not cls.__instance:    
#            cls.__instance = super(iPipeline, cls).__new__(cls, *args, **kwargs)
#        return cls.__instance
        
    def __init__(self, parent=None):
        """
        This method initializes the class.
        
        :param parent: ( QWidget )
        """        
        QMainWindow.__init__(self, parent)        
        uic.loadUi(Constants.frameworkUIFile, self)
        if self.tabWidget.currentIndex() == 0 :
            self.resize(958,650)
        else :
            self.resize(531,650)        
        
        self.sourceModule(Constants.DI_ani)
        self.sourceModule(Constants.DI_finalize)
        self.initialize()
        self.loadSettings()
#        if sys.platform == "darwin":
#            self.showPath = "/Users/higgsdecay/field/show"
        if 'win' in sys.platform:
             self.showPath = r"\\10.0.200.100"
             self.theOS = 'win'             
        elif 'linux' in sys.platform:
            self.theOS = 'linux'
            if not DEV_SHOW:
                self.showPath = "/show"
            else:
                self.showPath = "/home/idea/temp/Show"

        self.workcodeModel = StandardTreeModel(self)
        self.workcodedata = self.workcodeModel.load(QString(Constants.workcodeFile))

        self.assetTypes = []
        self.assets = []
        self.components = []
        self.sequences = []
        self.shots = []
        self.shotComponents = []

        self.createConnections()

        self.updateUI('currOpen')
        self.userNameLineEdit.setText(self.userName)        
        
        self.projNameCombo.addItems(self.getDirectoryList(self.showPath))
        try:
            self.projNameCombo.setCurrentIndex(
                self.projNameCombo.findText(self.projectName)
            )
        except:
            pass

        self.currOpenPreviewImage.setPixmap(QPixmap(NO_PREVIEW_FILENAME))
        self.assetPreviewImage.setPixmap(QPixmap(NO_PREVIEW_FILENAME))

        historyTableList = [self.currOpenHistoryTable, self.assetHistoryTable, self.shotHistoryTable]

        for historyTable in historyTableList:
            historyTable.setColumnWidth(0, 80)
            historyTable.setColumnWidth(1, 60)
            historyTable.setColumnWidth(2, 25)
            historyTable.setColumnWidth(3, 25)
            historyTable.setColumnWidth(4, 70)

        self.createActions()
        self.createToolBars()
        self.createMenus()
        
        self.setWindowTitle(Constants.applicationName)
        self.setStyleSheet("font-size: 11px")

    def assetMouseMoveEvent(self, event):
        currSelected = self.getCurrentlySelectedItem(1, 2)
        fileName = self.getFileName(1, currSelected[0], currSelected[1], "rig", "pubFolder")
        assetName = currSelected[1]
        scriptFolder = fileName+"/"+"script"
        output = "Asset:"+assetName+":"+scriptFolder
        ui.common.startDrag(output, self)

    def shotMouseMoveEvent(self, event):
        currSelected = self.getCurrentlySelectedItem(2, 2)
        fileName = self.getFileName(2, currSelected[0], currSelected[1], "rig", "pubFolder")
        assetName = currSelected[1]
        scriptFolder = fileName+"/"+"script"
        output = "Shot:"+assetName+":"+scriptFolder
        ui.common.startDrag(output, self)

    def createMenus(self):
        pass
#------------------------------------------------------------------------------ 
# For Mr.Go project.
#------------------------------------------------------------------------------ 

    def createActions(self):
        self.ani_createGroupControlAct = self.createAction("ani_createGroupControl", self.ani_createGroupControl)
        self.ani_replaceReferenceAct = self.createAction("ani_replaceReference", self.ani_replaceReference)
        self.ani_animTransferAct = self.createAction("ani_animTransfer", self.ani_animTransfer)
        self.mod_layerInfoAct = self.createAction("mod_layerInfo", self.mod_layerInfo )
#        self.finalize_geoBakeAct = self.createAction("finalize_geoBake", self.finalize_geoBake)
#        self.finalize_cacheFileLoaderAct = self.createAction("mrgo_CacheDialog", self.finalize_cacheFileLoader)
#        self.finalize_importToolAct = self.createAction("mrgo_ImportTool", self.finalize_importTool)
#      
    def createToolBars(self):
        shelfToolBar = QToolBar("Shelf")
        shelfToolBar.addAction(self.ani_createGroupControlAct)
        shelfToolBar.addAction(self.ani_replaceReferenceAct)        
#        shelfToolBar.addAction(self.finalize_geoBakeAct)
#        shelfToolBar.addAction(self.finalize_cacheFileLoaderAct)
#        shelfToolBar.addAction(self.finalize_importToolAct)
        shelfToolBar.addAction(self.ani_animTransferAct)
        shelfToolBar.addAction(self.mod_layerInfoAct)
        self.addToolBar(shelfToolBar)
#
    def mod_layerInfo(self):
        if cmds.ls( 'model_layerInfo' ) == []:
            return
        lm = cmds.ls( 'model_layerInfo' )[0]
        layerData = cmds.getAttr( lm + '.notes')
        LM= layerManager()
        LM.inLayer( eval( layerData ) )
        
    def ani_animTransfer(self):
        if self.currOpenLevel3 == "ani":
            at = AnimTransfer("alone", self)
            self.connect(at, SIGNAL("run"), self.ani_animTransfer2)
            at.show()

    def ani_animTransfer2(self, animFile, txtFile, selectedAsset):
        if standAlone : return
        mel.eval('DI_animTransfer "%s" "%s" %s' % (animFile, txtFile, selectedAsset))

    def ani_createGroupControl(self):
        if standAlone : return   
        mel.eval("DI_createGroupControl")

    def ani_replaceReference(self):
        if standAlone : return
        mel.eval("kis_replaceReference")
#
#    def finalize_geoBake(self):
#        if standAlone : return
#        startFrame = 70
#        endFrame = int(cmds.playbackOptions(q=True, maxTime=True)) + 1 # florat
#        location = cmds.workspace(q=True, fullName=True) # unicode
#
#        sceneFileName = str(self.currOpenFileNameLabel.text())
#        if len(sceneFileName) == 0:
#            geoCachePath = os.path.join(location, "data", "geoCache")
#        else:
#            geoCachePath = os.path.join(location, "data", "geoCache", os.path.splitext(sceneFileName)[0])
#
#        geoBake = GeoBake(startFrame, endFrame, geoCachePath, self)
#        geoBake.setModal(True)
#        geoBake.show()
#
#    def finalize_cacheFileLoader(self):
#        if standAlone : return
#        mrgo_CacheDialog()
#
#    def finalize_importTool(self):
#        if standAlone : return
#        mrgoImportTool()

#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 

    def createConnections(self):
        # Common
        self.connect(self.tabWidget, SIGNAL("currentChanged(int)"),
                     self.updateWorkingTab)
        self.connect(self.userNameLineEdit, SIGNAL("textChanged(const QString&)"),
                     self.setUsername)
        self.connect(self.projNameCombo, SIGNAL("currentIndexChanged(const QString&)"),
                     self.projectSelected)
        self.connect( self.resizeButton , SIGNAL("clicked()") ,
                      self.resizing )
        

        # Currently Open
        self.connect(self.currOpenSaveDevelButton, SIGNAL("clicked()"),
                     self.saveDevelSelected)
        self.connect(self.currOpenSavePublishButton, SIGNAL("clicked()"),
                     self.savePublishSelected)
        #self.connect(self.currOpenRollbackButton, SIGNAL("clicked()"),
        #             self.rollbackUI)
        self.connect(self.currOpenCloseButton, SIGNAL("clicked()"),
                     self.closeFile)
        self.connect(self.currOpenSnapshotButton, SIGNAL("clicked()"),
                     self.takeSnapshot)
        self.connect(self.currOpenRecordPlayblastButton, SIGNAL("clicked()"),
                     self.recordCurrentPlayblast)
        self.connect(self.currOpenViewPlayblastButton, SIGNAL("clicked()"),
                     lambda: self.viewPlayblastSelected(self.currOpenTab))
        self.connect(self.currOpenClearCommentButton, SIGNAL("clicked()"),
                     self.clearComment)
        self.connect(self.currOpenSaveCommentButton, SIGNAL("clicked()"),
                     self.saveComment)

        self.connect(self.currOpenClearSelectedCommentButton, SIGNAL("clicked()"),
                     self.selectedClearComment)
        self.connect(self.currOpenSaveSelectedCommentButton, SIGNAL("clicked()"),
                     self.selectedSaveComment)

        self.connect(self.currOpenExploreButton, SIGNAL("clicked()"),
                     self.exploreCurrent)
        self.connect(self.currOpenHistoryTable, SIGNAL("itemClicked(QTableWidgetItem*)"),
                     self.updateCurrentlyComment)
        self.connect( self.refreshOpenedButton , SIGNAL("clicked()") ,
                      self.refreshCurrentlyOpen )
        
#        self.connect( self.tracPriority_spinBox , SIGNAL("valueChanged()") ,
#                      self.printTrcPriority )

        # Asset Browser
        self.connect(self.assetTypeScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.updateAssetList)
        self.connect(self.assetScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.assetSelected)
        self.connect(self.componentScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.componentSelected)
        self.connect(self.componentScrollList, SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
                     lambda: self.componentDoubleClicked(1, "devel"))
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
        self.connect(self.assetViewPlayblastButton, SIGNAL("clicked()"),
                     lambda: self.viewPlayblastSelected(1))
        self.connect(self.exploreAssetButton, SIGNAL("clicked()"),
                     lambda: self.exploreSelectd(1))
        self.connect(self.assetHistoryTable, SIGNAL("itemClicked(QTableWidgetItem*)"),
                     self.updateAssetComment)
        self.connect(self.assetDevelList, SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
                     lambda value: self.componentDoubleClicked(1, "devel", value))
        self.connect(self.assetPublishList, SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
                     lambda value: self.componentDoubleClicked(1, "publish", value))

        # Shot Browser
        self.connect(self.sequenceScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.updateShotList)
        self.connect(self.shotScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.shotSelected)
        self.connect(self.shotComponentScrollList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     self.shotComponentSelected)
        self.connect(self.shotComponentScrollList, SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
                     lambda: self.componentDoubleClicked(2, "devel"))
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
        self.connect(self.showViewPlayblastButton, SIGNAL("clicked()"),
                     lambda: self.viewPlayblastSelected(2))
        self.connect(self.exploreShotButton, SIGNAL("clicked()"),
                     lambda: self.exploreSelectd(2))
        self.connect(self.shotHistoryTable, SIGNAL("itemClicked(QTableWidgetItem*)"),
                     self.updateShotComment)
        self.connect(self.shotDevelList, SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
                     lambda value: self.componentDoubleClicked(2, "devel", value))
        self.connect(self.shotPublishList, SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
                     lambda value: self.componentDoubleClicked(2, "publish", value))
        self.connect(self.assetDevelList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     lambda value: self.sceneFileSelected(value, 1, "devel"))
        self.connect(self.assetPublishList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     lambda value: self.sceneFileSelected(value, 1, "publish"))
        self.connect(self.shotDevelList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     lambda value: self.sceneFileSelected(value, 2, "devel"))
        self.connect(self.shotPublishList, SIGNAL("itemClicked(QListWidgetItem*)"),
                     lambda value: self.sceneFileSelected(value, 2, "publish"))

        # context menu
        self.connect(self.assetDevelList, SIGNAL("customContextMenuRequested(const QPoint&)"),
                     lambda value: self.componentMenu(value, 1, "devel"))
        self.connect(self.assetPublishList, SIGNAL("customContextMenuRequested(const QPoint&)"),
                     lambda value: self.componentMenu(value, 1, "publish"))
        self.connect(self.shotDevelList, SIGNAL("customContextMenuRequested(const QPoint&)"),
                     lambda value: self.componentMenu(value, 2, "devel"))
        self.connect(self.shotPublishList, SIGNAL("customContextMenuRequested(const QPoint&)"),
                     lambda value: self.componentMenu(value, 2, "publish"))
        self.connect(self.assetScrollList, SIGNAL("customContextMenuRequested(const QPoint&)"),
                     lambda value: self.assetShotListMenu("asset", value))
        self.connect(self.shotScrollList, SIGNAL("customContextMenuRequested(const QPoint&)"),
                     lambda value: self.assetShotListMenu("shot", value))

#        
#    def printTrcPriority(self):
#        print self.tracPriority_spinBox.value() 

    def clearComment(self):
        self.currOpenCommentField.clear()

    def saveComment(self):
        level1 = self.currOpenLevel1Field.text()
        level2 = self.currOpenLevel2Field.text()
        level3 = self.currOpenLevel3Field.text()
        tab = self.currOpenTab

        sceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1))
        if len(self.currOpenSubjectField.text()) == 0:
            filename = level2 + "_" + level3 + "_" + self.currOpenVerField.text() + "_" + self.currOpenWipField.text() + ".mb"
        else:
            filename = level2 + "_" + level3 + "_" + self.currOpenVerField.text() + "_" + self.currOpenWipField.text() + "_" + self.currOpenSubjectField.text() + ".mb" 

        filename = str(filename)
        _xmlfile = os.path.join(sceneFolder, '.%s.xml' % filename)
        if os.path.exists(_xmlfile):
            xmlfile = QFile( QString(_xmlfile))
            xml = iXML()
            xml.read(xmlfile)
    
            comment = self.currOpenCommentField.toPlainText()
            xml.updateDomElement("comment", comment)
    
            outFile = QFile(QString(_xmlfile))
            outFile.open(QFile.WriteOnly | QFile.Text)
    
            xml.write_test(outFile)
            QMessageBox.information(self, "Info", "Success")

    def selectedClearComment(self):
        self.currOpenCommentHistoryField.clear()

    def selectedSaveComment(self):
        if self.selected_comment_item is None:
            return

        comment = self.currOpenCommentHistoryField.toPlainText()
        self.selected_comment_item.updateDomElement("comment", comment)

        outFile = QFile(QString(self.selected_comment_xml))
        outFile.open(QFile.WriteOnly | QFile.Text)
        self.selected_comment_item.write_test(outFile)

        localFile = "." + os.path.basename(cmds.file(q=True, sn=True)) + ".xml"
        if localFile == os.path.basename(self.selected_comment_xml):
            self.currOpenCommentField.setPlainText(comment)
        QMessageBox.information(self, "Info", "Success")

    def openSaveAs(self):
        theFile = cmds.fileDialog2(dialogStyle=2)[0]
        cmds.file(rename = theFile )
        cmds.file( save = 1  )
        
    def sceneFileSelected(self, item, tab, mode):
        currSelected = self.getCurrentlySelectedItem(tab, 3)
        level1 = currSelected[0]
        level2 = currSelected[1]
        level3 = currSelected[2]

        if tab == 1: # asset
            previewObject = self.assetPreviewImage
            commentObject = self.assetCommentField
        elif tab == 2: # shot
            previewObject = self.shotPreviewImage
            commentObject = self.shotCommentField
        if mode == "devel":
            fileName = self.getFileName(tab, level1, level2, level3, "devFolder")
        elif mode == "publish":
            fileName = self.getFileName(tab, level1, level2, level3, "pubFolder")

        image = fileName+"/scenes/."+item.text()+".thumb.jpg"
        xmlFile = fileName+"/scenes/."+item.text()+".xml"

        if QFileInfo(image).isFile():
            previewObject.setPixmap(QPixmap(image))
        else:
            previewObject.setPixmap(QPixmap(NO_PREVIEW_FILENAME))

        if QFileInfo(xmlFile).isFile():
            n = Core.Note.Note2.NoteContainer()
            n.importSAX(str(xmlFile))
            comment = n.getNotes()[0].comment
            commentObject.setPlainText(comment)
        else:
            commentObject.clear()

        self.currOpenFile = fileName+"/scenes/."+item.text()

    def setUsername(self, name):
        self.userName = name

    def updateCurrentlyComment(self, item):
        self.selected_comment_item = None
        self.selected_comment_xml = None
        self.currOpenClearSelectedCommentButton.setEnabled(False)
        self.currOpenSaveSelectedCommentButton.setEnabled(False)
        index = item.row()
        current_item = self.currOpenHistories[index]

        level1 = self.currOpenLevel1Field.text()
        level2 = self.currOpenLevel2Field.text()
        level3 = self.currOpenLevel3Field.text()
        tab = self.currOpenTab

        if current_item.event == "devel":
            fileName = self.getFileName(tab, level1, level2, level3, "devFolder")
        #elif current_item.event == "publish":
        #    fileName = self.getFileName(tab, level1, level2, level3, "pubFolder")
        else:
            self.currOpenCommentHistoryField.setPlainText("")
            return

        sceneFolder = os.path.join(str(fileName), 'scenes')
        subject = str(current_item.subject).strip()
        if len(subject) == 0:
            if current_item.event == "devel":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + "_w" + str(current_item.wipversion).zfill(2) + ".mb"
            elif current_item.event == "publish":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + ".mb"
        else:
            if current_item.event == "devel":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + "_w" + str(current_item.wipversion).zfill(2) + "_" + subject + ".mb"
            elif current_item.event == "publish":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + "_" + subject + ".mb"

        filename = str(filename)
        self.selected_comment_xml = os.path.join(sceneFolder, '.%s.xml' % filename)
        if os.path.exists(self.selected_comment_xml):
            xmlfile = QFile( QString(self.selected_comment_xml))
            self.selected_comment_item = iXML()
            self.selected_comment_item.read(xmlfile)
            self.currOpenCommentHistoryField.setPlainText(self.selected_comment_item.findElement("comment"))
            self.currOpenClearSelectedCommentButton.setEnabled(True)
            self.currOpenSaveSelectedCommentButton.setEnabled(True)

    def updateAssetComment(self, item):
        index = item.row()
        current_item = self.assetHistories[index]

        tab = self.tabWidget.currentIndex()
        currSelected = self.getCurrentlySelectedItem(tab, 3)
        level1 = currSelected[0]
        level2 = currSelected[1]
        level3 = currSelected[2]

        if current_item.event == "devel":
            fileName = self.getFileName(tab, level1, level2, level3, "devFolder")
        elif current_item.event == "publish":
            fileName = self.getFileName(tab, level1, level2, level3, "pubFolder")
        else:
            self.assetCommentField.setPlainText("")
            return

        sceneFolder = os.path.join(str(fileName), 'scenes')
        subject = str(current_item.subject).strip()
        if len(subject) == 0:
            if current_item.event == "devel":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + "_w" + str(current_item.wipversion).zfill(2) + ".mb"
            elif current_item.event == "publish":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + ".mb"
        else:
            if current_item.event == "devel":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + "_w" + str(current_item.wipversion).zfill(2) + "_" + subject + ".mb"
            elif current_item.event == "publish":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + "_" + subject + ".mb"

        filename = str(filename)
        _xmlfile = os.path.join(sceneFolder, '.%s.xml' % filename)
        if os.path.exists(_xmlfile):
            xmlfile = QFile( QString(_xmlfile))
            xml = iXML()
            xml.read(xmlfile)
            self.assetCommentField.setPlainText(xml.findElement("comment"))

    def updateShotComment(self, item):
        index = item.row()
        current_item = self.shotHistories[index]

        tab = self.tabWidget.currentIndex()
        currSelected = self.getCurrentlySelectedItem(tab, 3)
        level1 = currSelected[0]
        level2 = currSelected[1]
        level3 = currSelected[2]

        if current_item.event == "devel":
            fileName = self.getFileName(tab, level1, level2, level3, "devFolder")
        elif current_item.event == "publish":
            fileName = self.getFileName(tab, level1, level2, level3, "pubFolder")
        else:
            self.shotCommentField.setPlainText("")
            return

        sceneFolder = os.path.join(str(fileName), 'scenes')
        subject = str(current_item.subject).strip()
        if len(subject) == 0:
            if current_item.event == "devel":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + "_w" + str(current_item.wipversion).zfill(2) + ".mb"
            elif current_item.event == "publish":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + ".mb"
        else:
            if current_item.event == "devel":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + "_w" + str(current_item.wipversion).zfill(2) + "_" + subject + ".mb"
            elif current_item.event == "publish":
                filename = level2 + "_" + level3 + "_v" + str(current_item.version).zfill(2) + "_" + subject + ".mb"

        filename = str(filename)
        _xmlfile = os.path.join(sceneFolder, '.%s.xml' % filename)
        if os.path.exists(_xmlfile):
            xmlfile = QFile( QString(_xmlfile))
            xml = iXML()
            xml.read(xmlfile)
            self.shotCommentField.setPlainText(xml.findElement("comment"))

    def assetShotListMenu(self, mode, pos):
        if mode == "asset":
            currItem = self.assetScrollList
            tab = 1
        elif mode == "shot":
            currItem = self.shotScrollList
            tab = 2
        selectionUIAct = self.createAction("selection tool", lambda: self.selectionUI(tab))
        animImportAct = self.createAction("anim import", lambda: self.animImportUI(tab))
        menu = QMenu()
        menu.addAction(selectionUIAct)
        if mode == "shot":
            menu.addAction(animImportAct)
        menu.exec_(currItem.mapToGlobal(pos))

    def animImportUI(self, tab):
        currSelected = self.getCurrentlySelectedItem(tab, 2)
        level1 = currSelected[0]
        level2 = currSelected[1]
        if tab == 1: #asset
            level3 = "rig"
        elif tab == 2: #shot
            level3 = "ani"

        devFolder = str(self.getFileName(tab, level1, level2, level3, "devFolder"))
        pubFolder = str(self.getFileName(tab, level1, level2, level3, "pubFolder"))

        ai = AnimImport(tab, devFolder, pubFolder)
        ai.show()

    def selectionUI(self, tab):
        currSelected = self.getCurrentlySelectedItem(tab, 2)
        level1 = currSelected[0]
        level2 = currSelected[1]
        if tab == 1: #asset
            level3 = "rig"
        elif tab == 2: #shot
            level3 = "ani"

        devFolder = str(self.getFileName(tab, level1, level2, level3, "devFolder"))
        pubFolder = str(self.getFileName(tab, level1, level2, level3, "pubFolder"))

        st = SelectionTool(tab, devFolder, pubFolder, self)
        st.show()

    def componentMenu(self, pos, tab, mode):
        refAssetAct = self.createAction("reference (assetName:)", lambda: self.importReference(tab, "reference (assetName:)", mode, 0))
        importAssetAct = self.createAction("import (assetName:)", lambda: self.importReference(tab, "import (assetName:)", mode, 0))
        multipleImportAct = self.createAction("multiple import (assetname:)", lambda: self.multipleSelected(tab, mode, 1))
        multipleRefAct = self.createAction("multiple reference (assetname:)", lambda: self.multipleSelected(tab, mode, 0))
        importAct = self.createAction("import", lambda: self.importReference(tab, "import", mode, 0))
        menu = QMenu()
        menu.addAction(refAssetAct)
        menu.addAction(multipleRefAct)
        menu.addSeparator()
        menu.addAction(importAct)
        menu.addAction(importAssetAct)
        menu.addAction(multipleImportAct)
        menu.exec_(self.assetDevelList.mapToGlobal(pos))

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
                item = self.assetDevelList.currentItem()
            elif tab == 2:
                item = self.shotDevelList.currentItem()
            path = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "devFolder")
        elif mode == "publish":
            if tab == 1:
                item = self.assetPublishList.currentItem()
            elif tab == 2:
                item = self.shotPublishList.currentItem()
            path = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "pubFolder")
        if item is None:
            return
        itemName = item.text()
        assetName = str(currSelected[1])
        fileName = path+"/scenes/"+itemName

        if sel:
            name = "multiple import (assetname:)"
            command = "Import"
        else:
            name = "multiple reference (assetname:)"
            command = "Reference"

        if not self.confirmDialog("Confirm", 'Are you sure you want to run "%s"?' % name):
            return
        if not standAlone :
            mel.eval('DI_multiple%s %s "%s" "%s"' % (command, numItems, assetName, fileName))

        self.multipleImportUI.close()

    def importReference(self, tab, ex, mode, type):
        if not self.confirmDialog("Confirm", 'Are you sure you want to run "%s"?' % ex):
            return
        currSelected = self.getCurrentlySelectedItem(tab, 3)
        if mode == "devel":
            if tab == 1:
                item = self.assetDevelList.currentItem()
            elif tab == 2:
                item = self.shotDevelList.currentItem()
            path = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "devFolder")
        elif mode == "publish":
            if tab == 1:
                item = self.assetPublishList.currentItem()
            elif tab == 2:
                item = self.shotPublishList.currentItem()
            path = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "pubFolder")
        if item is None:
            return
        itemName = item.text()
        assetName = currSelected[1]
        fileName = path+"/scenes/"+itemName
        if type: # filename
            namespace = os.path.splitext(str(itemName))[0]
        else: # assetName
            namespace = str(assetName)
            
        if ex == "reference (assetName:)":
            if not standAlone :
                mel.eval("file -r -gl -namespace \"%s\" -lrd \"all\" -options \"v=0\" \"%s\"" % (namespace, fileName))
                
                
        elif ex == "import (assetName:)":
            if not standAlone :
                mel.eval("file -import -namespace \"%s\" -ra true -options \"v=0\"  -pr -loadReferenceDepth \"all\" \"%s\"" % (namespace, fileName))
        elif ex == "import":
            if not standAlone :
                mel.eval("file -import -type \"mayaBinary\" -rdn -rpr \"clash\" -options \"v=0;p=17\"  -pr -loadReferenceDepth \"all\" \"%s\"" % (fileName))
             
#        if os.path.isfile( fileName[:-3] + '.layml' ):    
#            lm = layerManager()                  
#            lm.constructLayer( fileName[:-3] + '.layml' )

    def updateWorkingTab(self, tab):
        if tab == 0:
            self.resize(958,650)
            self.resizeButton.setText( '<<<')
        elif tab == 1:            
            self.resize(531,650)
            self.resizeButton.setText( '>>>')
            self.updateAssetTypeList()
        elif tab == 2:
            self.resize(531,650)
            self.resizeButton.setText( '>>>')
            self.updateSequenceList()
    
    def resizing(self): 
        if self.size().width() < 710: 
            if self.tabWidget.currentIndex() == 0:
                self.resize(958,650)
                self.resizeButton.setText( '<<<')
            else :
                self.resize(958,650)
                self.resizeButton.setText( '<<<')
            
        else :
            if self.tabWidget.currentIndex() == 0:                
                self.resize(706,650)
                self.resizeButton.setText( '>>>')
            else :
                self.resizeButton.setText( '>>>') 
                self.resize(531,650)
        
    def resizeWin(self , x , y ):
        self.resize( x , y )
        
    def projectSelected(self, item):
        self.activateProject(item)

        # Currently Open 초기화
        #self.updateCurrentlyOpen()
        # AssetType 초기화
        self.updateAssetTypeList()
        # Sequence 초기화
        self.updateSequenceList()

        if self.projNameCombo.currentText() == "mrgo":
            self.assetScrollList.setDragEnabled(True)
            self.shotScrollList.setDragEnabled(True)
            self.assetScrollList.mouseMoveEvent = self.assetMouseMoveEvent
            self.shotScrollList.mouseMoveEvent = self.shotMouseMoveEvent

        else:
            self.assetScrollList.setDragEnabled(False)
            self.shotScrollList.setDragEnabled(False)
            self.assetScrollList.mouseMoveEvent = None
            self.shotScrollList.mouseMoveEvent = None

    #===========================================================================
    # "Asset Browser" Tab
    #===========================================================================
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
                # 아이템 선택
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
                    # 아이템 선택
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
        # 버튼 및 메뉴 활성화 유무
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
                    # 아이템 선택
                    self.componentScrollList.setCurrentRow(row)

        #textScrollList -e -en $active "op_shotComponentScrollList";
        self.componentSelected()

    def componentSelected(self):
        currSelected = self.getCurrentlySelectedItem(1, 3)
        selected = 1
        if currSelected[2] == "":
            selected = 0
        if self.isSuperUser:
            self.componentRemoveButton.setEnabled(selected)
        # 컨텍스트 메뉴 활성화 유무
        if selected:
            # openPipelineUpdateShotComponentMenus($currSelected[0], $currSelected[1], $currSelected[2]);
            pass
        self.assetInformation()
        self.loadAssetHistory()
        self.loadAssetBrowse()

    #===========================================================================
    # assetInformation
    #===========================================================================
    def assetInformation(self):
        tab = 1
        selected = 1
        currSelected = self.getCurrentlySelectedItem(1, 3)
        level1 = currSelected[0]
        level2 = currSelected[1]
        level3 = currSelected[2]
        if level3 == "":
            selected = 0
            previewImage = NO_PREVIEW_FILENAME
        else:
            previewImage = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "previewFile")
            if not QFileInfo(previewImage).isFile():
                previewImage = NO_PREVIEW_FILENAME
        folder = self.getFileName(tab, level1, level2, level3, "folder")
        self.assetLocationField.setText(folder)
        self.assetCommentField.clear()
        self.assetPreviewImage.setPixmap(QPixmap(previewImage))
        #self.assetViewPlayblastButton.setEnabled(selected)

    #===========================================================================
    # "Shot Browser" Tab
    #===========================================================================
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
                # 아이템 선택
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
                    # 아이템 선택
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
        # 버튼 및 메뉴 활성화 유무
        if self.isSuperUser:
            self.shotRemoveButton.setEnabled(selected)
        self.shotComponentNewButton.setEnabled(selected)
        if selected:
            compList = self.getChildren(2, currSelected[0], currSelected[1], "")
            compList.sort()
            # updateShotMenus(currSelected[0], currSelected[1])
            for row, component in enumerate(compList):
                active = 1
                self.shotComponents.append(component)
                self.shotComponentScrollList.addItem(component)
                if ((currSelected[2] == component) and (preserveSelection == 1)):
                    # 아이템 선택
                    self.shotComponentScrollList.setCurrentRow(row)

        #textScrollList -e -en $active "op_shotComponentScrollList";
        self.shotComponentSelected()

    def shotComponentSelected(self):
        currSelected = self.getCurrentlySelectedItem(2, 3)
        selected = 1
        if currSelected[2] == "":
            selected = 0
        if self.isSuperUser:
            self.shotComponentRemoveButton.setEnabled(selected)
        # 컨텍스트 메뉴 활성화 유무
        if selected:
            # openPipelineUpdateShotComponentMenus($currSelected[0], $currSelected[1], $currSelected[2]);
            pass
        self.shotInformation()
        self.loadShotHistory()
        self.loadShotBrowse()

    def shotInformation(self):
        tab = 2
        selected = 1
        currSelected = self.getCurrentlySelectedItem(2, 3)
        level1 = currSelected[0]
        level2 = currSelected[1]
        level3 = currSelected[2]
        if level3 == "":
            selected = 0
            previewImage = NO_PREVIEW_FILENAME
        else:
            previewImage = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "previewFile")
            if not QFileInfo(previewImage).isFile():
                previewImage = NO_PREVIEW_FILENAME
        folder = self.getFileName(tab, level1, level2, level3, "folder")
        self.shotLocationField.setText(folder)
        self.shotCommentField.clear()
        self.shotPreviewImage.setPixmap(QPixmap(previewImage))
        #self.showViewPlayblastButton.setEnabled(selected)

    def exploreCurrent(self):
        level1 = self.currOpenLevel1
        level2 = self.currOpenLevel2
        level3 = self.currOpenLevel3
        tab = self.currOpenTab
        self.openLocation(tab, level1, level2, level3, 0, 1)

    def exploreSelectd(self, tab):
        selectedItem = self.getCurrentlySelectedItem(tab, 3)
        self.openLocation(tab, selectedItem[0], selectedItem[1], selectedItem[2])

    def takeSnapshot(self):
        level1 = self.currOpenLevel1
        level2 = self.currOpenLevel2
        level3 = self.currOpenLevel3
        tab = self.currOpenTab
        subject = self.currOpenSubjectField.text()
        ver = self.currOpenVerField.text()
        wip = self.currOpenWipField.text()
        if len(subject):
            fileName = "."+self.currOpenLevel2+"_"+self.currOpenLevel3+"_"+ver+"_"+wip+"_"+subject+".mb.thumb.jpg"
        else:
            fileName = "."+self.currOpenLevel2+"_"+self.currOpenLevel3+"_"+ver+"_"+wip+".mb.thumb.jpg"        
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
            fileName = self.currOpenLevel2+"_"+self.currOpenLevel3+"_"+ver+"_"+wip+"_"+subject+".mov"
        else:
            fileName = self.currOpenLevel2+"_"+self.currOpenLevel3+"_"+ver+"_"+wip+".mov"

        previewScale = self.previewScale_spinBox.value() 
        playblastFile, startFrame, endFrame, width, height, ratio = self.recordPlayblastForSequenceN(tab, level1, level2, level3, fileName , previewScale)
        priority = self.tracPriority_spinBox.value()        
        Tractor(self.userName, level2, level3, playblastFile, startFrame, endFrame, width, height, ratio , priority )

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

    def viewPlayblastSelected(self, tab):
        selectedItem = self.getCurrentlySelectedItem(tab, 3)
        self.viewPlayblast(tab, selectedItem[0], selectedItem[1], selectedItem[2])

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
        w = WorkcodeManager(tab, level1, level2, level3, self.workcodedata, self.userName, self)
        w.show()

    def saveDevelSelected(self):
        level1 = self.currOpenLevel1Field.text()
        level2 = self.currOpenLevel2Field.text()
        level3 = self.currOpenLevel3Field.text()
        tab = self.currOpenTab

        subjectName = str(self.currOpenSubjectField.text())
        sceneFileName = str(self.currOpenFileNameLabel.text())

        sceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1))
        sceneFiles = glob.glob(sceneFolder+"*.mb")
        
        ver_wip = VER_WIP_RE.findall( sceneFileName )[0] # return v01_w02
        currVer = int(ver_wip[1:3])
        currWip = int(ver_wip[-2:])

        if QFileInfo(os.path.join(sceneFolder, sceneFileName)).isFile():
            while True:
                currWip += 1
                curLatestVersion = os.path.join(sceneFolder, sceneFileName.replace(ver_wip, ver_wip[:-2]+str(currWip).zfill(2)))
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
                subjectLists[basename].append( i )

            for subject in subjectLists.keys():
                subjectLists[subject] = sorted(subjectLists[subject])

            if len(subjectLists):
                #try:
                subjects = subjectLists[subjectName]
                subjects = sorted(subjects, reverse=True)
                destinationFile = subjects[0]
                ver = VER_WIP_RE.findall( os.path.basename(str(destinationFile)))[0]
                nVer = ver[:-2]+str(int(ver[-2:])+1).zfill(2)
                destinationFile = destinationFile.replace(ver, nVer)
                #except KeyError:
                #    destinationFile = os.path.join(sceneFolder, "%s_%s_v01_w01_%s.mb" % (level2, level3, str(self.currOpenSubjectField.text())))
            else:
                # 초기화 버전
                destinationFile = os.path.join(sceneFolder, "%s_%s_v01_w01_%s.mb" % (level2, level3, str(self.currOpenSubjectField.text())))

        # 서브젝트가 존재하지 않을 때
        else:
            defaultFiles = filter(SCENEFILE_RE.search, sceneFiles)
            if len(defaultFiles):
                destinationFile = defaultFiles[-1]
                ver = VER_WIP_RE.findall( os.path.basename(str(destinationFile)))[0]
                nVer = ver[:-2]+str(int(ver[-2:])+1).zfill(2)
                destinationFile = destinationFile.replace(ver, nVer)
            else:
                # 초기화 버전
                destinationFile = os.path.join(sceneFolder, "%s_%s_v01_w01.mb" % (level2, level3))

        info = Information("Save Devel", level2, level3, currVer, currWip, subjectName, curLatestVersion, destinationFile, self)
        self.connect(info, SIGNAL("save"),
                     self.saveDevel)
        info.show()

    def saveDevel(self, destinationFile, comment, status, progress, ctime, application, subjectName):
        ext = 'mb'
        level1 = self.currOpenLevel1Field.text()
        level2 = self.currOpenLevel2Field.text()
        level3 = self.currOpenLevel3Field.text()
        tab = self.currOpenTab

        sceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1))

        fileName = os.path.basename(str(destinationFile))
        ver = int(VER_RE.findall( fileName )[0][2:])
        wip = int(WIP_RE.findall( fileName )[0][2:])

        # model layer information
        if str( level3 ) == 'model' and cmds.ls( 'model_layerInfo' ) == [] :
            print' creating model layer information'
            lm = layerManager()
            lm.createLMnode()
        else:
            print 'failed create lm node...........'

        try:
            cmds.file(rename=str(destinationFile))
            if ext == 'ma':
                type = 'mayaAscii'
            elif ext == 'mb':
                type = 'mayaBinary'
            else:
                type = 'mayaBinary'
                QMessageBox.warning(self, "warning", "openPipelineSaveWorkshop: Invalid file format ("+ext+") specified: saving to Maya Binary")
            # 씬파일 저장
            
            cmds.file(save=True, type=type)

        except:
            if 'win' in sys.platform:
                os.system('type NUL>%s' % os.path.join(sceneFolder, str(destinationFile)))                
            else:
                os.system('touch %s' % os.path.join(sceneFolder, str(destinationFile)))                

#        if str( level3 ) == 'model':
#            lm = layerManager()
#            lm.writeXML( os.path.join(sceneFolder, str( level2 ) + '_' + str( level3 ) + '.layml' ) )
                         
        # xml 생성
        historyFile = str(self.getFileName(tab, level1, level2, level3, "historyFile", 0, 1))
        nc = NoteContainer()
        if QFileInfo(historyFile).isFile():
            nc.importSAX(historyFile)
        else:
            open(historyFile, 'w')
        nc.addN(Note(self.userName,  # author
                    self.getDate(), # date
                    self.getTime(), # time
                    "devel",        # event
                    ver,            # version
                    wip,            # wipversion
                    subjectName,    # subject
                    unicode(comment),    # comment
                    fileName,
                    sceneFolder[:-1],
                    status,
                    progress,
                    ctime,
                    "",
                    application
                    ))
        nc.exportXML(historyFile)
        nc.ibXML(os.path.join(str(sceneFolder),   ".%s.xml" % fileName)   )

        self.loadCurrentHistory()

        self.currOpenVerField.setText("v"+str(ver).zfill(2))
        self.currOpenWipField.setText("w"+str(wip).zfill(2))
        self.currOpenCommentField.setText(comment)
        #self.currOpenFileNameLabel.setText(os.path.join(str(sceneFolder), str(destinationFile)))
        self.currOpenFileNameLabel.setText(destinationFile)
        self.currOpenSubjectField.setText(subjectName)

        #self.takeSnapshot()

    def savePublishSelected(self):
        level1 = self.currOpenLevel1
        level2 = self.currOpenLevel2
        level3 = self.currOpenLevel3
        tab = self.currOpenTab

        subjectName = str(self.currOpenSubjectField.text())
        sceneFileName = str(self.currOpenFileNameLabel.text())
        
        pubFolder = str(self.getFileName(tab, level1, level2, level3, "pubFolder", 0, 1))
        pubScenesFolder = os.path.join(pubFolder, "scenes")
        devSceneFolder = str(self.getFileName(tab, level1, level2, level3, "sceneFolder", 0, 1))

        o_filename = os.path.join(devSceneFolder, sceneFileName)

        # new
        mayaFiles = glob.glob(devSceneFolder+"*.mb")
        develVer = 1
        develWip = 1

        ver_wip = VER_WIP_RE.findall( sceneFileName )[0] # return v01_w02
        currVer = int(ver_wip[1:3])
        currWip = int(ver_wip[-2:])

        if QFileInfo(os.path.join(devSceneFolder, sceneFileName)).isFile():
            while True:
                currWip += 1
                develFile = os.path.join(devSceneFolder, sceneFileName.replace(ver_wip, ver_wip[:-2]+str(currWip).zfill(2)))
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
                subjectLists[basename].append( i )

            for subject in subjectLists.keys():
                subjectLists[subject] = sorted(subjectLists[subject])

            if len(subjectLists):
                #try:
                subjects = subjectLists[subjectName]
                #except KeyError:
                #    print '[debug] no file'
                #    return
                subjects = sorted(subjects, reverse=True)
                develFile2Latest = subjects[0]
                ver = VER_WIP_RE.findall( os.path.basename(str(develFile2Latest)))[0]
                nVer = ver[:-2]+str(int(ver[-2:])+1).zfill(2)
                develFile2 = develFile2Latest.replace(ver, nVer)
                if develFile == develFile2:
                    nVer = "v%s_w01" % (str(int(ver[1:3])+1).zfill(2))
                    develFile2 = develFile2Latest.replace(ver, nVer)
                #develVer = int(ver[1:3])+1
                publishFile = os.path.join(pubScenesFolder, "%s_%s_v%s_%s.mb" % ( level2, level3, str(currVer).zfill(2), str(self.currOpenSubjectField.text())))
            else:
                print '[debug] no file'
                return

        # 서브젝트가 존재하지 않을 때
        else:
            defaultFiles = filter(SCENEFILE_RE.search, mayaFiles)
            # 씬파일들이 존재할 때
            if len(defaultFiles):
                # 마지막 버전 선택
                develFile2Latest = defaultFiles[-1]
                # 선택된 파일을 버전 파싱
                ver = VER_WIP_RE.findall( os.path.basename(str(develFile2Latest)))[0]
                # 버전 카운트
                nVer = ver[:-2]+str(int(ver[-2:])+1).zfill(2)
                develFile2 = develFile2Latest.replace(ver, nVer)
                if develFile == develFile2:
                    nVer = "v%s_w01" % (str(int(ver[1:3])+1).zfill(2))
                    develFile2 = develFile2Latest.replace(ver, nVer)
                #develVer = int(ver[1:3])+1
                publishFile = os.path.join(pubScenesFolder, "%s_%s_v%s.mb" % ( level2, level3, str(currVer).zfill(2)))
            else:
                #develFile2 = os.path.join(devSceneFolder, "%s_%s_v01.mb" % (level2, level3))
                print '[debug] no file'
                return

        if self.currOpenLevel3 == "ani" and self.projNameCombo.currentText() == "mrgo":
            p = PublishWindowAni(level2, level3, subjectName, develFile, develFile2, publishFile, o_filename, self)
            p.show()
        else:
            info = PublishWindow(level2, level3, subjectName, develFile, develFile2, publishFile, o_filename, self)
            self.connect(info, SIGNAL("save"),
                         self.savePublish)
            info.show()

    #def savePublish(self, comment, status, progress, ctime, application, selectedAsset=[]):
    def savePublish(self, enableSave, closeSceneFile, develFile, publishFile, comment, status, progress, ctime, application, selectedAsset=[]):
        warning = False
        ext = 'mb'
        level1 = self.currOpenLevel1Field.text()
        level2 = self.currOpenLevel2Field.text()
        level3 = self.currOpenLevel3Field.text()
        tab = self.currOpenTab

        # 프리프로세싱
        if level3 == "finalize" and self.projNameCombo.currentText() == "mrgo":
            if cmds.namespace( exists='mrgo' ):
                refFileName = cmds.referenceQuery("mrgo:mrgo_worldz_CON", filename=True, shortName=True)
                if refFileName != "mrgo_facial_v05.mb" and refFileName != "mrgo_facial_v06.mb":
                    QMessageBox.warning(self, QString.fromLocal8Bit("Warning"),
                        QString.fromLocal8Bit("Please replace rig to facial version"))
                    return
            else:
                QMessageBox.warning(self, QString.fromLocal8Bit("Warning"),
                    QString.fromLocal8Bit("There is no namespace named \"mrgo\""))
                return

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

        verString = VER_RE.findall( basename )[0]
        publishVer = int(verString[2:])
        publishWip = 0

        devVerString = VER_WIP_RE.findall(os.path.basename(str(develFile)))[0]
        develVer = int(devVerString[1:3])
        develWip = int(devVerString[5:7])

        # ani 워크코드만을 위한 경로
        txtFile = str(os.path.join(scriptFolder, publishBasename+'.txt'))
        animFile = str(os.path.join(animFolder, publishBasename+'.anim'))

        geoCacheFolder = os.path.join(pubFolder, "data", "geoCache", publishBasename)

        if ext == '.ma':
            type = 'mayaAscii'
        elif ext == '.mb':
            type = 'mayaBinary'
        else:
            type = 'mayaBinary'
            print "savePublish: Invalid file format ("+ext+") specified: saving to Maya Binary"

        # devel file 저장
        if enableSave:
            # 현재 Scene을 develFile 이름으로 저장
            cmds.file(rename=develFile)
            cmds.file(save=True, type=type)

        if level3 == "ani" and self.projNameCombo.currentText() == "mrgo":
            if not QDir(scriptFolder).exists():
                os.makedirs(scriptFolder)
            if not QDir(animFolder).exists():
                os.makedirs(animFolder)
        
            if not standAlone :
                mel.eval('DI_animTransfer "%s" "%s" %s' % (animFile, txtFile, selectedAsset))

            #cmds.file(develFile, open=True, force=True)

        if level3 == "finalize" and self.projNameCombo.currentText() == "mrgo":
            if not QDir(geoCacheFolder).exists():
                os.makedirs(geoCacheFolder)

        # publishFolder 내에 생성되지 않은 폴더가 존재할 경우 폴더 생성
        if not QDir(dirname).exists():            
            os.makedirs(dirname)

        # 퍼블리쉬된 파일의 퍼미션을 쓰기모드로 변경
        if QFileInfo(publishFile).isFile():
            if not 'win' in sys.platform:
                os.chmod(publishFile, 0777)

        # publish file 저장
        if level3 == "ani" and self.projNameCombo.currentText() == "mrgo":
            cmds.file(rename=publishFile)
            cmds.file(save=True, type=type)
        elif level3 == "finalize" and self.projNameCombo.currentText() == "mrgo":
            cmds.file(rename=publishFile)
            cmds.file(save=True, type=type)
            startFrame = int(cmds.playbackOptions(q=True, minTime=True)) # float
            endFrame = int(cmds.playbackOptions(q=True, maxTime=True)) # florat
            location = geoCacheFolder
            # for geoBake
            try:
                if not standAlone :
                    mel.eval("mrgo_exportWorld")
                    mel.eval("mrgo_initiateWorld")
                    mel.eval("mrgo_muteWorld")
                    mel.eval('DI_geoBake %s %s "%s"' % (startFrame, endFrame, location))
            except:
                QMessageBox.warning(self, QString.fromLocal8Bit("경고"),
                    QString.fromLocal8Bit("[DI_geoBake] Bake가 되지 않았습니다."))
        else:
            # 저장된 파일을 publish 폴더로 복사            
            if 'win' in sys.platform:
                cmds.file(rename=publishFile)
                cmds.file(save=True, type=type)
                cmds.file(rename=develFile)
            else:
                os.system('cp -rfv %s %s' % (develFile, publishFile))
            


        # 퍼블리쉬된 파일의 퍼미션을 읽기모드로 변경
        if QFileInfo(publishFile).isFile():
            if not 'win' in sys.platform:
                os.chmod(publishFile, 0555)

        currDate = self.getDate()
        currTime = self.getTime()
        # xml 추가
        historyFile = str(self.getFileName(tab, level1, level2, level3, "historyFile", 0, 1))
        nc = NoteContainer()
        if QFileInfo(historyFile).isFile():
            nc.importSAX(historyFile)
        else:
            open(historyFile, 'w')
        # publish 추가
        nc.add(Note(self.userName,       # author
                    currDate,            # date
                    currTime,            # time
                    "publish",           # event
                    publishVer,          # version
                    publishWip,          # wipversion
                    subjectName,         # subject
                    unicode(comment)     # comment
                    ))
        if enableSave:
            # devel 추가
            nc.addN(Note(self.userName,      # author
                        currDate,            # date
                        currTime,            # time
                        "devel",             # event
                        develVer,            # version
                        develWip,            # wipversion
                        subjectName,         # subject
                        unicode(comment),     # comment
                        os.path.basename(develFile),
                        str(devSceneFolder)[:-1],
                        status,
                        progress,
                        ctime,
                        "",
                        application
                        ))
        # xml 저장
        nc.exportXML(historyFile)
        if enableSave:
            nc.ibXML(os.path.join(str(devSceneFolder),   ".%s.xml" % os.path.basename(develFile))   )

        devXML = os.path.join(str(devSceneFolder), ".%s.xml" % os.path.basename(develFile))
        pubXML = os.path.join(os.path.dirname(publishFile), ".%s.xml" % os.path.basename(publishFile))

        self.loadCurrentHistory()

        self.currOpenVerField.setText("v"+str(develVer).zfill(2))
        self.currOpenWipField.setText("v"+str(develWip).zfill(2))
        #self.currOpenWipField.setText("w01")
        self.currOpenFileNameLabel.setText(os.path.basename(develFile))

        self.currOpenCommentField.setPlainText(comment)

        devImage = self.takeSnapshot()
        pubImage = os.path.join(pubSceneFolder, ".%s.thumb.jpg" % os.path.basename(publishFile)   )

        if 'win' in sys.platform:
            os.system("copy %s %s" % (devXML, pubXML))
            os.system("copy %s %s" % (devImage, pubImage))
        else :
            os.system("cp -rf %s %s" % (devXML, pubXML))
            os.system("cp -rf %s %s" % (devImage, pubImage))
            

        QMessageBox.information(self, QString.fromLocal8Bit("Success"),
                            QString.fromLocal8Bit("%s\n completed publish." % publishFile))

        if closeSceneFile:
            self.closeFile2()

    def rollbackUI(self):
        level1 = self.currOpenLevel1
        level2 = self.currOpenLevel2
        level3 = self.currOpenLevel3
        tab = self.currOpenTab
        if len(level1):
            develFiles = self.getDevels(tab, level1, level2, level3, 0)
            develFiles = sorted(develFiles)
            numVersions = len(develFiles)
            if numVersions:
                d = QDialog(self)
                label = QLabel("Select Version to Rollback:")
                versionCombo = QComboBox()
                for i in range(numVersions):
                    version = self.getVersionFromFile(develFiles[i])
                    versionCombo.addItem(version)
                versionCombo.setCurrentIndex(numVersions-1)
                rollbackDevelNotes = QTextEdit()
                rollbackDevelNotes.setReadOnly(True)
                rollback = QPushButton('Rollback')
                cancel = QPushButton('cancel')
                self.connect(cancel, SIGNAL('clicked()'),
                             d.reject)
                layout = QVBoxLayout()
                layout2 = QHBoxLayout()
                layout2.addWidget(label)
                layout2.addWidget(versionCombo)
                layout3 = QHBoxLayout()
                layout3.addWidget(rollback)
                layout3.addWidget(cancel)
                layout.addLayout(layout2)
                layout.addWidget(rollbackDevelNotes)
                layout.addLayout(layout3)
                d.setLayout(layout)
                d.setWindowTitle("Rollback Devel")
                d.show()

    def loadCurrentHistory(self):
        level1 = self.currOpenLevel1
        level2 = self.currOpenLevel2
        level3 = self.currOpenLevel3
        tab = self.currOpenTab       
        print ' self.currOpenTab : ' , self.currOpenTab
        historyObj =  self.getEventNotes(tab, level1, level2, level3, 0, 1)
        
        # 아이템 갯수 정의
        self.currOpenHistoryTable.setRowCount(len(historyObj))
        # 테이블 안에 아이템 추가 
        for row, note in enumerate(historyObj):
            author = QTableWidgetItem(note.author)
            event = QTableWidgetItem(note.event)
            date = QTableWidgetItem(note.date.toString("MM/dd/yy")+" "+note.time.toString("hh:mm"))
            subject = QTableWidgetItem(note.subject)
            if note.event == "created":
                pub = QTableWidgetItem("")
                wip = QTableWidgetItem("")
            elif note.event == "publish":
                pub = QTableWidgetItem(str(note.version))
                wip = QTableWidgetItem("")
            else:
                pub = QTableWidgetItem(str(note.version))
                wip = QTableWidgetItem(str(note.wipversion))
            author.setTextAlignment(Qt.AlignCenter)
            event.setTextAlignment(Qt.AlignCenter)
            pub.setTextAlignment(Qt.AlignCenter)
            wip.setTextAlignment(Qt.AlignCenter)
            subject.setTextAlignment(Qt.AlignCenter)
            date.setTextAlignment(Qt.AlignCenter)
            self.currOpenHistoryTable.setItem(row, 0, author)
            self.currOpenHistoryTable.setItem(row, 1, event)
            self.currOpenHistoryTable.setItem(row, 2, pub)
            self.currOpenHistoryTable.setItem(row, 3, wip)
            self.currOpenHistoryTable.setItem(row, 4, subject)
            self.currOpenHistoryTable.setItem(row, 5, date)
            self.currOpenHistoryTable.setRowHeight( row , 20 )
            
        self.currOpenHistories = historyObj

    def loadAssetHistory(self):
        currSelected = self.getCurrentlySelectedItem(1, 3)
        historyObj =  self.getEventNotes(1, currSelected[0], currSelected[1], currSelected[2])
        # 아이템 갯수 정의
        self.assetHistoryTable.setRowCount(len(historyObj))
        # 히스토리 존재 유무 체크
        if not len(historyObj):
            return
        # 테이블 안에 아이템 추가
        for row, note in enumerate(historyObj):
            author = QTableWidgetItem(note.author)
            event = QTableWidgetItem(note.event)
            date = QTableWidgetItem(note.date.toString("MM/dd/yy")+" "+note.time.toString("hh:mm"))
            subject = QTableWidgetItem(note.subject)
            if note.event == "created":
                pub = QTableWidgetItem("")
                wip = QTableWidgetItem("")
            elif note.event == "publish":
                pub = QTableWidgetItem(str(note.version))
                wip = QTableWidgetItem("")
            else:
                pub = QTableWidgetItem(str(note.version))
                wip = QTableWidgetItem(str(note.wipversion))
            author.setTextAlignment(Qt.AlignCenter)
            event.setTextAlignment(Qt.AlignCenter)
            pub.setTextAlignment(Qt.AlignCenter)
            wip.setTextAlignment(Qt.AlignCenter)
            subject.setTextAlignment(Qt.AlignCenter)
            date.setTextAlignment(Qt.AlignCenter)
            self.assetHistoryTable.setItem(row, 0, author)
            self.assetHistoryTable.setItem(row, 1, event)
            self.assetHistoryTable.setItem(row, 2, pub)
            self.assetHistoryTable.setItem(row, 3, wip)
            self.assetHistoryTable.setItem(row, 4, subject)
            self.assetHistoryTable.setItem(row, 5, date)
        self.assetHistories = historyObj
        #if len(historyObj):
        #    self.assetCommentField.setPlainText(historyObj[0].comment)

    def loadShotHistory(self):
        currSelected = self.getCurrentlySelectedItem(2, 3)
        historyObj =  self.getEventNotes(2, currSelected[0], currSelected[1], currSelected[2])
        # 아이템 갯수 정의
        self.shotHistoryTable.setRowCount(len(historyObj))
        # 히스토리 존재 유무 체크
        if not len(historyObj):
            return
        # 테이블 안에 아이템 추가 
        for row, note in enumerate(historyObj):
            author = QTableWidgetItem(note.author)
            event = QTableWidgetItem(note.event)
            date = QTableWidgetItem(note.date.toString("MM/dd/yy")+" "+note.time.toString("hh:mm"))
            subject = QTableWidgetItem(note.subject)
            if note.event == "created":
                pub = QTableWidgetItem()
                wip = QTableWidgetItem()
            elif note.event == "publish":
                pub = QTableWidgetItem(str(note.version))
                wip = QTableWidgetItem()
            else:
                pub = QTableWidgetItem(str(note.version))
                wip = QTableWidgetItem(str(note.wipversion))
            author.setTextAlignment(Qt.AlignCenter)
            event.setTextAlignment(Qt.AlignCenter)
            pub.setTextAlignment(Qt.AlignCenter)
            wip.setTextAlignment(Qt.AlignCenter)
            subject.setTextAlignment(Qt.AlignCenter)
            date.setTextAlignment(Qt.AlignCenter)
            self.shotHistoryTable.setItem(row, 0, author)
            self.shotHistoryTable.setItem(row, 1, event)
            self.shotHistoryTable.setItem(row, 2, pub)
            self.shotHistoryTable.setItem(row, 3, wip)
            self.shotHistoryTable.setItem(row, 4, subject)
            self.shotHistoryTable.setItem(row, 5, date)
        self.shotHistories = historyObj
        #if len(historyObj):
        #    self.shotCommentField.setPlainText(historyObj[0].comment)

    def loadAssetBrowse(self):
        currSelected = self.getCurrentlySelectedItem(1, 3)
        devPath =  self.getFileName(1, currSelected[0], currSelected[1], currSelected[2], "devFolder")
        pubPath =  self.getFileName(1, currSelected[0], currSelected[1], currSelected[2], "pubFolder")
        devFiles = self.getFiles(devPath, "devel", True)
        pubFiles = self.getFiles(pubPath, "publish", True)

        self.assetDevelList.clear()
        self.assetPublishList.clear()
        for item in devFiles:
            self.assetDevelList.addItem(os.path.basename(item))
        for item in pubFiles:
            self.assetPublishList.addItem(os.path.basename(item))

    def loadShotBrowse(self):
        currSelected = self.getCurrentlySelectedItem(2, 3)
        devPath =  self.getFileName(2, currSelected[0], currSelected[1], currSelected[2], "devFolder")
        pubPath =  self.getFileName(2, currSelected[0], currSelected[1], currSelected[2], "pubFolder")
        devFiles = self.getFiles(devPath, "devel", True)
        pubFiles = self.getFiles(pubPath, "publish", True)

        self.shotDevelList.clear()
        self.shotPublishList.clear()
        for item in devFiles:
            self.shotDevelList.addItem(os.path.basename(item))
        for item in pubFiles:
            self.shotPublishList.addItem(os.path.basename(item))

    def clearCurrentHistory(self):
        self.currOpenHistoryTable.clear()

    def checkItem(self):
        try:
            return cmds.file(query=True, modified=True)
        except:
            return

    def removeProcess(self, tab, depth):
        currSelected = self.getCurrentlySelectedItem(tab, depth)
        if not self.confirmDialog("Confirm", 'Are you sure you want to remove directory?'):
            return
        result = self.removeItem(tab, currSelected[0], currSelected[1], currSelected[2])
        if result:
            #self.updateCurrentlyOpen()
            self.updateAssetTypeList()
            self.updateSequenceList()

    #===========================================================================
    # 정리할 함수들 = 시작 =
    #===========================================================================
    def componentDoubleClicked(self, tab, mode, item=None):        
        selected = 1
        currSelected = self.getCurrentlySelectedItem(tab, 3)
        self.currOpenLevel1 = currSelected[0]
        self.currOpenLevel2 = currSelected[1]
        self.currOpenLevel3 = currSelected[2]
        self.currOpenTab = self.tabWidget.currentIndex()
        self.currOpenProjectName = self.projNameCombo.currentText()
        self.currOpenSubject = ""

        devFolder = str(self.getFileName(self.currOpenTab, self.currOpenLevel1, self.currOpenLevel2, self.currOpenLevel3, "devFolder"))
        sceneFile = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "devel")

        previewImage = self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "previewFile")
        if not QFileInfo(previewImage).isFile():
            previewImage = NO_PREVIEW_FILENAME

        if mode == "devel":
            path = devFolder
        elif mode == "publish":
            selected = 0
            path = str(self.getFileName(self.currOpenTab, self.currOpenLevel1, self.currOpenLevel2, self.currOpenLevel3, "pubFolder"))

        if item is not None:            
            sceneFile = path+"/scenes/"+item.text()
            previewImage = path+("/scenes/.%s.thumb.jpg" % item.text())
            if not QFileInfo(previewImage).isFile():
                previewImage = NO_PREVIEW_FILENAME
            self.componentOpened(devFolder, sceneFile, mode, tab, currSelected, selected, previewImage, path)
            
        else: # item is None
            # 버전별 씬파일 보여주는 다이얼로그            
            sceneFolder = str(self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "sceneFolder"))
            mayaFiles = glob.glob(sceneFolder+"*.mb")

            defaultFiles = filter(SCENEFILE_RE.search, mayaFiles)
            subjectFiles = filter(SCENEFILE_WITH_SUBJECT_RE.search, mayaFiles)

            subjectLists = {}
            for i in subjectFiles:
                fileName = os.path.basename(i).rsplit('_', 1)[-1]
                basename = os.path.splitext(fileName)[0]
                if subjectLists.get(basename) is None:
                    subjectLists[basename] = []
                subjectLists[basename].append( i )

            for subject in subjectLists.keys():
                subjectLists[subject] = sorted(subjectLists[subject])

            buffer = []
            for subject in subjectLists.keys():
                buffer.append(os.path.basename(subjectLists[subject][-1]))

            if len(defaultFiles):
                buffer.append(os.path.basename(defaultFiles[-1]))

            buffer = sorted(buffer, reverse=True)

            if len(buffer) == 1:
                sp = QListWidgetItem(buffer[0])
                self.componentOpened(devFolder, sceneFile, mode, tab, currSelected, selected, previewImage, path, sp)
            elif len(buffer) == 0:
                self.componentOpened(devFolder, sceneFile, mode, tab, currSelected, selected, previewImage, path)
            else:
                self.componentFileUI = QDialog(self)
                self.componentFileUI.setWindowTitle("Open")
                fileList = QListWidget()
                fileList.addItems(buffer)
                self.connect(fileList, SIGNAL('itemDoubleClicked(QListWidgetItem*)'),
                             lambda value: self.componentOpened(devFolder, sceneFile, mode, tab, currSelected, selected, previewImage, path, value))
                layout = QHBoxLayout()
                layout.addWidget(fileList)
                self.componentFileUI.setLayout(layout)
                self.componentFileUI.resize(480,240)
                self.componentFileUI.show()

    def componentOpened(self, devFolder, sceneFile, mode, tab, currSelected, selected, previewImage, path, sp=None):
        print 'componentOpened'
        if sp is not None:
            sceneFile = path+"/scenes/"+sp.text()

        self.currOpenFile = sceneFile

        previewImage = path+("/scenes/.%s.thumb.jpg" % os.path.basename(str(sceneFile)))
        if not QFileInfo(previewImage).isFile():
            previewImage = NO_PREVIEW_FILENAME

        xmlFile = path+("/scenes/.%s.xml" % os.path.basename(str(sceneFile)))
        if QFileInfo(xmlFile).isFile():
            n = Core.Note.Note2.NoteContainer()
            n.importSAX(str(xmlFile))
            comment = n.getNotes()[0].comment
            self.currOpenCommentField.setPlainText(comment)
        else:
            self.currOpenCommentField.clear()
         
        if not self.openItem("devel", devFolder, str(sceneFile)):
            return
        
        sceneFolder = str(self.getFileName(tab, currSelected[0], currSelected[1], currSelected[2], "sceneFolder", 0, 1))
        if sceneFile == "":
            ver = "v01"
            wip = "w01"
            _filename = "%s_%s_%s_%s.mb" % (currSelected[1], currSelected[2], ver, wip)
            sceneFile = os.path.join( sceneFolder, str(_filename))
        else:
            ver = VER_RE.findall( str(sceneFile) )[0][1:]
            if mode == "devel":
                wip = WIP_RE.findall( str(sceneFile) )[0][1:]
            else:
                wip = ""

            if mode == "devel":
                try:
                    self.currOpenSubject = os.path.splitext(os.path.basename(str(sceneFile)))[0].split(ver+"_"+wip+"_")[1]
                except:
                    pass
            elif mode == "publish":
                try:
                    self.currOpenSubject = os.path.splitext(os.path.basename(str(sceneFile)))[0].split(ver+"_")[1]
                except:
                    pass

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
        self.currOpenLevel1Field.setText(currSelected[0])
        self.currOpenLevel2Field.setText(currSelected[1])
        self.currOpenLevel3Field.setText(currSelected[2])
        self.currOpenVerField.setText(ver)
        self.currOpenWipField.setText(wip)
        self.currOpenSaveDevelButton.setEnabled(selected)
        self.currOpenSavePublishButton.setEnabled(selected)
        #self.currOpenRollbackButton.setEnabled(True)
        self.currOpenCloseButton.setEnabled(True)
        self.currOpenSnapshotButton.setEnabled(True)
        self.currOpenRecordPlayblastButton.setEnabled(selected)
        #self.currOpenViewPlayblastButton.setEnabled(True)
        self.currOpenClearCommentButton.setEnabled(selected)
        self.currOpenSaveCommentButton.setEnabled(True)
        self.currOpenExploreButton.setEnabled(True)
        self.currOpenPreviewImage.setPixmap(QPixmap(previewImage))
        self.currOpenLocationField.setText(location)
        #self.currOpenCommentField.clear()
        self.loadCurrentHistory()
        # go to currently open
        self.tabWidget.setCurrentIndex(0)

        try:
            self.componentFileUI.close()
        except AttributeError:
            pass
        
        
        
        
    def refreshCurrentlyOpen(self):      
        if standAlone : return        
        sceneFile = cmds.file(q=1 ,l=1)[0]        
        if 'untitled' in sceneFile: return 
               
        sceneFileList = sceneFile.replace( self.showPath , '' )[1:]
        sceneFileList = sceneFileList.split('/')       
        # ['awesome', 'seq', 'TER', '234', 'ani', 'pub', 'scenes', '234_ani_v01.mb']
        # ['awesome', 'seq', 'TER', '234', 'ani', 'dev', 'scenes', '234_ani_v01_w03.mb']
        self.currOpenFile = sceneFile
        self.currOpenProjectName = sceneFileList[0]
        if self.projNameCombo.currentText() != self.currOpenProjectName : 
            thePrjIndex = list(self.getDirectoryList(self.showPath)).index(sceneFileList[0])
            self.projNameCombo.setCurrentIndex( thePrjIndex )
            
#        QtGui.QComboBox(). 
        tabName = 'Asset' if sceneFileList[1] == 'assets' else "shot"        
        tab = 1 if tabName == 'Asset' else 2
        
        mode = 'devel' if 'dev' in sceneFileList else 'publish'
        self.currOpenTab = tab
        self.currOpenLevel1 = sceneFileList[2]
        self.currOpenLevel2 = sceneFileList[3]
        self.currOpenLevel3 = sceneFileList[4]      
        
        if mode == "devel":
            ver = os.path.basename( sceneFile ).split('_')[2]
            wip = os.path.basename( sceneFile ).split('_')[3][:-3]            
            
            path =  str(self.getFileName(tab, self.currOpenLevel1, self.currOpenLevel2, self.currOpenLevel3, "devFolder"))                        
            try:
                self.currOpenSubject = os.path.splitext(os.path.basename(str(sceneFile)))[0].split(ver+"_"+wip+"_")[1]
            except : 
                self.currOpenSubject =''
            selected = 1            
        elif mode == "publish":
            path = str(self.getFileName( tab , self.currOpenLevel1, self.currOpenLevel2, self.currOpenLevel3, "pubFolder"))
            ver = os.path.basename( sceneFile ).split('_')[2]
            wip = ''  
            try :           
                self.currOpenSubject = os.path.splitext(os.path.basename(str(sceneFile)))[0].split(ver+"_")[1]
            except : 
                self.currOpenSubject =''
            selected = 0
           

        # preview Image
        subject = self.currOpenSubjectField.text()
        if len(subject):
            fileName = "."+self.currOpenLevel2+"_"+self.currOpenLevel3+"_"+ver+"_"+wip+"_"+subject+".mb.thumb.jpg"
        else:
            fileName = "."+self.currOpenLevel2+"_"+self.currOpenLevel3+"_"+ver+"_"+wip+".mb.thumb.jpg" 
#        previewImage = self.createThumbnailN(tab, self.currOpenLevel1, self.currOpenLevel2, self.currOpenLevel3, fileName)
        previewImage = path + ("/scenes/" + fileName)
        print 'previewImage : ' , previewImage        
        if not QFileInfo(previewImage).isFile():
            previewImage = NO_PREVIEW_FILENAME
            print  'NO_PREVIEW_FILENAME'            
         
        location = self.showPath + '/' + os.path.dirname( '/'.join( sceneFileList[:-2] ) )
        xmlFile = path+("/scenes/.%s.xml" % os.path.basename(str(sceneFile)))
        if QFileInfo(xmlFile).isFile():
            n = Core.Note.Note2.NoteContainer()
            n.importSAX(str(xmlFile))
            comment = n.getNotes()[0].comment
            self.currOpenCommentField.setPlainText(comment)
        else:
            self.currOpenCommentField.clear()

        self.currOpenFileNameLabel.setText(os.path.basename(str(sceneFile)))
        self.currOpenProjectField.setText(self.currOpenProjectName)
        self.currOpenProdField.setText(tabName)
        self.currOpenFileField.setText(mode)
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
        self.currOpenClearCommentButton.setEnabled(selected)
        self.currOpenSaveCommentButton.setEnabled(True)
        self.currOpenExploreButton.setEnabled(True)
        self.currOpenPreviewImage.setPixmap(QPixmap(previewImage))
        self.currOpenLocationField.setText(location)        
        self.loadCurrentHistory() 
#
#        self.tabWidget.setCurrentIndex(0)
        
        
        
        
    def updateUI(self, mode, offset=None):
        if mode == 'asset':
            self.assetPreviewImage.setPixmap(QPixmap(NO_PREVIEW_FILENAME))
            # 1. 테이블 클리어
            self.assetHistoryTable.clear()
            # 2. Header 에 라벨 추가
            self.assetHistoryTable.setHorizontalHeaderLabels( QStringList( ['Author', 'Event', 'V', 'W', 'Subject', 'Date']))
            # 3. 칼럼 사이즈 정의
            self.assetHistoryTable.setColumnWidth(0, 80)
            self.assetHistoryTable.setColumnWidth(1, 60)
            self.assetHistoryTable.setColumnWidth(2, 25)
            self.assetHistoryTable.setColumnWidth(3, 25)
            self.assetHistoryTable.setColumnWidth(4, 70)
            # 4. 아이템 갯수 정의
            self.assetHistoryTable.setRowCount(0)
            self.assetCommentField.clear()
            obj = [self.assetScrollList, self.componentScrollList]
            if offset is None: return
            for i in range(offset, len(obj)): obj[i].clear()
        elif mode == 'shot':
            self.shotPreviewImage.setPixmap(QPixmap(NO_PREVIEW_FILENAME))
            # 1. 테이블 클리어
            self.shotHistoryTable.clear()
            # 2. Header 에 라벨 추가
            self.shotHistoryTable.setHorizontalHeaderLabels( QStringList( ['Author', 'Event', 'V', 'W', 'Subject', 'Date']))
            # 3. 칼럼 사이즈 정의
            self.shotHistoryTable.setColumnWidth(0, 80)
            self.shotHistoryTable.setColumnWidth(1, 60)
            self.shotHistoryTable.setColumnWidth(2, 25)
            self.shotHistoryTable.setColumnWidth(3, 25)
            self.shotHistoryTable.setColumnWidth(4, 70)
            # 4. 아이템 갯수 정의
            self.shotHistoryTable.setRowCount(0)
            self.shotCommentField.clear()
            obj = [self.shotScrollList, self.shotComponentScrollList]
            if offset is None: return
            for i in range(offset, len(obj)): obj[i].clear()
        elif mode == 'currOpen':
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
            #self.currOpenRollbackButton.setEnabled(False)
            self.currOpenCloseButton.setEnabled(False)
            self.currOpenSnapshotButton.setEnabled(False)
            self.currOpenRecordPlayblastButton.setEnabled(False)
            self.currOpenViewPlayblastButton.setEnabled(False)
            self.currOpenClearCommentButton.setEnabled(False)
            #self.currOpenSaveCommentButton.setEnabled(False)
            self.currOpenExploreButton.setEnabled(False)
            self.currOpenPreviewImage.setPixmap(QPixmap(NO_PREVIEW_FILENAME))
            self.currOpenLocationField.clear()
            self.currOpenHistoryTable.setRowCount(0)
            self.currOpenHistoryTable.clear()
            self.currOpenHistoryTable.setHorizontalHeaderLabels( QStringList( ['Author', 'Event', 'V', 'W', 'Subject', 'Date']))
            self.currOpenHistoryTable.setColumnWidth(0, 80)
            self.currOpenHistoryTable.setColumnWidth(1, 60)
            self.currOpenHistoryTable.setColumnWidth(2, 25)
            self.currOpenHistoryTable.setColumnWidth(3, 25)
            self.currOpenHistoryTable.setColumnWidth(4, 70)
            self.currOpenCommentField.clear()
            self.currOpenCommentHistoryField.clear()
            self.currOpenSaveCommentButton.setEnabled(False)
            self.currOpenClearSelectedCommentButton.setEnabled(False)
            self.currOpenSaveSelectedCommentButton.setEnabled(False)

    def updateCurrentlyOpen(self):
        level1 = self.currOpenLevel1
        level2 = self.currOpenLevel2
        level3 = self.currOpenLevel3
        tab = self.currOpenTab
        currPath = self.getFileName(tab, level1, level2, level3, "folder")
        if level1 == "":
            self.clearCurrentHistory()
            # 기본정보 초기화
            self.currOpenProjectField.clear()
            self.currOpenProdField.clear()
            self.currOpenFileField.clear()
            self.currOpenVerField.clear()
            self.currOpenWipField.clear()
            self.currOpenLevel1Field.clear()
            self.currOpenLevel2Field.clear()
            self.currOpenLevel3Field.clear()
            # 버튼 비활성화
            self.currOpenSaveDevelButton.setEnabled(False)
            self.currOpenSavePublishButton.setEnabled(False)
            #self.currOpenRollbackButton.setEnabled(False)
            self.currOpenCloseButton.setEnabled(False)
            self.currOpenSnapshotButton.setEnabled(False)
            self.currOpenRecordPlayblastButton.setEnabled(False)
            self.currOpenViewPlayblastButton.setEnabled(False)
            self.currOpenClearCommentButton.setEnabled(False)
            self.currOpenSaveCommentButton.setEnabled(False)
            self.currOpenExploreButton.setEnabled(False)
            # 이미지 및 필드 초기화
            self.currOpenPreviewImage.setPixmap(QPixmap(NO_PREVIEW_FILENAME))
            self.currOpenLocationField.clear()
            self.currOpenCommentField.clear()
        elif QDir(currPath).exists():
            pass

    #===========================================================================
    # 정리할 함수들 = 끝 =
    #===========================================================================

    def closeEvent(self, event):
#        msg = QMessageBox.question(self, QString.fromLocal8Bit("확인창"),
#                QString.fromLocal8Bit("종료하시겠습니까?"),
#                QMessageBox.Ok | QMessageBox.Cancel)
#        if msg != QMessageBox.Ok:
#            event.ignore()
#            return

        settings = QSettings("DIGITAL idea", "iPipeline")
        settings.setValue("username", self.userNameLineEdit.text())
        settings.setValue("projectname", self.projNameCombo.currentText())
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("assetWindowState", self.splitter_asset.saveState())
        settings.setValue("shotWindowState", self.splitter_shot.saveState())
        app = None 

    def loadSettings(self):
        settings = QSettings("DIGITAL idea", "iPipeline")
        if settings.contains("username"):
            self.userName = settings.value("username").toString()
        if settings.contains("projectname"):
            self.projectName = settings.value("projectname").toString()
        settings.setValue("geometry", self.saveGeometry())
        self.splitter_asset.restoreState(settings.value("assetWindowState").toByteArray())
        self.splitter_shot.restoreState(settings.value("shotWindowState").toByteArray())

    def confirmDialog(self, title, text):
        msg = QMessageBox.question(self, title, text, QMessageBox.Ok | QMessageBox.Cancel)
        if msg != QMessageBox.Ok:
            return False
        return True

def pipeline():
    global app    
    try:        
        app.close()        
    except :        
        app = iPipeline()
    app.show()
        
    
    print ' iPipeline'

def pipeline_console():
    app = QApplication(sys.argv)
    mainWin = iPipeline()
#    print 'id(mainWin) : ' ,id(mainWin)    
#    if id(mainWin) not in [ id(n) for n in globals().values() ]:
#        mainWin.show()
    
    mainWin.show()
    sys.exit(app.exec_())

   
    


#***********************************************************************************************
#***    Launcher.
#***********************************************************************************************
if __name__ == "__main__": 
#    settings = QSettings("DIGITAL idea", "iPipeline")
#    for x in dir( settings ):
#        if x[0] != '_':
#            print x
#    print settings.pyqtConfigure()
    test = pipeline_console()
    
#    print test.getFileName( 0 , 'cha', 'humanA', 'rig', 'historyFile', 0, 0)
#    pipeline_console()

