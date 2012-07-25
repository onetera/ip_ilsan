# -*- coding: utf-8 -*-

"""
**information.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    Information Module.

**Others:**

"""
#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import os
import glob
import re

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
if os.getenv('LOGNAME') == 'DIGITALIDEA\\d10218':
    import sys
    sys.path.append( '/home/d10218/work/ipipeline' )
    from foundations.globals.constants import Constants
else :    
    from foundations.globals.constants import Constants
    
from deptTree import deptTree , DeptTree
from xsend import Message
from userInfo import UserInformation


#from lib.checkUp.modelingCheckUp import modCheckup

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
class Information(QDialog):

    def __init__(self, title='', tab = '' , level1='' , level2='', level3='', ver=1, wip=1, subjectName='', currentlyFilename='', latestFilename='', parent=None):
        QDialog.__init__(self, parent) 
        uifile = sorted(glob.glob(Constants.applicationDirectory+"components/addons/information/ui/*.ui"))[-1]     
        uic.loadUi( uifile , self)
#        uic.loadUi(Constants.applicationDirectory+"components/addons/information/ui/information06.ui", self)
#        print 'latestFilename = ' , latestFilename
#        self.showname = currentlyFilename.split( os.sep )[1] if currentlyFilename.split( os.sep ) != [''] else 'TEMP'
        self.tab = tab
        self.userinfo = UserInformation()
        self.level1 = level1
        self.level2 = level2
        self.level3 = level3
        self.subjectName = subjectName
        self.ver = ver
        self.wip = wip
        # default button
        #self.Currently_radioButton.setChecked(True)
        #self.Wip_radioButton.setChecked(True)
        #self.Maya_radioButton.setChecked(True)
        
        self.sceneFolder = os.path.dirname(str(currentlyFilename))
        self.Currently_lineEdit.setText(os.path.basename(currentlyFilename))
        #self.Status_comboBox.addItems(["TEMP", "WIP", "FINISH"])
        #self.applicationComboBox.addItems(['iMaya', 'iQualoth', 'iRman'])
        
        if not QFileInfo(currentlyFilename).isFile():
            self.Devel1_label.setText('OK')
            self.Devel1_label.setStyleSheet("color: green")
        if currentlyFilename == latestFilename:
            self.Latest_radioButton.setEnabled(False)
        else:
            self.Latest_lineEdit.setText(os.path.basename(latestFilename))
            if not QFileInfo(currentlyFilename).isFile():
                self.Devel2_label.setText('OK')
                self.Devel2_label.setStyleSheet("color: green")

        self.Pub_spinBox.setValue(ver)
        self.Wip_spinBox.setValue(wip)
        self.Subject_lineEdit.setText(subjectName)
        self.updateCustomField()

        self.connect(self.Currently_radioButton, SIGNAL("clicked()"), self.radioButtonClicked)
        self.connect(self.Latest_radioButton, SIGNAL("clicked()"), self.radioButtonClicked)
        self.connect(self.Custom_radioButton, SIGNAL("clicked()"), self.radioButtonClicked)

        self.connect(self.Pub_spinBox, SIGNAL("valueChanged(int)"), self.updatePubField)
        self.connect(self.Wip_spinBox, SIGNAL("valueChanged(int)"), self.updateCustomField)
        self.connect(self.Subject_lineEdit, SIGNAL("textChanged(const QString&)"), self.updateCustomField)        
        self.connect(self.touser_btn, SIGNAL("clicked()"), self.addUser )
#        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.saveas)
            
        if os.path.basename(currentlyFilename) != '' :
            self.msg_textedit.setText( u'%s님이 %s를 Devel에 저장 하였습니다.' % (self.userinfo.name , os.path.basename(currentlyFilename) ))
        self.loadSettings()      
        self.setWindowTitle(title)
#        self.result = 0

    def addUser(self):
        touserList = DeptTree( self )
        touserList.connect( touserList ,  SIGNAL("Send"),  self.addUserToLineEditor )
        
    def addUserToLineEditor(self , theList ):
        txt = str( self.tojid_lineEdit.text() )
        if len( theList ) > 1 :
            theStr = [txt] + theList[1:] if txt != '' else theList[1:] 
            users = ', '.join( theStr )
            self.tojid_lineEdit.setText( unicode(users ) )
        
    def updatePubField(self):
        self.Wip_spinBox.setValue( 1 )
        self.updateCustomField()
        
    def updateCustomField(self):        
        pub = str(self.Pub_spinBox.value()).zfill(2)        
        wip = str(self.Wip_spinBox.value()).zfill(2)
        subject = self.Subject_lineEdit.text()
        if len(subject):
            res = "%s_%s_v%s_w%s_%s.mb" % (self.level2, self.level3, pub, wip, subject)
        else:
            res = "%s_%s_v%s_w%s.mb" % (self.level2, self.level3, pub, wip)

        self.Custom_lineEdit.setText(res)
        if QFileInfo(os.path.join(self.sceneFolder, res)).isFile():
            self.Valid_lineEdit.setText("already exists.")
            self.Valid_lineEdit.setStyleSheet("color: red")
        else:
            self.Valid_lineEdit.setText("OK")
            self.Valid_lineEdit.setStyleSheet("color: green")

    def radioButtonClicked(self):
        if self.Currently_radioButton.isChecked() or self.Latest_radioButton.isChecked():
            self.groupBox.setEnabled(False)
        else:
            self.groupBox.setEnabled(True)


    def accept(self):  
                
        if self.Currently_radioButton.isChecked():
            filename = self.Currently_lineEdit.text()
        elif self.Latest_radioButton.isChecked():
            filename = self.Latest_lineEdit.text()
        elif self.Custom_radioButton.isChecked():
            filename = self.Custom_lineEdit.text()
            self.subjectName = self.Subject_lineEdit.text()
            if self.Valid_lineEdit.text() != "OK":
                if not self.confirmDialog("Confirm", "Are you sure you want to overwrite %s?" % filename):
                    return
        if self.Temp_radioButton.isChecked():
            status = "TEMP"
            progress = 10
        elif self.Wip_radioButton.isChecked():
            status = "WIP"
            progress = 50
        elif self.Finish_radioButton.isChecked():
            status = "FINISH"
            progress = 100

        if self.Maya_radioButton.isChecked():
            application = "iMaya"
        elif self.Rman_radioButton.isChecked():
            application = "iRman"
        elif self.Qualoth_radioButton.isChecked():
            application = "iQualoth"

        ctime = 1
        self.result = 1
        self.emit(SIGNAL("save"), filename, self.commentTextEdit.toPlainText(), status, progress, ctime, application, self.subjectName , self.tab)
        if self.tojid_lineEdit.text() != '' and self.sendMsg_gbox.isChecked() :
#            Message( 'd10218' , self.msg_textedit.toPlainText() )
            for x in self.parseUserList():
                Message( x , self.msg_textedit.toPlainText() ) 
        self.close()

    def parseUserList(self):
        ''' [ dxxxxxx , dxxxxx , dxxxxx ] '''
        thetxt = str( self.tojid_lineEdit.text() ) 
        if thetxt == '' : return
        return [ re.search( 'd\d{5}' , x).group() for x in thetxt.split(',') ]

    def confirmDialog(self, title, text):
        msg = QMessageBox.question(self, title, text, QMessageBox.Ok | QMessageBox.Cancel)
        if msg != QMessageBox.Ok:
            return False
        return True
    

    def closeEvent(self, e):
        settings = QSettings("DIGITAL idea", "iPipeline")
        settings.beginGroup("develPub")
        settings.setValue("devmsglist", unicode( self.tojid_lineEdit.text() ) )
        settings.setValue("msgchecked", self.sendMsg_gbox.isChecked() )
        settings.endGroup()

    def loadSettings(self):
        settings = QSettings("DIGITAL idea", "iPipeline")
        settings.beginGroup("develPub")        
        if settings.contains("devmsglist"):
            self.tojid_lineEdit.setText( settings.value("devmsglist").toString()  )
        if settings.contains("msgchecked"):
            self.sendMsg_gbox.setChecked( settings.value("msgchecked").toBool()  )
            
            
            
    
if __name__ == '__main__':
#    print Constants.applicationDirectory+"components/addons/information/ui/information06.ui"
#    import foundations
    app = QApplication(sys.argv)
    mainWin = Information()
    mainWin.show()
    sys.exit(app.exec_())
        
