from PyQt4.QtXml import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import time

class iXML(object):
    def __init__(self):
        # xml read
        self.filename = ''
        self.location = ''
        self.username = ''
        self.created = time.strftime('%b %d, %Y %I:%M %p')
        self.status = 'WIP'
        self.progress = '0'
        self.time = '8'
        self.comment = ''
        self.publish = ''
        self.application = ''

        self.domDocument = QDomDocument()
        self.domElementForItem = {}

    def read(self, device):
        ok, errorStr, errorLine, errorColumn = self.domDocument.setContent(device, True)
        root = self.domDocument.documentElement()
        node = root.firstChildElement()
        while not node.isNull():
            self.domElementForItem[ str( node.tagName()) ] = node.text()
            node = node.nextSiblingElement()
        return True

    def getData(self):
        return self.domElementForItem

    def printS(self):
        return self.domDocument.toString()

    def updateDomElement(self, element, text):
        root = self.domDocument.documentElement()
        oldElement = root.firstChildElement( element)
        if not oldElement.isNull():
            newElement = self.domDocument.createElement( element)
            newText = self.domDocument.createTextNode( text)
            newElement.appendChild( newText)
            self.domElementForItem[ oldElement.tagName() ] = QString( text)
            root.replaceChild( newElement, oldElement)
        #else:
        #    self.createElement(element, text)

    def findElement(self, element):
        root = self.domDocument.documentElement()
        node = root.firstChildElement( element)
        if not node.isNull():
            return node.text()
        return None

    def createHeader(self):
        doc = self.domDocument
        header = doc.createProcessingInstruction( 'xml', 'version=\"1.0\" encoding=\"UTF-8\"')
        doc.appendChild( header)
        root = doc.createElement( 'root')
        doc.appendChild( root)

    def createElement(self, element, text, parentItem=None):
        root = self.domDocument.documentElement()
        newElement = self.domDocument.createElement( element)
        newText = self.domDocument.createTextNode( text)
        newElement.appendChild( newText)
        root.appendChild( newElement)

    def write_test(self, device):
        indentSize = 4
        out = QTextStream( device)
        self.domDocument.save( out, indentSize)
        return True
        
    def write(self, device):
        indentSize = 4

        doc = QDomDocument()
        header = doc.createProcessingInstruction( 'xml', 'version=\"1.0\" encoding=\"UTF-8\"')
        doc.appendChild( header)
        root = doc.createElement( 'root')
        doc.appendChild( root)

        for c in ['filename', 'location', 'username', 'created', 'status', 'progress', 'time', 'comment', 'publish', 'application']:
            if c == 'filename': text = self.filename
            elif c == 'location': text = self.location
            elif c == 'username': text = self.username
            elif c == 'created': text = self.created
            elif c == 'status': text = self.status
            elif c == 'progress': text = self.progress
            elif c == 'time': text = self.time
            elif c == 'comment': text = self.comment
            elif c == 'publish': text = self.publish
            elif c == 'application': text = self.application
            filename = doc.createElement( c)
            root.appendChild( filename)
            t = doc.createTextNode( text)
            filename.appendChild( t)

        out = QTextStream( device)
        doc.save(out, indentSize)
        return True


    #############
    # new version
    #############

    def newHeader(self):
        doc = self.domDocument
        header = doc.createProcessingInstruction( 'xml', 'version=\"1.0\" encoding=\"UTF-8\"')
        doc.appendChild( header)
        root = doc.createElement( 'ibrowser')
        version = doc.createAttribute( 'version')
        version.setValue( '1')
        root.setAttributeNode( version)
        doc.appendChild( root)

    def newElement(self, element, items):
        root = self.domDocument.documentElement()
        app = root.firstChildElement( 'group')
        if not app.isNull() and app.attributeNode( 'id').value() == element:
            group = self.domDocument.createElement( 'group')
            for c in items.keys():
                id = self.domDocument.createAttribute( c)
                id.setValue( items[c])
                group.setAttributeNode( id)
                app.appendChild( group) 
                

        else:
            group = self.domDocument.createElement( 'group')
            id = self.domDocument.createAttribute( 'id')
            id.setValue( element)
            group.setAttributeNode( id)
            root.appendChild( group) 

    def parse(self):
        root = self.domDocument.documentElement()
        app = root.firstChildElement( 'group')
        child = app.firstChildElement()
        app = Application()
        while not child.isNull():
            name = child.attributeNode( 'id').value()
            filter = child.attributeNode( 'filter').value()
            command = child.attributeNode( 'command').value()
            app.addItem( name, filter, command)
            child = child.nextSiblingElement()
        return app

    def updateElement3(self, app2, filter, command):
        root = self.domDocument.documentElement()
        app = root.firstChildElement( 'group')
        child = app.firstChildElement()
        while not child.isNull():
            name = child.attributeNode( 'id').value()
            if name == app2:
                child.setAttribute( 'filter', filter)
                child.setAttribute( 'command', command)
                break
            child = child.nextSiblingElement()

    def read2(self, device):
        ok, errorStr, errorLine, errorColumn = self.domDocument.setContent(device, True)
        root = self.domDocument.documentElement()
        node = root.firstChildElement()
        while not node.isNull():
            #self.domElementForItem[ str( node.tagName()) ] = node.text()
            node = node.nextSiblingElement()
        return True

    def write2(self, device):
        indentSize = 4
        out = QTextStream( device)
        self.domDocument.save( out, indentSize)
        return True

class ApplicationItem(object):
    def __init__(self, name, filter, command):
        self.name = name
        self.filter = filter
        self.command = command

class Application(object):
    def __init__(self):
        self.items = []

    def addItems(self, items):
        self.items = items

    def addItem(self, name, filter, command):
        self.items.append( ApplicationItem( name, filter, command))

    def findText(self, text):
        for row, item in enumerate(self.items):
            if item.name == text:
                return row

    def findItem(self, text):
        for row, item in enumerate(self.items):
            if item.name == text:
                return self.items[ row]

    def findApp(self, ext):
        ext = str( ext).split('.')[1]
        for row, item in enumerate(self.items):
            if str( item.filter).find( ext) != -1:
                return item.command

    def keys(self):
        temp = []
        for row, item in enumerate(self.items):
            temp.append( str( item.name))
        return temp

    def extensions(self):
        temp = {}
        for row, item in enumerate(self.items):
            ext = str( item.filter)
            if ext.find( ',') != -1:
                for c in ext.split(','):
                    temp[ '*.'+c.strip()] = None
            else:
                temp[ '*.'+ext] = None
        return temp.keys()

    def getItems(self):
        return self.items
        
    def getApplication(self):
        temp = {}
        for row, item in enumerate(self.items):
            f = str( item.filter)
            if len( f.split(',')) != 1:
                _f = f.split(',')[0].strip()
            else:
                _f = f
            temp[ str( item.name)] = _f
        return temp

if __name__ == '__main__':
    inFile = QFile( QString( 'preferences.xml'))
    xml = XML()
    xml.read2( inFile)
    print xml.updateElement3()


