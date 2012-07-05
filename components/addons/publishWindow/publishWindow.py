# -*- coding: utf-8 -*-

"""
**publishWindow.py**

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

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
class PublishWindow(QDialog):

    def __init__(self, level2='', level3='', subjectName='', devel1='', devel2='', publishFile='', o_filename='', parent=None):
        QDialog.__init__(self, parent)
        uifile = sorted(glob.glob(Constants.applicationDirectory+"components/addons/publishWindow/ui/*.ui"))[-1]
        uic.loadUi(uifile, self)

        self.level2 = level2
        self.level3 = level3
        self.subjectName = subjectName
        self.develSceneFolder = os.path.dirname(str(devel1))
        self.publishSceneFolder = os.path.dirname(str(publishFile))

        self.o_filename = o_filename

        # default button
        self.Devel1_radioButton.setChecked(True)
        self.Wip_radioButton.setChecked(True)
        self.Maya_radioButton.setChecked(True)

        self.Devel1_lineEdit.setText(os.path.basename(devel1))
        self.Devel2_lineEdit.setText(os.path.basename(devel2))
        self.Publish_lineEdit.setText(os.path.basename(publishFile))

        if not QFileInfo(devel1).isFile():
            self.Devel1_label.setText('OK')
            self.Devel1_label.setStyleSheet("color: green")

        if not QFileInfo(devel2).isFile():
            self.Devel2_label.setText('OK')
            self.Devel2_label.setStyleSheet("color: green")

        if QFileInfo(publishFile).isFile():
            self.Publish_label.setText('already exists.')
            self.Publish_label.setStyleSheet("color: red")
        else:
            self.Publish_label.setText('OK')
            self.Publish_label.setStyleSheet("color: green")

        #self.updateCustomField()
        self.connect(self.touser_btn, SIGNAL("clicked()"), self.addUser )
        #self.connect(self.Devel1_radioButton, SIGNAL("clicked()"), self.radioButtonClicked)
        #self.connect(self.Devel2_radioButton, SIGNAL("clicked()"), self.radioButtonClicked)

        if os.path.basename(publishFile) != '' :
            self.msg_textedit.setText( u' %s를 업로드 하였습니다.' % os.path.basename(publishFile) )
        self.loadSettings()

        self.setWindowTitle("Save Publish")

    def addUser(self):
        touserList = DeptTree( self )
        touserList.connect( touserList ,  SIGNAL("Send"),  self.addUserToLineEditor )
        
    def addUserToLineEditor(self , theList ):
        txt = str( self.tojid_lineEdit.text() )
        if len( theList ) > 1 :
            theStr = [txt] + theList[1:] if txt != '' else theList[1:] 
            users = ', '.join( theStr )
            self.tojid_lineEdit.setText( unicode(users ) )

    def updateCustomField(self):
        pub = str(self.Pub_spinBox.value()).zfill(2)
        wip = str(self.Wip_spinBox.value()).zfill(2)
        subject = self.Subject_lineEdit.text()
        if len(subject):
            res = "%s_%s_v%s_w%s_%s.mb" % (self.level2, self.level3, pub, wip, subject)
        else:
            res = "%s_%s_v%s_w%s.mb" % (self.level2, self.level3, pub, wip)

        self.Custom_lineEdit.setText(res)
        if QFileInfo(os.path.join(self.develSceneFolder, res)).isFile():
            self.Valid_lineEdit.setText("already exists.")
            self.Valid_lineEdit.setStyleSheet("color: red")
        else:
            self.Valid_lineEdit.setText("OK")
            self.Valid_lineEdit.setStyleSheet("color: green")

    def radioButtonClicked(self):
        if self.Devel1_radioButton.isChecked() or self.Devel2_radioButton.isChecked():
            self.groupBox.setEnabled(False)
        else:
            self.groupBox.setEnabled(True)

    def parseUserList(self):
        ''' [ dxxxxxx , dxxxxx , dxxxxx ] '''
        thetxt = str( self.tojid_lineEdit.text() ) 
        if thetxt == '' : return
        return [ re.search( 'd\d{5}' , x).group() for x in thetxt.split(',') ]

    def accept(self):       
                
        #if self.groupBox.isChecked():
        if self.Devel1_radioButton.isChecked():
            develFile = self.Devel1_lineEdit.text()
        elif self.Devel2_radioButton.isChecked():
            develFile = self.Devel2_lineEdit.text()
        #else:
        #    develFile = ""

        publishFile = self.Publish_lineEdit.text()
        if self.Publish_label.text() != "OK":
            if not self.confirmDialog("Confirm", "Are you sure you want to overwrite %s?" % publishFile):
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

        if not self.groupBox.isChecked():
            develFile = self.o_filename

        self.emit(SIGNAL("save"), self.groupBox.isChecked(), self.checkBox_close.isChecked(), develFile, publishFile, self.commentTextEdit.toPlainText(), status, progress, ctime, application)
        if self.tojid_lineEdit.text() != '' and self.sendMsg_gbox.isChecked():
            for x in self.parseUserList():
                Message( x , self.msg_textedit.toPlainText() )
        
        self.close()

    def confirmDialog(self, title, text):
        msg = QMessageBox.question(self, title, text, QMessageBox.Ok | QMessageBox.Cancel)
        if msg != QMessageBox.Ok:
            return False
        return True

    def closeEvent(self, e):
        settings = QSettings("DIGITAL idea", "iPipeline")
        settings.beginGroup("publish")
        settings.setValue("saveDevel", self.groupBox.isChecked())
        settings.setValue("closeFile", self.checkBox_close.isChecked())
        settings.setValue("msglist", unicode( self.tojid_lineEdit.text() ) )
        settings.setValue("msgchecked", self.sendMsg_gbox.isChecked() )
        settings.endGroup()

    def loadSettings(self):
        settings = QSettings("DIGITAL idea", "iPipeline")
        settings.beginGroup("publish")
        if settings.contains("saveDevel"):
            self.groupBox.setChecked(settings.value("saveDevel").toBool())
        if settings.contains("closeFile"):
            self.checkBox_close.setChecked(settings.value("closeFile").toBool())
        if settings.contains("msglist"):
            self.tojid_lineEdit.setText( unicode( settings.value("msglist") ) )
        if settings.contains("msgchecked"):
            self.sendMsg_gbox.setChecked( settings.value("msgchecked").toBool()  )
            
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    mainWin = PublishWindow()
    mainWin.show()
    sys.exit(app.exec_())
    
    
    
                