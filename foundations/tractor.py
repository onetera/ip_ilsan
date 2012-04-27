# -*- coding: utf-8 -*-

"""
**tractor.py**

**Platform:**
    Linux, Mac Os X.

**Description:**
    tractor Module.

**Others:**

"""

#***********************************************************************************************
#***    External imports.
#***********************************************************************************************
import os

#***********************************************************************************************
#***    Internal imports.
#***********************************************************************************************
try:
    import foundations.nuke as nuke
    from foundations.globals.constants import Constants
except :
    print "import Error"
    import nuke 
    import globals.constants.Constants
    
    
    
    
class Tractor(object):
    def __init__(self, userName, shot, workcode, playblastFile, startFrame, endFrame, width, height, ratio , pbias ):        
        self.userName = userName
        self.shot = shot
        self.workcode = workcode
        self.playblastFile = playblastFile
        self.startFrame = startFrame
        self.endFrame = endFrame
        self.width = width
        self.height = height
        self.ratio = ratio
        self.pbias = pbias
        self.process()

    def process(self):
        dirPath = self.playblastFile.rsplit('/', 1)[0] # mov 파일이 저장될 폴더
        basename = os.path.basename(self.playblastFile)
        base = os.path.splitext(basename)[0]

        sourceFile = os.path.join(dirPath, base+".####.jpg")
        version = int(base.split('_v')[1][:2])

        local_mov_file = os.path.join("/local", basename)
        tempdir = dirPath
        nuke_filename = os.path.join(tempdir, '%s.nk' % base)
        alfred_filename = os.path.join(tempdir, '%s.alf' % base)
        movefile = '/bin/mv %s %s' % (local_mov_file, os.path.dirname(dirPath))
        deletefile = '/bin/rm %s' % (os.path.join(dirPath, '._%s' % (base+'.mov')))

        nk = nuke.open(Constants.nukeTemplaeFile)
        nk.set_source(sourceFile)
        nk.set_slate(True)
        nk.set_note("")
        nk.set_username(self.userName)
        nk.set_jobname(self.workcode) # workcode
        nk.set_status("TEMP")
        nk.set_task("") # subject
        nk.set_shotname(self.shot) # shot
        nk.set_version(version) # version
        nk.set_cgi_version(0)
        nk.set_lut(False, Constants.lutFile)
        nk.set_codec("Photo-JPEG")
        nk.set_quality("High")
        nk.set_opacity("0.7")
        nk.set_aspect_ratio(self.ratio)
        nk.set_format(str(self.width/2), str(self.height/2), "1", "Custom")
        nk.set_frame_range("%s-%s" % (self.startFrame, self.endFrame))
        nk.set_fps("24")
        # output
        nk.set_proxy_file(self.playblastFile)
        nk.set_destination(local_mov_file)
        nuke_script = nk.script()

        try:
            os.mkdir(tempdir)
        except:
            pass

        f = open(nuke_filename, 'w')
        for line in nuke_script:
            f.write(line.encode('utf-8'))
        f.close()

        tractor_script = self.submit([
            base,
            self.userName,
            '', # note field
            self.startFrame,
            self.endFrame,
            nuke_filename,
            alfred_filename,
            nuke_filename,
            movefile,
            tempdir,
            deletefile,
            self.pbias ], True  )

        f = open(alfred_filename, 'w')
        f.write(tractor_script)
        f.close()

        os.system('%s --engine=%s --user=idea %s &' % (
            Constants.tractor,
            Constants.engine_ip,
            alfred_filename)
            )

    def submit(self, arg, checked):
        (job,username,notes,first,last,scenefile,alffile,nukefile,movefile,tempdir,deletefile,pbias) = arg
        if checked:
            m_first = str(int(first) - 1)
        else:
            m_first = first

        # alfred info
        alfredInfo = """##AlfredToDo 3.0
Job -title {[mov] %(job)s (%(first)s-%(last)s)} -comment {[Artist] : %(username)s,   [Note] : } -pbias %(pbias)s -service {mov} -subtasks {
  Task -title {Frame.%(first)s-%(last)s} -cmds {
      RemoteCmd {/Applications/Nuke6.2v2/NukeX6.2v2.app/NukeX6.2v2 -F %(m_first)s-%(last)s -m 2 -t -X MOV -x %(scenefile)s} -atleast {1} -atmost {1} -samhost 1 -service {mov}
  } -cleanup {
    RemoteCmd {%(movefile)s}
    RemoteCmd {/bin/rm -rf %(tempdir)s}
  }
}""" % {
    'job': job,
    'username': username,
    'notes': notes,
    'first': first,
    'm_first': m_first,
    'last': last,
    'scenefile': scenefile,
    'alffile': alffile,
    'nukefile': nukefile,
    'movefile': movefile,
    'tempdir': tempdir,
    'pbias' : pbias
    }
        return alfredInfo

if __name__ == '__main__' :
    trac = Tractor( 'onetera' , 'test' , 'rig' , '/lustre/TEMP/_test.mov' , 0 , 100 , 720 , 480 , 10  )
