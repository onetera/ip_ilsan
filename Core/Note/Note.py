from PyQt4.QtCore import *
from PyQt4.QtXml import *

import xml.sax.handler

class Note(object):
    def __init__(self, author=None, date=None, time=None,
                 event=None, version=None, wipversion=None, subject='', comment=None,
                 filename=None, location=None, status=None, progress=None, ctime=None,
                 publish=None, application=None):
        self.author = author
        self.date = date
        self.time = time
        self.event = event
        self.version = version
        self.wipversion = wipversion
        self.subject = subject
        self.comment = comment
        
        self.filename = filename
        self.location = location
        self.status = status
        self.progress = progress
        self.ctime = ctime
        self.publish = publish
        self.application = application

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
        
        self.bauthor = False
        self.bdate = False
        self.btime = False
        self.bevent = False
        self.bversion = False
        self.bwipversion = False
        self.bsubject = False
        self.bcomment = False

    def clear(self):
        self.author = None
        self.date = None
        self.time = None
        self.event = None
        self.version = None
        self.wipversion = 1
        self.subject = ''
        self.comment = ''

    def startElement(self, name, attributes):
        if name == "note":
            self.clear()
        if name == "author":
            self.bauthor = True
        if name == "date":
            self.bdate = True
        if name == "time":
            self.btime = True
        if name == "event":
            self.bevent = True
        if name == "version":
            self.bversion = True
        if name == "wipversion":
            self.bwipversion = True
        if name == "subject":
            self.bsubject = True
        self.comment = ''

    def characters(self, text):
        if self.bauthor:
            self.author = text
            self.bauthor = False
        if self.bdate:
            ymd = text.split("/")
            if len(ymd) != 3:
                raise ValueError, "invalid date"
            self.date = QDate(int(ymd[2]), int(ymd[0]), int(ymd[1]))
            self.bdate = False
        if self.btime:
            hms = text.split(":")
            if len(hms) != 3:
                raise ValueError, "invalid time"
            self.time = QTime(int(hms[0]), int(hms[1]), int(hms[2]))
            self.btime = False
        if self.bevent:
            self.event = text
            self.bevent = False
        if self.bversion:
            self.version = int(text)
            self.bversion = False
        if self.bwipversion:
            self.wipversion = int(text)
            self.bwipversion = False
        if self.bsubject:
            self.subject = text
            self.bsubject = False
        self.comment += text

    def endElement(self, name):
        if name == "note":
            self.notes.add(Note(self.author, self.date, self.time,
                    self.event, self.version, self.wipversion, self.subject, self.comment.rstrip()))
            self.clear()

if __name__ == "__main__":
    s = NoteContainer()
    s.importSAX('../../Template/import.xml')
    s.exportXML("../../Template/export.xml")
    #print s.readXML()
