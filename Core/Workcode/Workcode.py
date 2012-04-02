# -*- coding: utf-8 -*-

"""
**Note.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    Note Module.

**Others:**

"""

#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

DirectoryTag = QString("DIRECTORY")
NameAttribute = QString("NAME")
DescriptionAttribute = QString("DESCRIPTION")

#***********************************************************************************************
#***    Module classes and definitions.
#***********************************************************************************************
class StandardItem(QStandardItem):
    """
    This class is the **StandardItem** class.
    """

    def __init__(self, text):
        QStandardItem.__init__(self, text)

        self.m_description = QStandardItem()
        self.m_description.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

    def descriptionItem(self):
        return self.m_description

    def description(self):
        return self.m_description.text()

    def addDescription(self, text):
        self.m_description.setText(text)

class StandardTreeModel(QStandardItemModel):
    def __init__(self, parent):
        QStandardItemModel.__init__(self, parent)
        self.initialize()

    def initialize(self):
        self.setHorizontalHeaderLabels(
            QStringList(['Name', 'Description']))
        for column in range(1, self.columnCount()):
            self.horizontalHeaderItem(column).setTextAlignment(
                Qt.AlignVCenter | Qt.AlignLeft)

    def createNewTask(self, root, name):
        nameItem = StandardItem(name)
        root.appendRow([nameItem, nameItem.descriptionItem()])
        return nameItem

    def insertNewTask(self, insert, name, index):
        parent = QStandardItem()
        if insert == 'AtTopLevel':
            parent = self.invisibleRootItem()
        else:
            if index.isValid():
                parent = self.itemFromIndex(index)
                if not parent:
                    return
                if insert == 'AsSibling':
                    parent = parent.parent() if parent.parent() else self.invisibleRootItem()
            else:
                return
        return self.createNewTask(parent, name)

    def clear(self):
        QStandardItemModel.clear(self)
        self.initialize()

    def save(self, filename):
        if not filename.isEmpty():
            m_filename = filename

        file = QFile(m_filename)
        if not file.open(QIODevice.WriteOnly | QIODevice.Text):
            print 'error'

        writer = QXmlStreamWriter(file)
        writer.setAutoFormatting(True)
        writer.writeStartDocument()
        writer.writeStartElement("WORKCODE")
        writer.writeAttribute("VERSION", "1.0")
        self.writeTaskAndChildren(writer, self.invisibleRootItem())
        writer.writeEndElement() # WORKCODE
        writer.writeEndDocument()

    def writeTaskAndChildren(self, writer, root):
        if root != self.invisibleRootItem():
            #item = StandardItem(root)
            writer.writeStartElement(DirectoryTag)
            writer.writeAttribute(NameAttribute, root.text())
            writer.writeAttribute(DescriptionAttribute, root.description())
        for row in range(root.rowCount()):
            self.writeTaskAndChildren(writer, root.child(row, 0))
        if root != self.invisibleRootItem():
            writer.writeEndElement()

    def load(self, filename):
        if not filename.isEmpty():
            m_filename = filename

        file = QFile(m_filename)
        if not file.open(QIODevice.ReadOnly):
            print 'error'

        self.clear()

        stack = []
        stack2 = {}
        stack.append(self.invisibleRootItem())
        reader = QXmlStreamReader(file)
        while not reader.atEnd():
            reader.readNext()
            if reader.isStartElement():
                if reader.name() == DirectoryTag:
                    name = reader.attributes().value(NameAttribute).toString()
                    description = reader.attributes().value(DescriptionAttribute).toString()
                    nameItem = self.createNewTask(stack[-1], name)
                    nameItem.addDescription(description)
#------------------------------------------------------------------------------
                    buf = []
                    for c in stack:
                        buf.append( str(c.text()) )
                    res = os.path.join(os.sep.join( buf ), str(name))
                    if res.find(os.sep) != -1:
                        token = res.split(os.sep)[1]
                        stack2[token].append( res[len(token)+2:] )
                    else:
                        stack2[res] = []

                    stack.append(nameItem)

            elif reader.isEndElement():
                if reader.name() == DirectoryTag:
                    stack.pop()

        if len(stack) != 1 and stack[0] != self.invisibleRootItem():
            print 'loading error: possibly corrupt file'

        return stack2