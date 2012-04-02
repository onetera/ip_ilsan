# -*- coding: utf-8 -*-

"""
**assistantFunctions.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    assistantFunctions Module.

**Others:**

"""

#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
from PyQt4 import QtCore, QtGui

#***********************************************************************************************
#***    Internal imports.
#***********************************************************************************************
from foundations.globals.constants import Constants

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
class assistantFunctions:
    """
    This class is the **assistantFunctions** class.
    """

    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal='triggered()'):
        action = QtGui.QAction( text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(Constants.applicationDirectory+"resources/%s" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable( True)
        return action
    
    
    #def createMenuAction(self, menu, icon, text, checkable, group, data):