from PyQt4.QtCore import *
from PyQt4.QtXml import *

import xml.sax.handler

class Note(object):
    def __init__(self, filename=None, location=None, username=None,
                 created=None, status=None, progress=None, time=None, publish=None,
                 application=None, comment=None):
        self.filename = filename
        self.location = location
        self.username = username
        self.created = created
        self.status = status
        self.progress = progress
        self.time = time
        self.publish = publish
        self.application = application
        self.comment = comment

class NoteContainer(object):
    def __init__(self):
        self.__fname = QString()
        self.__notes = []
        self.__noteFromId = {}

    def __iter__(self):
        for pair in iter(self.__notes):
            yield pair

    def __len__(self):
        return len(self.__notes)
    
    def getNotes(self, reverse=False):
        if reverse:
            notes = self.__notes
            notes.reverse()
        else:
            notes = self.__notes
        return notes

    def clear(self, clearFilename=True):
        self.__notes = []
        self.__noteFromId = {}
        if clearFilename:
            self.__fname = QString()

    def add(self, note):
        #if id(note) in self.__noteFromId:
        #    return False
        # test
        self.__notes.append( note )

    def addN(self, note):
        #if id(note) in self.__noteFromId:
        #    return False
        # test
        self.__notes.append( note )
        self.__special = []
        self.__special.append( note )

    def ibXML(self, fname):
        error = None
        fh = None
        try:
            fh = QFile(fname)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError, unicode(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec("UTF-8")
            stream << ("<?xml version='1.0' encoding='UTF-8'?>\n"
                       "<root>\n")
            for note in self.__special:
                stream << ("    <filename>%s</filename>\n"
                           "    <location>%s</location>\n"
                           "    <username>%s</username>\n"
                           "    <created>%s</created>\n"
                           "    <status>%s</status>\n"
                           "    <progress>%s</progress>\n"
                           "    <time>%s</time>\n"
                           "    <comment>%s</comment>\n"
                           "    <publish/>\n"
                           "    <application>%s</application>\n" % (
                                note.filename,
                                note.location,
                                note.author,
                                note.date.toString("MMM dd, yyyy ")+note.time.toString("hh:mm AP"),
                                note.status,
                                note.progress,
                                note.ctime,
                                note.comment.strip(),
                                note.application)
                           )
            stream << "</root>\n"
        except (IOError, OSError), e:
            error = "Failed to export: %s" % e
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            return True, "Exported %d note records to %s" % (
                    len(self.__special), QFileInfo(fname).fileName())

    def exportXML(self, fname):
        error = None
        fh = None
        try:
            fh = QFile(fname)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError, unicode(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec("UTF-8")
            stream << ("<?xml version='1.0' encoding='UTF-8'?>\n"
                       "<notes>\n")
            for note in self.__notes:
                stream << ("  <note>\n"
                           "    <author>%s</author>\n"
                           "    <date>%s</date>\n"
                           "    <time>%s</time>\n"
                           "    <event>%s</event>\n" % (
                                note.author, note.date.toString("MM/dd/yyyy"), note.time.toString(), note.event))
                if note.event == "devel":
                    stream << ("    <version>%s</version>\n"
                               "    <wipversion>%s</wipversion>\n" % (note.version, note.wipversion))
                elif note.event == "publish":
                    stream << "    <version>%s</version>\n" % note.version
                stream << "    <subject>%s</subject>\n" % note.subject
                stream << ("    <comment>%s</comment>\n"
                           "  </note>\n" % note.comment.strip())
            stream << "</notes>\n"
        except (IOError, OSError), e:
            error = "Failed to export: %s" % e
        finally:
            if fh is not None:
                fh.close()
            if error is not None:
                return False, error
            return True, "Exported %d note records to %s" % (
                    len(self.__notes), QFileInfo(fname).fileName())

    def readXML(self):
        outString = QString()
        for i in range(len(self.__notes), 0, -1):
            note = self.__notes[i-1]
            outString += "Author: %s\n" % note.author
            outString += "Date: %s %s\n" % (note.date.toString("MM/dd/yyyy"), note.time.toString())
            if note.event == "devel":
                outString += "Event: %s (Version:%s, Wip: %s)\n" % (note.event, note.version, note.wipversion)
            elif note.event == "publish":
                outString += "Event: %s (Version:%s)\n" % (note.event, note.version)
            else:
                outString += "Event: %s\n" % note.event
            #if note.event != "created":
            #if not note.comment.trimmed().isEmpty():
            outString += "Comment: %s\n\n" % note.comment
            #else:
                #outString += "\n"
        return outString

    def setFilename(self, fname):
        self.__fname = fname

    def filename(self):
        return self.__fname

    @staticmethod
    def formats():
        return "*.xml"

    def importSAX(self, fname):
        handler = NoteHandler(self)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(fname)


class NoteHandler(xml.sax.handler.ContentHandler):
    def __init__(self, notes):
        self.notes = notes
        self.text = ""
        self.error = None
        
        self.bfilename = False
        self.blocation = False
        self.busername = False
        self.bcreated = False
        self.bstatus = False
        self.bprogress = False
        self.btime = False
        self.bcomment = False
        self.bpublish = False
        self.bapplication = False

    def clear(self):
        self.filename = None
        self.location = None
        self.username = None
        self.created = None
        self.status = None
        self.progress = 1
        self.time = ''
        self.publish = ''
        self.application = ''
        self.comment = ''

    def startElement(self, name, attributes):
        if name == "root":
            self.clear()
        if name == "filename":
            self.bfilename = True
        if name == "location":
            self.blocation = True
        if name == "username":
            self.busername = True
        if name == "created":
            self.bcreated = True
        if name == "status":
            self.bstatus = True
        if name == "progress":
            self.bprogress = True
        if name == "time":
            self.btime = True
        if name == "publish":
            self.bpublish = True
        if name == "application":
            self.bapplication = True
        if name == "comment":
            self.bcomment = True
        #self.comment = ''

    def characters(self, text):
        if self.bfilename:
            self.filename = text
            self.bfilename = False
        if self.blocation:
            self.location = text
            self.blocation = False
        if self.busername:
            self.username = text
            self.busername = False
        if self.bcreated:
            self.created = text
            self.bcreated = False
        if self.bstatus:
            self.status = text
            self.bstatus = False
        if self.bprogress:
            self.progress = text
            self.bprogress = False
        if self.btime:
            self.time = text
            self.btime = False
        if self.bpublish:
            self.publish = text
            self.bpublish = False
        if self.bapplication:
            self.application = text
            self.bapplication = False
        if self.bcomment:
            self.comment += text

    def endElement(self, name):
        if name == "comment":
            self.bcomment = False
        if name == "root":
            self.notes.add(Note(self.filename, self.location, self.username,
                    self.created, self.status, self.progress, self.time, self.publish.rstrip(), self.application,
                    self.comment.rstrip()))
            self.clear()

if __name__ == "__main__":
    s = NoteContainer()
    s.importSAX('/show/mrgo/seq/SS_01/ACR/cleanplate/dev/scenes/.ACR_cleanplate_v01_w01.mb.xml')
    print s.getNotes()
    #s.exportXML("../../Template/export.xml")
    #print s.readXML()
