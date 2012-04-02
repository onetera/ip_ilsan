import os
import re
import glob

mayaFileRegx = re.compile("_v[0-9]{2}_w[0-9]{2}.mb")
subjectMayaFileRegx = re.compile("_v[0-9]{2}_w[0-9]{2}_[\w]+.mb")
versionRegx = re.compile('_v[0-9]{2}_w[0-9]{2}')

class SceneFile(object):
    def __init__(self, level1, level2, level3, sceneFolder, subject=""):
        self.level1 = level1
        self.level2 = level2
        self.level3 = level3
        self.subject = subject
        self.sceneFolder = sceneFolder

        if len(subject):
            pass

        self.filename = filename
        self.basename = os.path.basename(self.filename)
        self.base, self.ext = os.path.splitext(self.basename)

        self.version = 1
        self.wipversion = 1
        self.mayaAllFiles = glob.glob(os.path.join(self.sceneFolder, "*"+self.ext))

        self.getInformation()
        self.devel()

    def getInformation(self):
        #if not len(self.mayaAllFiles):
            
        version = versionRegx.findall(self.base)[0]
        pieces = self.base.split(version)
        print version, pieces

        

    def getPattern(self, selVersion=None):
        version = versionRegx.findall(self.base)[0]
        pieces = self.base.split(version)
        if pieces[1] != '':
            if selVersion is None:
                return pieces[0] +'_v[0-9]{2}_w[0-9]{2}' + pieces[1]+self.ext
            else:
                return pieces[0] + ('_v%s_w[0-9]{2}'%selVersion) + pieces[1]+self.ext
        else:
            if selVersion is None:
                return pieces[0]+'_v[0-9]{2}_w[0-9]{2}'+self.ext
            else:
                return pieces[0]+('_v%s_w[0-9]{2}'%selVersion)+self.ext

    def getMayaFile(self):
        selMayaFileRegx = re.compile( self.getPattern())
        Files = filter(selMayaFileRegx.search, self.mayaAllFiles)
        if len(Files):
            return os.path.basename(Files[-1])
        else:
            return None

    def getVersion(self, filename):
        version = versionRegx.findall(filename)[0]
        return (version[2:4], version[-2:], version)

    def updateDev(self, filename):
        ver, wip, versionName = self.getVersion(filename)
        filename = filename.replace(versionName, '_v%s_w%s' % (ver, str(int(wip)+1).zfill(2)))
        return filename

    def devel(self):
        print self.getMayaFile()
        #print updateDev( self.getMayaFile() )

    def nextPublish(self):
        pass
        
            
def choice(path, mayaFiles):
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)

    currently_latest = getFile(basename, mayaFiles)
    print currently_latest
    #print updateDev(currently_latest)

def getFile(path, mayaFiles):
    version, wip, versionWipString = getVersion(path)
    selMayaFileRegx = re.compile( getPattern( path, version))
    Files = filter(selMayaFileRegx.search, mayaFiles)
    if len(Files):
        return Files[-1]
    else:
        return None

def getVersion(path):
    version = versionRegx.findall(os.path.basename(path))[0]
    return (version[2:4], version[-2:], version)

def updateDev(path):
    dir = os.path.dirname(path)
    filename = os.path.basename(path)
    ver, wip, versionName = getVersion(filename)
    filename = filename.replace(versionName, '_v%s_w%s' % (ver, str(int(wip)+1).zfill(2)))
    return os.path.join(dir, filename)


#mayaFiles = glob.glob('/show/mrgo/seq/SS_01/ACR/cloth/dev/scenes/*.mb')
#choice('/show/mrgo/seq/SS_01/ACR/cloth/dev/scenes/ACR_cloth_v01_w01_test.mb', mayaFiles)

SceneFile('/show/mrgo/seq/SS_01/ACR/cloth/dev/scenes/ACR_cloth_v01_w02_test.mb')
