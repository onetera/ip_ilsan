# -*- coding: utf-8 -*-

from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys


from foundations.globals.constants import Constants
if 'linux' in sys.platform:
    try:
        import ldap
    except :    
        sys.path.append( '/lustre/INHouse/Tool/irtool/PyQt4.9.1/python2.7/lib/python2.7/site-packages/python_ldap-2.3.13-py2.7-linux-x86_64.egg' )
        import ldap
        
try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA = True
except ImportError:
    MAYA = False


#QTreeWidget.
class DeptTree( QDialog ):
    
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
#        uic.loadUi('ui/deptTree.ui', self)
        uic.loadUi( Constants.deptTreeUI , self)
        self.allUser = getAllLdapUser()
        self.allDepts =   self.allUser.keys()
        
        self.setWindowTitle( 'Department' )
        self.setTree()   
        self.setConnect() 
          
        self.show()

    def setTree(self):
        #self.dept_treeWidget
        root = QTreeWidgetItem( self.dept_treeWidget )
        root.setExpanded(1)
        
        allusers = sorted(self.allUser.keys())
        for m in allusers:
            dept_item = QTreeWidgetItem()
            dept_item.setData(0,0,QVariant(m) )
            root.addChild( dept_item )
            for n in self.allUser[m] :
                user = QTreeWidgetItem()
                user.setData( 0, 0, QVariant( n[0]+'('+n[1]+')' ) )
#                user.setData(0, QtCore.Qt.UserRole, Settings.Status.Network.iOnline)
                dept_item.addChild( user )
#        childDepts = root.addChildren( [ QTreeWidgetItem( x ) for x in self.allDepts ] )
        
    def setConnect(self):        
        self.connect(  self.dept_treeWidget , SIGNAL("itemDoubleClicked(QTreeWidgetItem*, int)"), self.pprint )
        self.connect( self.close_btn , SIGNAL("clicked()"), self.close )

        
    def pprint(self):  
        dept =  str( self.dept_treeWidget.currentItem().parent().text(0) ) 
        name =   str( self.dept_treeWidget.currentItem().text(0) )
        if dept == '':
            result = [ str(self.dept_treeWidget.currentItem().child(x).text(0) ) for x in range( self.dept_treeWidget.currentItem().childCount() )]
            result.insert(0, name )                 
        else :
            result = [ dept , name ]   
        self.emit(SIGNAL("Send"), result )
        print result             
        return result
                    
        
def getAllLdapUser( ):
        l=ldap.open( Constants.ldapAddress )
        uname="CN=ipipeline,CN=Users,DC=digitalidea,DC=co,DC=kr"
        password="idea"
        
        l.protocol_version=ldap.VERSION3        
        l.simple_bind_s(uname,password)
        
        base_dn = 'CN=Users,DC=digitalidea,DC=co,DC=kr'
        attr = ['info','sAMAccountNAME' , 'mail' ]        
        result = l.search_s(base_dn,ldap.SCOPE_SUBTREE ,)       
        
        dict = {}        
        depts = list(set( [ x[1].get('mail')[0] for x in result if x[1].get('mail')!= None ] ))
        
        users = [ x[1] for x in result if 'info' in x[1].keys() and 'sAMAccountName' in x[1].keys() ]        
        for x in users:            
            if x.get('mail') == None:
                if dict.get( 'Null' ) == None :
                        dict[ 'Null' ] = []
                dict[ 'Null' ].append( ( unicode( x['info'][0] ) , x['sAMAccountName'][0] ) )
            else:
                if dict.get( x.get('mail')[0] ) == None :
                    dict[ x.get('mail')[0] ] = []
                dict[ x.get('mail')[0] ].append( ( unicode( x['info'][0] ) , x['sAMAccountName'][0] ) )
        return dict


        
def deptTree(parent=None):
    if MAYA == True :              
        DeptTree_app = DeptTree(parent)
        DeptTree_app.show()
    else :
        DeptTree_app = QApplication(sys.argv)
        DeptTree_appWin = DeptTree(parent) 
#        DeptTree_app.exec_()       
        sys.exit(DeptTree_app.exec_())
        
if __name__ == '__main__':    
    deptTree()
#    for x in getAllLdapUser():
#        print x , ' : ' , getAllLdapUser()[x]



