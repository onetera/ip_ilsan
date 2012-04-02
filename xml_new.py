from PyQt4.QtXml import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import time

class XmlNew(object):
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

    def read(self, device):
        self.domDocument.setContent(device, True)
        root = self.domDocument.documentElement()
        node = root.firstChildElement()
        while not node.isNull():
            node = node.nextSiblingElement()
        return True

    def write2(self, device):
        indentSize = 4
        out = QTextStream( device)
        self.domDocument.save( out, indentSize)
        return True

    def test(self, value, mode=None):
        root = self.domDocument.documentElement()
        applications = root.elementsByTagName('applications').at(value)
        node = applications.firstChildElement()
        extensions = {}
        applications = {}
        while not node.isNull():
            sub = node.firstChild()
            buf = {}
            buf2 = []
            while not sub.isNull():
                data = sub.toElement().text()
                if sub.nodeName() == 'description':
                    buf['description'] = str(data)
                if sub.nodeName() == 'command':
                    buf['command'] = data
                if sub.nodeName() == 'pattern':
                    buf2.append(str(data))
                sub = sub.nextSibling()

            applications[ buf['description']] = {}
            applications[ buf['description']]['extension'] = buf2
            applications[ buf['description']]['command'] = buf['command']

            for ext in buf2:
                try:
                    #extensions[ext]['application'].append( buf['description'])
                    extensions[ext].append( buf['description'])
                except:
                    #extensions[ext] = {'application':[]}
                    extensions[ext] = []
                    #extensions[ext]['application'].append( buf['description'])
                    extensions[ext].append( buf['description'])
                #extensions[ext]['command'] = buf['command']
            node = node.nextSiblingElement()

        if mode is None:
            return applications
        else:
            return extensions

    def sortByApplication(self, value):
        temp = self.test(0, value)
        temp.update(self.test(1, value))
        return self.test(0, value), temp


if __name__ == '__main__':

    inFile = QFile( QString( 'preference_new.xml'))
    xml = XmlNew()
    xml.read2( inFile)
    workcode_application, common_application = xml.sortByApplication(None)
    #print str(workcode_application['Photoshop']['command']) % {'projdir':'/usr/local/test', 'filename':'test_v001.nk'}

    workcode_application, common_application = xml.sortByApplication(True)

